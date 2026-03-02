"""Bridge d'intégration entre ai-act-audit-tool et ai-act-iso42001-framework.

Ce module permet d'exporter les résultats d'audit AI Act vers le format
du framework ISO 42001.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AuditResult:
    """Résultat simplifié d'un audit."""
    classification: str
    exemption_applied: bool
    logging_score: float
    vulnerabilities: list
    system_name: str
    system_version: str


def export_audit_to_iso42001(
    audit_result: AuditResult,
    workflow_id: str
) -> Dict[str, Any]:
    """
    Transforme les résultats d'audit AI Act en entrées pour le framework ISO 42001.
    
    Args:
        audit_result: Résultat de l'audit AI Act
        workflow_id: Identifiant du workflow dans le framework ISO 42001
    
    Returns:
        dict compatible avec ai-act-iso42001-framework/
    """
    return {
        "workflow_id": workflow_id,
        "system_name": audit_result.system_name,
        "system_version": audit_result.system_version,
        "risk_classification": audit_result.classification,
        "ai_act_compliance": {
            "art6_3_exemption_applied": audit_result.exemption_applied,
            "logging_compliance_score": audit_result.logging_score,
            "jailbreak_vulnerabilities": len(audit_result.vulnerabilities),
            "last_audit_date": datetime.now(timezone.utc).isoformat(),
            "next_review_due": _calculate_review_date(audit_result.classification)
        },
        "iso42001_mapping": {
            "context_organization": "04-CONTEXTE-ORGANISATION/",
            "leadership": "05-LEADERSHIP/",
            "planning": "06-PLANIFICATION/",
            "support": "07-SUPPORT/",
            "operation": "08-FONCTIONNEMENT/",
            "evaluation": "09-EVALUATION-PERFORMANCES/",
            "improvement": "10-AMELIORATION/"
        }
    }


def _calculate_review_date(classification: str) -> str:
    """Calcule la date de prochaine revue selon la classification."""
    from datetime import timedelta
    
    now = datetime.now(timezone.utc)
    
    if classification == "high_risk":
        # Haut risque: revue annuelle
        review_date = now + timedelta(days=365)
    elif classification == "limited_risk":
        # Risque limité: revue bi-annuelle
        review_date = now + timedelta(days=730)
    else:
        # Risque minimal: revue tri-annuelle
        review_date = now + timedelta(days=1095)
    
    return review_date.isoformat()


def generate_iso42001_documentation(
    system_name: str,
    classification: str,
    output_dir: str = "./iso42001-docs"
) -> Dict[str, str]:
    """
    Génère les chemins de documentation pour le framework ISO 42001.
    
    Returns:
        dict avec les chemins des documents à créer
    """
    base_path = f"{output_dir}/{system_name.replace(' ', '_')}"
    
    docs = {
        "context": f"{base_path}/04-CONTEXTE-ORGANISATION/ecosysteme-ia.md",
        "policy": f"{base_path}/05-LEADERSHIP/politique-ia.md",
        "risk_register": f"{base_path}/06-PLANIFICATION/registre-risques.md",
        "training_plan": f"{base_path}/07-SUPPORT/plan-formation.md",
        "monitoring": f"{base_path}/08-FONCTIONNEMENT/procedure-surveillance.md",
        "audit_program": f"{base_path}/09-EVALUATION-PERFORMANCES/programme-audit.md",
        "improvement": f"{base_path}/10-AMELIORATION/procedure-non-conformites.md"
    }
    
    if classification == "high_risk":
        docs["technical_file"] = f"{base_path}/08-FONCTIONNEMENT/8.1-doc-technique/annexe-iv-checklist.md"
        docs["fria"] = f"{base_path}/06-PLANIFICATION/6.1.4-evaluation-impact/fria.md"
    
    return docs
