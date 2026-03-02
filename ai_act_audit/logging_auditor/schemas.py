"""Schémas Pydantic pour logs conformes Article 12 AI Act.

Ce module définit les structures de données validées par Pydantic
garantissant la conformité avec l'Article 12 du AI Act (traçabilité).
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from enum import Enum
import hashlib
import json


class LogLevel(str, Enum):
    """Niveaux de log."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AIActLogEntry(BaseModel):
    """
    Schéma conforme Article 12 AI Act.
    
    Champs obligatoires pour la traçabilité des systèmes à haut risque.
    Référence: Article 12(1) du Règlement (UE) 2024/1689
    """
    
    # ==================== IDENTIFICATION ====================
    session_id: str = Field(
        ..., 
        description="Identifiant unique de session (UUID)",
        examples=["sess_550e8400-e29b-41d4-a716-446655440000"]
    )
    
    system_id: str = Field(
        ..., 
        description="Identifiant unique du système IA",
        examples=["IA-RECRUIT-001", "IA-FRAUD-DETECT-002"]
    )
    
    system_version: str = Field(
        ..., 
        description="Version du système (semantic versioning)",
        examples=["2.3.1", "1.0.0-beta.2"]
    )
    
    # ==================== TEMPORALITÉ ====================
    timestamp_start: datetime = Field(
        ..., 
        description="Début de session (UTC, ISO 8601)",
        examples=["2026-03-02T08:14:00Z"]
    )
    
    timestamp_end: datetime = Field(
        ..., 
        description="Fin de session (UTC, ISO 8601)",
        examples=["2026-03-02T08:14:05.234Z"]
    )
    
    # ==================== DONNÉES ====================
    input_data_hash: str = Field(
        ..., 
        description="SHA-256 hash des données d'entrée",
        examples=["a3f5c8e9d2b1... (64 caractères)"]
    )
    
    input_data_preview: Optional[str] = Field(
        default=None,
        description="Aperçu tronqué des données entrée (debug)",
        max_length=500
    )
    
    output_data_hash: str = Field(
        ..., 
        description="SHA-256 hash des données de sortie",
        examples=["b7e9d1f4a8c2... (64 caractères)"]
    )
    
    output_data_preview: Optional[str] = Field(
        default=None,
        description="Aperçu tronqué des données sortie (debug)",
        max_length=500
    )
    
    reference_databases: List[str] = Field(
        ..., 
        description="Liste des bases de données référencées",
        examples=[["cv_database_v3", "job_offers_2026"]]
    )
    
    # ==================== SUPERVISION ====================
    human_oversight_id: Optional[str] = Field(
        default=None,
        description="Identifiant du superviseur humain (si applicable)",
        examples=["user_jean.dupont", "admin_marie.curie"]
    )
    
    human_oversight_timestamp: Optional[datetime] = Field(
        default=None,
        description="Date/heure de la vérification humaine"
    )
    
    human_oversight_decision: Optional[str] = Field(
        default=None,
        description="Décision du superviseur: APPROVED, REJECTED, MODIFIED",
        examples=["APPROVED", "REJECTED", "MODIFIED"]
    )
    
    # ==================== MÉTADONNÉES ====================
    user_id: str = Field(
        ..., 
        description="Identifiant de l'utilisateur ayant initié la requête",
        examples=["user_12345", "api_client_xyz"]
    )
    
    request_id: str = Field(
        ..., 
        description="Identifiant unique de la requête",
        examples=["req_abc123def456"]
    )
    
    model_version: Optional[str] = Field(
        default=None,
        description="Version spécifique du modèle ML utilisé",
        examples=["gpt-4-turbo-2024-01", "bert-base-uncased"]
    )
    
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Score de confiance du modèle (0-1)"
    )
    
    processing_duration_ms: Optional[int] = Field(
        default=None,
        ge=0,
        description="Durée de traitement en millisecondes"
    )
    
    # ==================== CONFORMITÉ ====================
    compliance_flags: List[str] = Field(
        default_factory=list,
        description="Flags de conformité détectés",
        examples=[["BIAS_ALERT", "LOW_CONFIDENCE"]]
    )
    
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Niveau de log"
    )
    
    additional_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Métadonnées additionnelles (extension)"
    )
    
    # ==================== VALIDATORS ====================
    
    @field_validator('timestamp_start', 'timestamp_end')
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        """Garantit que les timestamps sont en UTC."""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)
    
    @field_validator('input_data_hash', 'output_data_hash')
    @classmethod
    def validate_hash_format(cls, v: str) -> str:
        """Valide le format SHA-256 (64 caractères hex)."""
        if len(v) != 64:
            raise ValueError("SHA-256 hash doit faire 64 caractères")
        if not all(c in '0123456789abcdef' for c in v.lower()):
            raise ValueError("Hash doit être en hexadécimal")
        return v.lower()
    
    def model_post_init(self, __context: Any) -> None:
        """Validation post-initialisation."""
        # Vérifier cohérence timestamps
        if self.timestamp_end < self.timestamp_start:
            raise ValueError("timestamp_end doit être postérieur à timestamp_start")
        
        # Vérifier supervision si haut risque
        if self.human_oversight_decision and not self.human_oversight_id:
            raise ValueError("human_oversight_id requis si décision présente")
    
    # ==================== MÉTHODES UTILITAIRES ====================
    
    @classmethod
    def compute_hash(cls, data: Any) -> str:
        """Calcule le SHA-256 d'une donnée."""
        if isinstance(data, str):
            encoded = data.encode('utf-8')
        else:
            encoded = json.dumps(data, sort_keys=True).encode('utf-8')
        return hashlib.sha256(encoded).hexdigest()
    
    @property
    def session_duration_seconds(self) -> float:
        """Calcule la durée de session en secondes."""
        return (self.timestamp_end - self.timestamp_start).total_seconds()
    
    @property
    def is_human_verified(self) -> bool:
        """Indique si la décision a été vérifiée par un humain."""
        return self.human_oversight_id is not None
    
    def to_json(self) -> str:
        """Export JSON conforme."""
        return self.model_dump_json(indent=2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export dictionnaire."""
        return self.model_dump()


class AIActLogBatch(BaseModel):
    """Batch de logs pour export/import."""
    
    batch_id: str = Field(..., description="Identifiant du batch")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    system_id: str = Field(..., description="Système concerné")
    entries: List[AIActLogEntry] = Field(default_factory=list)
    
    @property
    def entry_count(self) -> int:
        return len(self.entries)
    
    @property
    def date_range(self) -> tuple:
        """Retourne (min_date, max_date) du batch."""
        if not self.entries:
            return (None, None)
        dates = [e.timestamp_start for e in self.entries]
        return (min(dates), max(dates))


class LogComplianceReport(BaseModel):
    """Rapport de conformité des logs."""
    
    system_id: str
    audit_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_entries: int
    compliant_entries: int
    missing_fields: Dict[str, int] = Field(default_factory=dict)
    
    @property
    def compliance_rate(self) -> float:
        if self.total_entries == 0:
            return 0.0
        return (self.compliant_entries / self.total_entries) * 100
