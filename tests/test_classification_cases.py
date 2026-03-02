"""Cas tests de validation pour la classification AI Act.

Ces tests valident l'algorithme de classification sur des scénarios réels:
1. Haut risque - Tri automatique de CV
2. Exempté Art 6(3) - Correcteur orthographique  
3. Risque minimal - Générateur de mots de passe
"""

import pytest
from ai_act_audit.risk_classifier.classifier import (
    RiskClassifier, 
    AISystem, 
    RiskLevel
)


class TestClassificationCases:
    """Suite de tests pour la classification AI Act."""
    
    @pytest.fixture
    def classifier(self):
        """Fixture pour le classificateur."""
        return RiskClassifier()
    
    def test_cv_screening_high_risk(self, classifier):
        """Test: Système de tri CV = Haut risque (Annexe III - Emploi)"""
        system = AISystem(
            name="RecrutIA Pro",
            description="Système de tri automatique de CV pour présélection candidats",
            domain="RH / Recrutement",
            uses_personal_data=True,
            automated_decision_making=True,
            human_oversight=False,
            is_employment_related=True,
            narrow_procedural_task=False,
            improves_human_work=False,
            non_material_influence=False
        )
        
        result = classifier.classify(system)
        
        assert result.risk_level == RiskLevel.HIGH_RISK
        assert result.annex_iii_applies is True
        assert result.article_6_3_exception is False
    
    def test_spell_checker_exempted(self, classifier):
        """Test: Correcteur orthographique = Exempté Art 6(3)"""
        system = AISystem(
            name="OrthoCorrect",
            description="Correcteur orthographique automatique pour documents",
            domain="Bureautique",
            uses_personal_data=False,
            automated_decision_making=False,
            human_oversight=True,
            is_education_related=False,
            is_employment_related=False,
            narrow_procedural_task=True,
            improves_human_work=True,
            non_material_influence=True
        )
        
        result = classifier.classify(system)
        
        assert result.risk_level == RiskLevel.LIMITED_RISK
        assert result.article_6_3_exception is True
    
    def test_password_generator_minimal(self, classifier):
        """Test: Générateur mots de passe = Risque minimal"""
        system = AISystem(
            name="PassGen Secure",
            description="Générateur de mots de passe aléatoires sécurisés",
            domain="Cybersécurité",
            uses_personal_data=False,
            automated_decision_making=False,
            human_oversight=False,
            is_biometric_system=False,
            is_employment_related=False,
            is_credit_scoring=False,
            is_education_related=False,
            is_law_enforcement=False,
            is_migration_asylum=False,
            is_justice_related=False,
            is_critical_infrastructure=False,
            is_healthcare=False,
            narrow_procedural_task=False,
            improves_human_work=False,
            non_material_influence=False
        )
        
        result = classifier.classify(system)
        
        assert result.risk_level == RiskLevel.MINIMAL_RISK
        assert result.annex_iii_applies is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
