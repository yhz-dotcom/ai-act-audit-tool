"""Auditeur de logs pour conformité Article 12 AI Act.

Vérifie que les logs respectent les exigences de traçabilité :
- Période d'utilisation
- Bases de données utilisées
- Données d'entrée (input)
- Identification des personnes vérifiant les résultats
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import datetime
from enum import Enum
import json
import re


class LogComplianceStatus(str, Enum):
    """Statut de conformité des logs."""
    
    COMPLIANT = "compliant"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"


class LogRequirement(str, Enum):
    """Exigences de l'Article 12."""
    
    USAGE_PERIOD = "usage_period"  # Période d'utilisation
    INPUT_DATA = "input_data"  # Données d'entrée
    OUTPUT_DATA = "output_data"  # Données de sortie
    REFERENCE_DATABASES = "reference_databases"  # Bases de données
    HUMAN_VERIFIER = "human_verifier"  # Personne vérifiant les résultats
    TIMESTAMP = "timestamp"  # Horodatage
    MODEL_VERSION = "model_version"  # Version du modèle
    CONFIDENCE_SCORE = "confidence_score"  # Score de confiance


@dataclass
class LogEntry:
    """Entrée de log attendue pour un système à haut risque."""
    
    timestamp: Optional[datetime] = None
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    model_version: Optional[str] = None
    reference_databases: list[str] = field(default_factory=list)
    human_verifier: Optional[str] = None  # ID ou nom de la personne
    confidence_score: Optional[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class LogCheckResult:
    """Résultat d'une vérification de log."""
    
    requirement: LogRequirement
    present: bool
    valid: bool
    details: str
    example_value: Optional[Any] = None


@dataclass
class LogAuditResult:
    """Résultat complet d'un audit de logs."""
    
    system_name: str
    overall_status: LogComplianceStatus
    compliance_score: float  # 0.0 à 1.0
    checks: list[LogCheckResult]
    missing_requirements: list[LogRequirement]
    recommendations: list[str]
    raw_sample: Optional[dict] = None  # Exemple de log analysé


class LoggingAuditor:
    """Auditeur de conformité des logs selon Article 12 AI Act."""
    
    # Champs requis par l'Article 12
    REQUIRED_FIELDS = [
        LogRequirement.USAGE_PERIOD,
        LogRequirement.INPUT_DATA,
        LogRequirement.REFERENCE_DATABASES,
        LogRequirement.HUMAN_VERIFIER,
    ]
    
    # Champs recommandés pour une bonne observabilité
    RECOMMENDED_FIELDS = [
        LogRequirement.OUTPUT_DATA,
        LogRequirement.TIMESTAMP,
        LogRequirement.MODEL_VERSION,
        LogRequirement.CONFIDENCE_SCORE,
    ]
    
    def __init__(self):
        self.field_extractors = self._setup_extractors()
    
    def _setup_extractors(self) -> dict:
        """Configure les extracteurs pour chaque champ."""
        return {
            LogRequirement.TIMESTAMP: self._extract_timestamp,
            LogRequirement.USAGE_PERIOD: self._extract_usage_period,
            LogRequirement.INPUT_DATA: self._extract_input,
            LogRequirement.OUTPUT_DATA: self._extract_output,
            LogRequirement.REFERENCE_DATABASES: self._extract_databases,
            LogRequirement.HUMAN_VERIFIER: self._extract_human_verifier,
            LogRequirement.MODEL_VERSION: self._extract_model_version,
            LogRequirement.CONFIDENCE_SCORE: self._extract_confidence,
        }
    
    def audit_logs(
        self,
        system_name: str,
        log_sample: dict[str, Any],
        log_schema: Optional[dict[str, str]] = None
    ) -> LogAuditResult:
        """
        Audite un échantillon de logs.
        
        Args:
            system_name: Nom du système audité
            log_sample: Exemple de log à analyser
            log_schema: Mapping optionnel champ -> clé dans le log
        
        Returns:
            Résultat de l'audit
        """
        checks = []
        missing = []
        recommendations = []
        
        # Vérifier tous les champs requis
        for req in self.REQUIRED_FIELDS:
            result = self._check_requirement(req, log_sample, log_schema)
            checks.append(result)
            if not result.present:
                missing.append(req)
                recommendations.append(f"AJOUTER: Champ '{req.value}' obligatoire (Article 12)")
            elif not result.valid:
                recommendations.append(f"CORRIGER: Champ '{req.value}' présent mais invalide")
        
        # Vérifier les champs recommandés
        for req in self.RECOMMENDED_FIELDS:
            result = self._check_requirement(req, log_sample, log_schema)
            checks.append(result)
            if not result.present:
                recommendations.append(f"RECOMMANDÉ: Ajouter le champ '{req.value}' pour meilleure observabilité")
        
        # Calculer le score
        required_checks = [c for c in checks if c.requirement in self.REQUIRED_FIELDS]
        valid_required = sum(1 for c in required_checks if c.present and c.valid)
        compliance_score = valid_required / len(self.REQUIRED_FIELDS)
        
        # Déterminer le statut
        if compliance_score == 1.0:
            status = LogComplianceStatus.COMPLIANT
        elif compliance_score >= 0.5:
            status = LogComplianceStatus.PARTIAL
        else:
            status = LogComplianceStatus.NON_COMPLIANT
        
        return LogAuditResult(
            system_name=system_name,
            overall_status=status,
            compliance_score=compliance_score,
            checks=checks,
            missing_requirements=missing,
            recommendations=recommendations,
            raw_sample=log_sample
        )
    
    def _check_requirement(
        self,
        requirement: LogRequirement,
        log_sample: dict,
        log_schema: Optional[dict] = None
    ) -> LogCheckResult:
        """Vérifie une exigence spécifique."""
        extractor = self.field_extractors.get(requirement)
        if not extractor:
            return LogCheckResult(
                requirement=requirement,
                present=False,
                valid=False,
                details="Extracteur non disponible"
            )
        
        value, present, valid, details = extractor(log_sample, log_schema)
        
        return LogCheckResult(
            requirement=requirement,
            present=present,
            valid=valid,
            details=details,
            example_value=value
        )
    
    # Extracteurs de champs
    
    def _extract_timestamp(self, log: dict, schema: Optional[dict]) -> tuple:
        """Extrait l'horodatage."""
        keys = ["timestamp", "ts", "time", "datetime", "created_at", "date"]
        if schema and "timestamp" in schema:
            keys = [schema["timestamp"]] + keys
        
        for key in keys:
            if key in log and log[key]:
                value = log[key]
                # Vérifier si c'est un timestamp valide
                valid = self._is_valid_timestamp(value)
                return value, True, valid, f"Trouvé: '{key}'"
        
        return None, False, False, "Horodatage non trouvé"
    
    def _extract_usage_period(self, log: dict, schema: Optional[dict]) -> tuple:
        """Extrait la période d'utilisation."""
        # Peut être un champ dédié ou dérivé du timestamp
        keys = ["usage_period", "session_duration", "duration", "elapsed_time"]
        if schema and "usage_period" in schema:
            keys = [schema["usage_period"]] + keys
        
        for key in keys:
            if key in log and log[key]:
                return log[key], True, True, f"Trouvé: '{key}'"
        
        # Alternative: vérifier si on peut calculer depuis start/end
        if "start_time" in log and "end_time" in log:
            return f"{log['start_time']} - {log['end_time']}", True, True, "Calculé depuis start_time/end_time"
        
        return None, False, False, "Période d'utilisation non trouvée"
    
    def _extract_input(self, log: dict, schema: Optional[dict]) -> tuple:
        """Extrait les données d'entrée."""
        keys = ["input", "prompt", "query", "request", "user_input", "input_data"]
        if schema and "input" in schema:
            keys = [schema["input"]] + keys
        
        for key in keys:
            if key in log and log[key]:
                value = log[key]
                valid = len(str(value)) > 0
                return value, True, valid, f"Trouvé: '{key}'"
        
        return None, False, False, "Données d'entrée non trouvées"
    
    def _extract_output(self, log: dict, schema: Optional[dict]) -> tuple:
        """Extrait les données de sortie."""
        keys = ["output", "response", "result", "answer", "completion", "output_data"]
        if schema and "output" in schema:
            keys = [schema["output"]] + keys
        
        for key in keys:
            if key in log and log[key]:
                return log[key], True, True, f"Trouvé: '{key}'"
        
        return None, False, False, "Données de sortie non trouvées"
    
    def _extract_databases(self, log: dict, schema: Optional[dict]) -> tuple:
        """Extrait les références aux bases de données."""
        keys = ["databases", "reference_databases", "sources", "context_sources", "retrieval_sources"]
        if schema and "databases" in schema:
            keys = [schema["databases"]] + keys
        
        for key in keys:
            if key in log and log[key]:
                value = log[key]
                valid = isinstance(value, list) or isinstance(value, str)
                return value, True, valid, f"Trouvé: '{key}'"
        
        return None, False, False, "Références aux bases de données non trouvées"
    
    def _extract_human_verifier(self, log: dict, schema: Optional[dict]) -> tuple:
        """Extrait l'identifiant du vérificateur humain."""
        keys = ["human_verifier", "verified_by", "reviewer", "approver", "human_oversight"]
        if schema and "human_verifier" in schema:
            keys = [schema["human_verifier"]] + keys
        
        for key in keys:
            if key in log and log[key]:
                return log[key], True, True, f"Trouvé: '{key}'"
        
        return None, False, False, "Vérificateur humain non identifié"
    
    def _extract_model_version(self, log: dict, schema: Optional[dict]) -> tuple:
        """Extrait la version du modèle."""
        keys = ["model_version", "model", "version", "model_id", "deployment"]
        if schema and "model_version" in schema:
            keys = [schema["model_version"]] + keys
        
        for key in keys:
            if key in log and log[key]:
                return log[key], True, True, f"Trouvé: '{key}'"
        
        return None, False, False, "Version du modèle non trouvée"
    
    def _extract_confidence(self, log: dict, schema: Optional[dict]) -> tuple:
        """Extrait le score de confiance."""
        keys = ["confidence", "confidence_score", "score", "probability"]
        if schema and "confidence" in schema:
            keys = [schema["confidence"]] + keys
        
        for key in keys:
            if key in log and log[key] is not None:
                value = log[key]
                valid = isinstance(value, (int, float)) and 0 <= value <= 1
                return value, True, valid, f"Trouvé: '{key}'"
        
        return None, False, False, "Score de confiance non trouvé"
    
    def _is_valid_timestamp(self, value: Any) -> bool:
        """Vérifie si une valeur est un timestamp valide."""
        if isinstance(value, datetime):
            return True
        
        if isinstance(value, str):
            # Essayer plusieurs formats
            formats = [
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
            ]
            for fmt in formats:
                try:
                    datetime.strptime(value.split(".")[0].replace("Z", ""), fmt)
                    return True
                except ValueError:
                    continue
        
        return False
    
    def generate_compliant_log_schema(self) -> dict:
        """Génère un schéma de log conforme Article 12."""
        return {
            "timestamp": "ISO 8601 datetime",
            "session_id": "Identifiant unique de session",
            "input_data": "Données d'entrée (prompt)",
            "output_data": "Réponse générée",
            "model_version": "Version du modèle utilisé",
            "reference_databases": ["Liste des sources/bases utilisées"],
            "human_verifier": "ID de la personne ayant vérifié",
            "verification_timestamp": "Date de vérification humaine",
            "confidence_score": "Score de confiance (0-1)",
            "metadata": {
                "user_id": "Identifiant utilisateur",
                "request_id": "ID de requête",
                "duration_ms": "Durée de traitement"
            }
        }
