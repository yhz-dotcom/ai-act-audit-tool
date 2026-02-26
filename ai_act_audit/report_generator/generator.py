"""Générateur de rapports d'audit.

Génère des rapports de conformité AI Act au format JSON et PDF.
"""

from dataclasses import dataclass, asdict
from typing import Optional, Any
from datetime import datetime
from pathlib import Path
import json

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


@dataclass
class AuditReport:
    """Rapport d'audit complet."""
    
    # Métadonnées
    report_id: str
    generated_at: datetime
    system_name: str
    system_description: str
    auditor_name: str
    
    # Résultats
    risk_classification: dict[str, Any]
    jailbreak_results: dict[str, Any]
    logging_audit: dict[str, Any]
    
    # Synthèse
    overall_compliance_score: float
    critical_issues: list[str]
    recommendations: list[str]
    next_steps: list[str]


class ReportGenerator:
    """Générateur de rapports d'audit AI Act."""
    
    def __init__(self, output_dir: str = "audit_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_json_report(self, report: AuditReport) -> str:
        """Génère un rapport au format JSON."""
        filepath = self.output_dir / f"{report.report_id}.json"
        
        data = {
            "metadata": {
                "report_id": report.report_id,
                "generated_at": report.generated_at.isoformat(),
                "system_name": report.system_name,
                "system_description": report.system_description,
                "auditor_name": report.auditor_name,
            },
            "risk_classification": report.risk_classification,
            "jailbreak_testing": report.jailbreak_results,
            "logging_compliance": report.logging_audit,
            "summary": {
                "overall_compliance_score": report.overall_compliance_score,
                "critical_issues": report.critical_issues,
                "recommendations": report.recommendations,
                "next_steps": report.next_steps,
            }
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def generate_pdf_report(self, report: AuditReport) -> str:
        """Génère un rapport au format PDF."""
        filepath = self.output_dir / f"{report.report_id}.pdf"
        
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1a1a2e')
        )
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#16213e')
        )
        heading3_style = ParagraphStyle(
            'CustomHeading3',
            parent=styles['Heading3'],
            fontSize=13,
            spaceAfter=10,
            textColor=colors.HexColor('#0f3460')
        )
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=10
        )
        
        story = []
        
        # Page de titre
        story.append(Paragraph("Rapport d'Audit AI Act", title_style))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"<b>Système:</b> {report.system_name}", body_style))
        story.append(Paragraph(f"<b>Description:</b> {report.system_description}", body_style))
        story.append(Paragraph(f"<b>Auditeur:</b> {report.auditor_name}", body_style))
        story.append(Paragraph(f"<b>Date:</b> {report.generated_at.strftime('%Y-%m-%d %H:%M')}", body_style))
        story.append(Paragraph(f"<b>ID Rapport:</b> {report.report_id}", body_style))
        story.append(Spacer(1, 0.5*inch))
        
        # Score global
        score_color = self._score_color(report.overall_compliance_score)
        story.append(Paragraph(f"<b>Score de conformité global:</b> {report.overall_compliance_score:.1%}", 
                              ParagraphStyle('Score', parent=body_style, textColor=score_color, fontSize=14)))
        story.append(Spacer(1, 0.3*inch))
        
        # Section 1: Classification des risques
        story.append(Paragraph("1. Classification des Risques", heading2_style))
        story.append(Spacer(1, 0.1*inch))
        
        risk_data = report.risk_classification
        if risk_data:
            story.append(Paragraph(f"<b>Niveau de risque:</b> {risk_data.get('risk_level', 'N/A').upper()}", body_style))
            story.append(Paragraph(f"<b>Raisonnement:</b> {risk_data.get('reasoning', 'N/A')}", body_style))
            story.append(Paragraph(f"<b>Annexe III applicable:</b> {'Oui' if risk_data.get('annex_iii_applies') else 'Non'}", body_style))
            
            if risk_data.get('compliance_requirements'):
                story.append(Paragraph("<b>Exigences de conformité:</b>", body_style))
                for req in risk_data['compliance_requirements'][:5]:  # Limiter à 5
                    story.append(Paragraph(f"  • {req}", body_style))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Section 2: Tests de jailbreak
        story.append(Paragraph("2. Tests de Sécurité (Jailbreak)", heading2_style))
        story.append(Spacer(1, 0.1*inch))
        
        jailbreak_data = report.jailbreak_results
        if jailbreak_data:
            summary = jailbreak_data.get('summary', {})
            story.append(Paragraph(f"<b>Tests passés:</b> {summary.get('passed', 0)}/{summary.get('total_tests', 0)} " +
                                  f"({summary.get('success_rate', 'N/A')})", body_style))
            
            # Tableau des vulnérabilités
            vulnerabilities = jailbreak_data.get('vulnerabilities', [])
            if vulnerabilities:
                story.append(Paragraph("<b>Vulnérabilités détectées:</b>", body_style))
                
                table_data = [['Test', 'Catégorie', 'Sévérité']]
                for vuln in vulnerabilities[:10]:  # Limiter à 10
                    table_data.append([
                        vuln.get('test', 'N/A')[:30],
                        vuln.get('category', 'N/A'),
                        vuln.get('severity', 'N/A').upper()
                    ])
                
                table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16213e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                ]))
                story.append(table)
        
        story.append(PageBreak())
        
        # Section 3: Conformité des logs
        story.append(Paragraph("3. Conformité des Logs (Article 12)", heading2_style))
        story.append(Spacer(1, 0.1*inch))
        
        logging_data = report.logging_audit
        if logging_data:
            status = logging_data.get('overall_status', 'N/A')
            status_color = colors.green if status == 'compliant' else colors.orange if status == 'partial' else colors.red
            story.append(Paragraph(f"<b>Statut:</b> {status.upper()}", 
                                  ParagraphStyle('Status', parent=body_style, textColor=status_color)))
            story.append(Paragraph(f"<b>Score:</b> {logging_data.get('compliance_score', 0):.1%}", body_style))
            
            missing = logging_data.get('missing_requirements', [])
            if missing:
                story.append(Paragraph("<b>Champs obligatoires manquants:</b>", body_style))
                for req in missing:
                    story.append(Paragraph(f"  • {req}", body_style))
            
            recommendations = logging_data.get('recommendations', [])
            if recommendations:
                story.append(Paragraph("<b>Recommandations:</b>", body_style))
                for rec in recommendations[:5]:
                    story.append(Paragraph(f"  • {rec}", body_style))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Section 4: Synthèse et recommandations
        story.append(Paragraph("4. Synthèse et Recommandations", heading2_style))
        story.append(Spacer(1, 0.1*inch))
        
        if report.critical_issues:
            story.append(Paragraph("<b>Problèmes critiques:</b>", heading3_style))
            for issue in report.critical_issues:
                story.append(Paragraph(f"  ⚠ {issue}", body_style))
            story.append(Spacer(1, 0.1*inch))
        
        if report.recommendations:
            story.append(Paragraph("<b>Recommandations prioritaires:</b>", heading3_style))
            for rec in report.recommendations:
                story.append(Paragraph(f"  • {rec}", body_style))
            story.append(Spacer(1, 0.1*inch))
        
        if report.next_steps:
            story.append(Paragraph("<b>Prochaines étapes:</b>", heading3_style))
            for step in report.next_steps:
                story.append(Paragraph(f"  → {step}", body_style))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            f"<i>Ce rapport a été généré automatiquement par AI Act Audit Tool. "
            f"Il ne constitue pas un avis juridique.</i>",
            ParagraphStyle('Footer', parent=body_style, fontSize=8, textColor=colors.grey)
        ))
        
        doc.build(story)
        return str(filepath)
    
    def _score_color(self, score: float) -> colors.Color:
        """Retourne la couleur associée au score."""
        if score >= 0.8:
            return colors.green
        elif score >= 0.5:
            return colors.orange
        else:
            return colors.red
    
    def generate_both(self, report: AuditReport) -> tuple[str, str]:
        """Génère les deux formats de rapport."""
        json_path = self.generate_json_report(report)
        pdf_path = self.generate_pdf_report(report)
        return json_path, pdf_path
