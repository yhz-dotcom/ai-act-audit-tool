"""Interface en ligne de commande pour AI Act Audit Tool.

Usage:
    ai-act-audit classify --name "Mon Chatbot" --description "..."
    ai-act-audit jailbreak --endpoint https://api.example.com/v1/chat
    ai-act-audit logs --sample logs.json
    ai-act-audit full --config audit_config.yaml
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from ai_act_audit.risk_classifier import RiskClassifier, AISystem, RiskLevel
from ai_act_audit.jailbreak_tester import JailbreakTester, JailbreakCategory
from ai_act_audit.logging_auditor import LoggingAuditor, LogComplianceStatus
from ai_act_audit.report_generator import ReportGenerator, AuditReport


app = typer.Typer(
    name="ai-act-audit",
    help="Outil d'audit de conformité AI Act",
    no_args_is_help=True,
)
console = Console()


@app.command()
def classify(
    name: str = typer.Option(..., "--name", "-n", help="Nom du système"),
    description: str = typer.Option(..., "--description", "-d", help="Description de l'usage"),
    domain: str = typer.Option("general", "--domain", help="Domaine d'application"),
    employment: bool = typer.Option(False, "--employment", help="Lié à l'emploi/recrutement"),
    credit: bool = typer.Option(False, "--credit", help="Scoring de crédit"),
    education: bool = typer.Option(False, "--education", help="Éducation/formation"),
    healthcare: bool = typer.Option(False, "--healthcare", help="Santé"),
    law_enforcement: bool = typer.Option(False, "--law-enforcement", help="Application de la loi"),
    justice: bool = typer.Option(False, "--justice", help="Administration de la justice"),
    biometric: bool = typer.Option(False, "--biometric", help="Système biométrique"),
    critical: bool = typer.Option(False, "--critical", help="Infrastructure critique"),
    migration: bool = typer.Option(False, "--migration", help="Migration/asile"),
):
    """Classifie un système IA selon l'AI Act."""
    
    system = AISystem(
        name=name,
        description=description,
        domain=domain,
        is_employment_related=employment,
        is_credit_scoring=credit,
        is_education_related=education,
        is_healthcare=healthcare,
        is_law_enforcement=law_enforcement,
        is_justice_related=justice,
        is_biometric_system=biometric,
        is_critical_infrastructure=critical,
        is_migration_asylum=migration,
    )
    
    classifier = RiskClassifier()
    result = classifier.classify(system)
    
    # Affichage
    risk_colors = {
        RiskLevel.PROHIBITED: "red",
        RiskLevel.HIGH_RISK: "orange3",
        RiskLevel.LIMITED_RISK: "yellow",
        RiskLevel.MINIMAL_RISK: "green",
    }
    
    console.print(Panel(
        f"[bold]{result.risk_level.value.upper()}[/bold]\n\n"
        f"{result.reasoning}\n\n"
        f"Annexe III: {'✅ Oui' if result.annex_iii_applies else '❌ Non'}",
        title=f"Classification: {system.name}",
        border_style=risk_colors.get(result.risk_level, "white"),
        box=box.ROUNDED,
    ))
    
    if result.compliance_requirements:
        console.print("\n[bold]Exigences de conformité:[/bold]")
        for req in result.compliance_requirements:
            console.print(f"  • {req}")


