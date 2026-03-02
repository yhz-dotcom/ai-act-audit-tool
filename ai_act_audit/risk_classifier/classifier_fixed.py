"""Classificateur de risque AI Act - VERSION CORRIGÉE.

CORRECTIONS:
- Article 6(3): Vérification correcte du profilage (AND logique)
- Ajout is_safety_component pour Annexe I
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Niveaux de risque définis par l'AI Act."""
    
    PROHIBITED = "prohibited"
    HIGH_RISK = "high_risk"
    LIMITED_RISK = "limited_risk"
    MINIMAL_RISK = "minimal_risk"


class AISystem(BaseModel):
    """Représentation d'un système d'IA à auditer."""
    
    name: str = Field(..., description="Nom du système")
    description: str = Field(..., description="Description de l'usage prévu")
    domain: str = Field(..., description="Domaine d'application")
    uses_personal_data: bool = Field(default=False)
    automated_decision_making: bool = Field(default=False)
    human_oversight: bool = Field(default=False)
    
    # Annexe I - Composants sécurité
    is_safety_component: bool = Field(
        default=False, 
        description="Composant sécurité produit réglementé (Annexe I)"
    )
    
    # Annexe III
    is_biometric_system: bool = Field(default=False)
    is_employment_related: bool = Field(default=False)
    is_credit_scoring: bool = Field(default=False)
    is_education_related: bool = Field(default=False)
    is_law_enforcement: bool = Field(default=False)
    is_migration_asylum: bool = Field(default=False)
    is_justice_related: bool = Field(default=False)
    is_critical_infrastructure: bool = Field(default=False)
    is_healthcare: bool = Field(default=False)
    
    # Article 6(3) - Conditions cumulatives
    narrow_procedural_task: bool = Field(default=False)
    improves_human_work: bool = Field(default=False)
    non_material_influence: bool = Field(default=False)


class RiskClassificationResult(BaseModel):
    """Résultat de la classification de risque."""
    
    system: AISystem
    risk_level: RiskLevel
    reasoning: str = Field(..., description="Explication de la classification")
    annex_iii_applies: bool = Field(default=False)
    article_6_3_exception: bool = Field(default=False)
    compliance_requirements: list[str] = Field(default_factory=list)


class RiskClassifier:
    """Classificateur de risque selon l'AI Act - VERSION CORRIGÉE."""
    
    PROHIBITED_PATTERNS = [
        "manipulation comportementale",
        "exploitation vulnérabilité",
        "scoring social",
        "biométrie à distance en temps réel dans espaces publics",
        "émotions écoles/bureaux",
    ]
    
    def classify(self, system: AISystem) -> RiskClassificationResult:
        """Classifie un système IA selon l'AI Act."""
        
        # 1. Vérifier si c'est interdit
        if self._is_prohibited(system):
            return RiskClassificationResult(
                system=system,
                risk_level=RiskLevel.PROHIBITED,
                reasoning="Système utilisant des pratiques interdites par l'Article 5",
                annex_iii_applies=False,
                compliance_requirements=["ARRÊTER IMMÉDIATEMENT"]
            )
        
        # 2. Vérifier Annexe I (composants sécurité)
        if system.is_safety_component:
            return RiskClassificationResult(
                system=system,
                risk_level=RiskLevel.HIGH_RISK,
                reasoning="Composant de sécurité d'un produit réglementé (Annexe I)",
                annex_iii_applies=False,
                compliance_requirements=self._get_high_risk_requirements()
            )
        
        # 3. Vérifier Annexe III
        if self._is_high_risk(system):
            # Vérifier exemption Article 6(3)
            if self._has_article_6_3_exception(system):
                return RiskClassificationResult(
                    system=system,
                    risk_level=RiskLevel.LIMITED_RISK,
                    reasoning="Système Annexe III mais exempté par Article 6(3)",
                    annex_iii_applies=True,
                    article_6_3_exception=True,
                    compliance_requirements=["Transparence (Article 50)"]
                )
            
            return RiskClassificationResult(
                system=system,
                risk_level=RiskLevel.HIGH_RISK,
                reasoning="Système à haut risque selon Annexe III",
                annex_iii_applies=True,
                compliance_requirements=self._get_high_risk_requirements()
            )
        
        # 4. Vérifier risque limité
        if self._is_limited_risk(system):
            return RiskClassificationResult(
                system=system,
                risk_level=RiskLevel.LIMITED_RISK,
                reasoning="Système à risque limité (Article 50)",
                compliance_requirements=["Obligations de transparence"]
            )
        
        # 5. Risque minimal
        return RiskClassificationResult(
            system=system,
            risk_level=RiskLevel.MINIMAL_RISK,
            reasoning="Système à risque minimal",
            compliance_requirements=["Bonnes pratiques recommandées"]
        )
    
    def _is_prohibited(self, system: AISystem) -> bool:
        """Vérifie si le système est interdit (Article 5)."""
        prohibited_keywords = [
            "manipulation subliminale",
            "exploitation handicap",
            "scoring social",
            "biométrie temps réel public"
        ]
        desc_lower = system.description.lower()
        return any(kw in desc_lower for kw in prohibited_keywords)
    
    def _is_high_risk(self, system: AISystem) -> bool:
        """Vérifie si le système est à haut risque (Annexe III)."""
        high_risk_indicators = [
            system.is_biometric_system,
            system.is_employment_related,
            system.is_credit_scoring,
            system.is_education_related,
            system.is_law_enforcement,
            system.is_migration_asylum,
            system.is_justice_related,
            system.is_critical_infrastructure,
            system.is_healthcare,
        ]
        return any(high_risk_indicators)
    
    def _has_article_6_3_exception(self, system: AISystem) -> bool:
        """
        Vérifie si le système bénéficie d'une exception Article 6(3).
        
        CORRECTION: 
        - Vérifie d'abord le profilage (pas d'exemption si profilage)
        - Utilise AND logique pour les conditions (pas OR)
        """
        # CRITIQUE: Si profilage détecté → Pas d'exemption possible
        if system.uses_personal_data and system.automated_decision_making:
            return False  # Profilage = maintien haut risque
        
        # Toutes les conditions doivent être cumulées (ET logique)
        return (
            system.narrow_procedural_task and
            system.improves_human_work and
            system.non_material_influence and
            system.human_oversight
        )
    
    def _is_limited_risk(self, system: AISystem) -> bool:
        """Vérifie si le système est à risque limité (Article 50)."""
        limited_risk_keywords = ["chatbot", "bot conversationnel", "deepfake"]
        desc_lower = system.description.lower()
        return any(kw in desc_lower for kw in limited_risk_keywords)
    
    def _get_high_risk_requirements(self) -> list[str]:
        """Retourne la liste des exigences pour systèmes haut risque."""
        return [
            "Système de management qualité (Article 17)",
            "Gestion des risques (Article 9)",
            "Gouvernance des données (Article 10)",
            "Documentation technique (Article 11)",
            "Logging et traçabilité (Article 12)",
            "Transparence (Article 13)",
            "Supervision humaine (Article 14)",
            "Exactitude, robustesse, cybersécurité (Article 15)",
            "Évaluation de conformité (Article 43)",
            "Déclaration UE et marquage CE (Articles 47-48)",
            "Enregistrement dans la base UE (Article 49)",
            "Surveillance post-marché (Article 72)"
        ]
