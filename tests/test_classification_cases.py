"""Cas tests de validation - Classification AI Act.

Ces tests valident l'algorithme de classification sur des scénarios réels:
1. Haut risque - Tri automatique de CV
2. Exempté Art 6(3) - Correcteur orthographique  
3. Risque minimal - Générateur de mots de passe
"""

import pytest
from ai_act_audit.risk_classifier.classifier import (
    RiskClassifier, AISystem, RiskLevel
)


def test_cv_screening_high_risk():
    """Test: Système de tri CV = Haut risque (Annexe III - Emploi)"""
    
    classifier = RiskClassifier()
    
    system = AISystem(
        name="RecrutIA Pro",
        description="Système de tri automatique de CV pour présélection candidats",
        domain="RH / Recrutement",
        uses_personal_data=True,
        automated_decision_making=True,
        human_oversight=False,
        
        # Annexe III
        is_employment_related=True,
        
        # Article 6(3) - Toutes FALSE
        narrow_procedural_task=False,
        improves_human_work=False,
        non_material_influence=False
    )
    
    result = classifier.classify(system)
    
    assert result.risk_level == RiskLevel.HIGH_RISK
    assert result.annex_iii_applies is True
    assert result.article_6_3_exception is False
    
    # Vérifier exigences conformité
    required_compliance = [
        "Système de management qualité",
        "Gestion des risques",
        "Documentation technique",
        "Supervision humaine"
    ]
    
    for req in required_compliance:
        assert any(req in c for c in result.compliance_requirements)


def test_spell_checker_exempted():
    """Test: Correcteur orthographique = Exempté Art 6(3)"""
    
    classifier = RiskClassifier()
    
    system = AISystem(
        name="OrthoCorrect",
        description="Correcteur orthographique automatique pour documents",
        domain="Bureautique",
        uses_personal_data=False,
        automated_decision_making=False,
        human_oversight=True,
        
        # Annexe III
        is_employment_related=False,
        is_education_related=False,
        
        # Article 6(3) - Toutes TRUE
        narrow_procedural_task=True,
        improves_human_work=True,
        non_material_influence=True
    )
    
    result = classifier.classify(system)
    
    assert result.risk_level == RiskLevel.LIMITED_RISK
    assert result.article_6_3_exception is True
    assert any("Transparence" in c for c in result.compliance_requirements)


def test_password_generator_minimal():
    """Test: Générateur mots de passe = Risque minimal"""
    
    classifier = RiskClassifier()
    
    system = AISystem(
        name="PassGen Secure",
        description="Générateur de mots de passe aléatoires sécurisés",
        domain="Cybersécurité",
        uses_personal_data=False,
        automated_decision_making=False,
        human_oversight=False,
        
        # Aucun indicateur Annexe III
        is_biometric_system=False,
        is_employment_related=False,
        is_credit_scoring=False,
        is_education_related=False,
        is_law_enforcement=False,
        is_migration_asylum=False,
        is_justice_related=False,
        is_critical_infrastructure=False,
        is_healthcare=False,
        
        # Pas d'exemption nécessaire
        narrow_procedural_task=False,
        improves_human_work=False,
        non_material_influence=False
    )
    
    result = classifier.classify(system)
    
    assert result.risk_level == RiskLevel.MINIMAL_RISK
    assert result.annex_iii_applies is False
    assert len(result.compliance_requirements) <= 1


def test_profiling_stays_high_risk():
    """Test: Profilage = Maintien haut risque même si Art 6(3) conditions OK"""
    
    classifier = RiskClassifier()
    
    system = AISystem(
        name="Scoring RH",
        description="Évaluation comportementale candidats",
        domain="RH",
        uses_personal_data=True,  # Profilage
        automated_decision_making=True,
        
        # Conditions Art 6(3) remplies...
        narrow_procedural_task=True,
        improves_human_work=True,
        non_material_influence=True,
        human_oversight=True,
        
        # ...mais profilage = maintien haut risque
        is_employment_related=True
    )
    
    result = classifier.classify(system)
    
    # Même avec conditions Art 6(3), le profilage maintient haut risque
    assert result.risk_level == RiskLevel.HIGH_RISK
    assert result.article_6_3_exception is False