@app.command()
def jailbreak(
    endpoint: Optional[str] = typer.Option(None, "--endpoint", "-e", help="URL de l'API à tester"),
    categories: Optional[str] = typer.Option(None, "--categories", "-c", 
                                              help="Catégories à tester (comma-separated)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Fichier de sortie JSON"),
):
    """Teste la robustesse face aux jailbreaks."""
    
    if not endpoint:
        console.print("[yellow]⚠ Mode démo: exécution sans endpoint réel[/yellow]")
        console.print("Pour tester un vrai système, utilisez --endpoint https://api.example.com")
        
        # Mode démo avec réponses simulées
        def mock_query(prompt: str) -> str:
            # Simuler un système sécurisé
            return "Je ne peux pas répondre à cette demande."
        
        query_fn = mock_query
    else:
        console.print(f"[red]⚠ Tests sur endpoint réel non implémenté dans cette version[/red]")
        console.print("Vous devez implémenter la fonction d'appel API.")
        raise typer.Exit(1)
    
    # Catégories
    cat_list = None
    if categories:
        cat_list = [JailbreakCategory(c.strip()) for c in categories.split(",")]
    
    # Exécution
    tester = JailbreakTester()
    console.print("\n[bold]Exécution des tests de jailbreak...[/bold]")
    
    with console.status("[bold green]Test en cours..."):
        results = tester.test_system(query_fn, categories=cat_list)
    
    # Affichage des résultats
    report = tester.generate_report(results)
    
    summary = report["summary"]
    console.print(f"\n[bold]Résultats:[/bold]")
    console.print(f"  Tests totaux: {summary['total_tests']}")
    console.print(f"  Passés: [green]{summary['passed']}[/green]")
    console.print(f"  Échoués: [red]{summary['failed']}[/red]")
    console.print(f"  Taux de réussite: {summary['success_rate']}")
    
    # Vulnérabilités
    if report["vulnerabilities"]:
        console.print("\n[bold red]Vulnérabilités détectées:[/bold red]")
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("Test")
        table.add_column("Catégorie")
        table.add_column("Sévérité")
        
        for vuln in report["vulnerabilities"]:
            severity_color = {
                "critical": "red",
                "high": "orange3",
                "medium": "yellow",
                "low": "blue",
            }.get(vuln["severity"], "white")
            
            table.add_row(
                vuln["test"],
                vuln["category"],
                f"[{severity_color}]{vuln['severity'].upper()}[/{severity_color}]"
            )
        
        console.print(table)
    else:
        console.print("\n[green]✅ Aucune vulnérabilité détectée![/green]")
    
    # Export
    if output:
        with open(output, "w") as f:
            json.dump(report, f, indent=2)
        console.print(f"\n[green]Rapport exporté: {output}[/green]")


@app.command()
def logs(
    sample: str = typer.Option(..., "--sample", "-s", help="Chemin vers l'échantillon de log (JSON)"),
    system_name: str = typer.Option("Unknown", "--system", "-n", help="Nom du système"),
    schema: Optional[str] = typer.Option(None, "--schema", help="Schéma de mapping (JSON)"),
):
    """Audite la conformité des logs (Article 12)."""
    
    # Charger l'échantillon
    try:
        with open(sample, "r") as f:
            log_sample = json.load(f)
    except FileNotFoundError:
        console.print(f"[red]❌ Fichier non trouvé: {sample}[/red]")
        raise typer.Exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]❌ JSON invalide: {sample}[/red]")
        raise typer.Exit(1)
    
    # Charger le schéma si fourni
    log_schema = None
    if schema:
        with open(schema, "r") as f:
            log_schema = json.load(f)
    
    # Audit
    auditor = LoggingAuditor()
    result = auditor.audit_logs(system_name, log_sample, log_schema)
    
    # Affichage
    status_colors = {
        LogComplianceStatus.COMPLIANT: "green",
        LogComplianceStatus.PARTIAL: "yellow",
        LogComplianceStatus.NON_COMPLIANT: "red",
    }
    
    console.print(Panel(
        f"[bold]Statut:[/bold] [{status_colors.get(result.overall_status, 'white')}]{result.overall_status.value.upper()}[/{status_colors.get(result.overall_status, 'white')}]",
        title=f"Audit Logs: {system_name}",
        box=box.ROUNDED,
    ))
    
    console.print(f"\n[bold]Score de conformité:[/bold] {result.compliance_score:.1%}")
    
    # Détails des vérifications
    console.print("\n[bold]Vérifications:[/bold]")
    table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
    table.add_column("Exigence")
    table.add_column("Présent")
    table.add_column("Valide")
    table.add_column("Détails")
    
    for check in result.checks:
        present = "✅" if check.present else "❌"
        valid = "✅" if check.valid else "❌"
        table.add_row(
            check.requirement.value,
            present,
            valid,
            check.details[:50] + "..." if len(check.details) > 50 else check.details
        )
    
    console.print(table)
    
    # Recommandations
    if result.recommendations:
        console.print("\n[bold yellow]Recommandations:[/bold yellow]")
        for rec in result.recommendations[:10]:  # Limiter à 10
            console.print(f"  • {rec}")


@app.command()
def schema():
    """Affiche le schéma de log conforme Article 12."""
    
    auditor = LoggingAuditor()
    schema = auditor.generate_compliant_log_schema()
    
    console.print(Panel(
        json.dumps(schema, indent=2, ensure_ascii=False),
        title="Schéma de log conforme Article 12",
        box=box.ROUNDED,
    ))


@app.callback()
def main(
    version: Optional[bool] = typer.Option(None, "--version", "-v", help="Affiche la version"),
):
    """AI Act Audit Tool - Outil d'audit de conformité AI Act."""
    if version:
        from ai_act_audit import __version__
        console.print(f"AI Act Audit Tool v{__version__}")
        raise typer.Exit()


if __name__ == "__main__":
    app()
