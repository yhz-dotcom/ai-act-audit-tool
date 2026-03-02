"""Classificateur de risque AI Act.

Ce module détermine le niveau de risque d'un système IA selon l'AI Act européen.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Niveaux de risque définis par l'AI Act."""
    
    PROHIBITED = "prohibited"  # Interdit
    HIGH_RISK = "high_risk"    # Haut risque (Annexe III)
    LIMITED_RISK = "limited_risk"  # Risque limité (transparence)
    MINIMAL_RISK = "minimal_risk"  # Risque minimal


class AISystem(BaseModel):
    """Représentation d'un système d'IA à auditer."""
    
    name: str = Field(..., description="Nom du système")
    description: str = Field(..., description="Description de l'usage prévu")
    domain: str = Field(..., description="Domaine d'application")
    uses_personal_data: bool = Field(default=False, description="Utilise des données personnelles")
    automated_decision_making: bool = Field(default=False, description="Prise de décision automatisée")
    human_oversight: bool = Field(default=False, description="Supervision humaine en place")
    
    # Champs spécifiques AI Act
    is_biometric_system: bool = Field(default=False, description="Système biométrique")
    is_employment_related: bool = Field(default=False, description="Lié à l'emploi/recrutement")
    is_credit_scoring: bool = Field(default=False, description="Scoring de crédit")
    is_education_related: bool = Field(default=False, description="Éducation/formation")
    is_law_enforcement: bool = Field(default=False, description="Application de la loi")
    is_migration_asylum: bool = Field(default=False, description="Migration/asile")
    is_justice_related: bool = Field(default=False, description="Administration de la justice")
    is_critical_infrastructure: bool = Field(default=False, description="Infrastructure critique")
    is_healthcare: bool = Field(default=False, description="Santé")
    
    # Exceptions Article 6(3)
    narrow_procedural_task: bool = Field(default=False, description="Tâche procédurale étroite")
    improves_human_work: bool = Field(default=False, description="Améliore le travail humain")
    non_material_influence: bool = Field(default=False, description="Influence non substantielle")


class RiskClassificationResult(BaseModel):
    """Résultat de la classification de risque."""
    
    system: AISystem
    risk_level: RiskLevel
    reasoning: str = Field(..., description="Explication de la classification")
    annex_iii_applies: bool = Field(default=False, description="Annexe III applicable")
    article_6_3_exception: bool = Field(default=False, description="Exception Article 6(3)")
    compliance_requirements: list[str] = Field(default_factory=list, description="Exigences de conformité")


class RiskClassifier:
    """Classificateur de risque selon l'AI Act."""
    
    # Pratiques interdites (Article 5)
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
                reasoning="Système utilisant des pratiques interdites par l'Article 5 de l'AI Act",
                annex_iii_applies=False,
                compliance_requirements=["ARRÊTER IMMÉDIATEMENT — Système interdit"]
            )
        
        # 2. Vérifier si c'est haut risque (Annexe III)
        if self._is_high_risk(system):
            # Vérifier les exceptions Article 6(3)
            if self._has_article_6_3_exception(system):
                return RiskClassificationResult(
                    system=system,
                    risk_level=RiskLevel.LIMITED_RISK,
                    reasoning="Système Annexe III mais exempté par Article 6(3)",
                    annex_iii_applies=True,
                    article_6_3_exception=True,
                    compliance_requirements=[
                        "Transparence (Article 50)",
                        "Documentation de l'exemption"
                    ]
                )
            
            return RiskClassificationResult(
                system=system,
                risk_level=RiskLevel.HIGH_RISK,
                reasoning="Système à haut risque selon Annexe III de l'AI Act",
                annex_iii_applies=True,
                compliance_requirements=[
                    "Système de management qualité (Article 17)",
                    "Gestion des risques (Article 9)",
                    "Gouvernance des données (Article 10)",
                    "Documentation technique (Article 11)",
                    "Logging et traçabilité (Article 12)",
                    "Transparence et info aux utilisateurs (Article 13)",
                    "Supervision humaine (Article 14)",
                    "Exactitude, robustesse, cybersécurité (Article 15)",
                    "Évaluation de conformité (Article 43)",
                    "Déclaration UE et marquage CE (Articles 47-48)",
                    "Enregistrement dans la base UE (Article 49)",
                    "Surveillance post-marché (Article 72)"
                ]
            )
        
        # 3. Vérifier si c'est risque limité (chatbots, deepfakes, etc.)
        if self._is_limited_risk(system):
            return RiskClassificationResult(
                system=system,
                risk_level=RiskLevel.LIMITED_RISK,
                reasoning="Système à risque limité nécessitant transparence (Article 50)",
                compliance_requirements=[
                    "Informer l'utilisateur qu'il interagit avec une IA",
                    "Marquer le contenu synthétique",
                    "Divulguer les deepfakes"
                ]
            )
        
        # 4. Sinon, risque minimal
        return RiskClassificationResult(
            system=system,
            risk_level=RiskLevel.MINIMAL_RISK,
            reasoning="Système à risque minimal — pas d'obligation spécifique",
            compliance_requirements=["Bonnes pratiques recommandées"]
        )
    
    def _is_prohibited(self, system: AISystem) -> bool:
        """Vérifie si le système est interdit (Article 5)."""
        # Simplified check — in practice would analyze description
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
        
        ATTENTION: Les 4 conditions doivent être cumulées (ET logique).
        Si profilage détecté -> Pas d'exemption possible.
        
        Référence: AI Act Article 6(3)
        """
        # CRITIQUE: Si profilage détecté -> Maintien haut risque
        # Profilage = données personnelles + décision automatisée
        if system.uses_personal_data and system.automated_decision_making:
            return False
        
        # Les 4 conditions doivent TOUTES être remplies (ET logique)
        conditions = [
            system.narrow_procedural_task,           # C1: Tâche procédurale étroite
            system.improves_human_work,               # C2: Améliore travail humain
            system.non_material_influence,            # C3: Influence non substantielle
            system.human_oversight                    # C4: Supervision humaine
        ]
        
        return all(conditions)
    
    def _is_limited_risk(self, system: AISystem) -> bool:
        """Vérifie si le système est à risque limité (Article 50)."""
        limited_risk_keywords = ["chatbot", "bot conversationnel", "deepfake", "contenu synthétique"]
        desc_lower = system.description.lower()
        return any(kw in desc_lower for kw in limited_risk_keywords)
