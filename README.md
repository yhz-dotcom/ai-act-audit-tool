# AI Act Audit Tool

Outil d'audit de conformité AI Act pour systèmes d'intelligence artificielle.

## Fonctionnalités

- **Classification des risques** — Détermine si un système IA est à haut risque selon l'AI Act
- **Tests de jailbreak** — Vérifie la robustesse face aux injections de prompts
- **Audit de logs** — Contrôle la conformité Article 12 (traçabilité)
- **Génération de rapports** — Rapports PDF/JSON pour les auditeurs

## Installation rapide

```bash
pip install -e ".[dev]"
```

## Usage rapide

```bash
# Classifier un système
ai-act-audit classify --name "MonChatbot" --description "Chatbot support client"

# Tester la robustesse
ai-act-audit jailbreak

# Auditer des logs
ai-act-audit logs --sample examples/compliant_log_sample.json --system "MonChatbot"

# Voir le schéma conforme
ai-act-audit schema
```

## Structure du projet

```
ai-act-audit/
├── ai_act_audit/
│   ├── risk_classifier/      # Classification des risques AI Act
│   ├── jailbreak_tester/     # Tests de sécurité (prompt injection)
│   ├── logging_auditor/      # Vérification des logs (Article 12)
│   ├── observability_checker/ # Contrôle de l'observabilité
│   └── report_generator/     # Génération de rapports
├── tests/                    # Tests unitaires
├── examples/                 # Exemples de logs
├── docs/                     # Documentation
└── README.md
```

## Modules

### Risk Classifier
- 4 niveaux de risque: Interdit, Haut risque, Risque limité, Minimal
- Détection Annexe III (haut risque)
- Exceptions Article 6(3)
- Mapping des exigences de conformité

### Jailbreak Tester
- 8 vecteurs d'attaque testés
- Injection de prompts, roleplay, encodage
- Classification par sévérité
- Rapport de vulnérabilités

### Logging Auditor (Article 12)
- Vérification des champs obligatoires
- Période d'utilisation, input/output, bases de données
- Identification du vérificateur humain
- Score de conformité et recommandations

### Report Generator
- Rapports PDF professionnels
- Export JSON pour intégration
- Synthèse visuelle des résultats

## Documentation

Voir [docs/USAGE.md](docs/USAGE.md) pour le guide complet.

## Licence

MIT
