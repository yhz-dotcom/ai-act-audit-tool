# AI Act Audit Tool

Outil d'audit de conformité AI Act pour systèmes d'intelligence artificielle.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 🎯 Fonctionnalités

- **🎲 Classification des risques** — Détermine si un système IA est à haut risque selon l'AI Act (Article 6, Annexes I & III)
- **🔒 Tests de jailbreak** — Vérifie la robustesse face aux injections de prompts (8 vecteurs d'attaque)
- **📝 Audit de logs** — Contrôle la conformité Article 12 (traçabilité obligatoire)
- **📊 Génération de rapports** — Rapports PDF/JSON et artefacts réglementaires

---

## 🚀 Installation rapide

```bash
# Cloner le repository
git clone https://github.com/yhz-dotcom/ai-act-audit-tool.git
cd ai-act-audit-tool

# Installer avec les dépendances de développement
pip install -e ".[dev]"
```

---

## 📖 Usage rapide

### Classifier un système IA

```bash
# Classification basique
ai-act-audit classify --name "MonChatbot" --description "Chatbot support client"

# Classification avec détails
ai-act-audit classify \
  --name "RecrutIA Pro" \
  --description "Système de tri automatique de CV" \
  --domain "RH" \
  --employment-related \
  --uses-personal-data \
  --automated-decision-making
```

### Tester la robustesse (Article 15)

```bash
# Tous les vecteurs d'attaque
ai-act-audit jailbreak --target http://localhost:8000

# Catégories spécifiques
ai-act-audit jailbreak --categories prompt_injection,roleplay
```

### Auditer des logs (Article 12)

```bash
# Vérifier conformité
ai-act-audit logs --sample examples/compliant_log_sample.json --system "MonChatbot"

# Générer schéma conforme
ai-act-audit schema > my_log_schema.json
```

### Générer des artefacts réglementaires

```bash
# Déclaration UE de conformité (Art. 19)
ai-act-audit generate eu-conformity-declaration --system IA-001

# Documentation technique Annexe IV
ai-act-audit generate annex-iv-doc --system IA-001

# Export registre UE (Art. 49)
ai-act-audit generate eu-register-entry --system IA-001
```

---

## 📁 Structure du projet

```
ai-act-audit/
├── ai_act_audit/
│   ├── risk_classifier/          # Classification Article 6 (Annexes I & III)
│   │   ├── classifier.py         # Logique de classification
│   │   └── schemas.py            # Modèles Pydantic
│   ├── jailbreak_tester/         # Tests robustesse Article 15
│   │   ├── tester.py             # 8 vecteurs d'attaque
│   │   └── vectors.py            # Définition des tests
│   ├── logging_auditor/          # Audit logs Article 12
│   │   ├── auditor.py            # Vérification conformité
│   │   └── schemas.py            # Schéma Pydantic conforme
│   ├── report_generator/         # Génération rapports
│   │   └── generator.py          # PDF/JSON/Artefacts
│   └── cli.py                    # Interface ligne de commande
├── tests/                        # Tests unitaires et cas de validation
│   └── test_classification_cases.py  # 4 cas tests AI Act
├── docs/                         # Documentation
│   ├── CLASSIFICATION_LOGIC.md   # Arbre de décision Article 6
│   ├── JAILBREAK_VECTORS.md      # Vecteurs d'attaque Article 15
│   └── USAGE.md                  # Guide complet
├── examples/                     # Exemples de logs conformes
└── README.md                     # Ce fichier
```

---

## 🧪 Tests de validation

```bash
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=ai_act_audit --cov-report=html

# Cas spécifiques de classification AI Act
pytest tests/test_classification_cases.py -v
```

### Cas tests inclus

| Cas | Classification | Description |
|:----|:---------------|:------------|
| `test_cv_screening_high_risk` | 🔴 Haut risque | Tri automatique de CV (Annexe III) |
| `test_spell_checker_exempted` | 🟡 Exempté | Correcteur orthographique (Art 6(3)) |
| `test_password_generator_minimal` | 🟢 Minimal | Générateur de mots de passe |
| `test_profiling_stays_high_risk` | 🔴 Haut risque | Profilage = pas d'exemption |

---

## 📚 Documentation

### Architecture de classification

Voir [docs/CLASSIFICATION_LOGIC.md](docs/CLASSIFICATION_LOGIC.md) pour l'arbre de décision complet :

1. **Article 5** — Pratiques interdites
2. **Annexe I** — Composants de sécurité
3. **Annexe III** — Secteurs haut risque
4. **Article 6(3)** — Exemptions (avec vérification profilage)
5. **Article 50** — Obligations de transparence

### Vecteurs d'attaque

Voir [docs/JAILBREAK_VECTORS.md](docs/JAILBREAK_VECTORS.md) pour les 8 vecteurs testés :

| # | Catégorie | Vecteur | Sévérité |
|:-:|:----------|:--------|:--------:|
| 1 | Prompt Injection | Ignore previous instructions | 🔴 Critique |
| 2 | Roleplay | DAN (Do Anything Now) | 🔴 Critique |
| 3 | Roleplay | Developer Mode | 🔴 Critique |
| 4 | Encoding | Base64 obfuscation | 🟠 Haute |
| 5 | Context Manipulation | Hypothetical scenario | 🟠 Haute |
| 6 | Context Manipulation | Translation trick | 🟠 Haute |
| 7 | Adversarial | Token smuggling | 🟡 Moyenne |
| 8 | Multi-turn | Gradual escalation | 🟡 Moyenne |

### Schéma de logs conforme Article 12

```python
from ai_act_audit.logging_auditor.schemas import AIActLogEntry

log = AIActLogEntry(
    session_id="sess_550e8400-e29b-41d4-a716-446655440000",
    system_id="IA-RECRUIT-001",
    system_version="2.3.1",
    timestamp_start=datetime.now(timezone.utc),
    timestamp_end=datetime.now(timezone.utc),
    input_data_hash="a3f5c8e9d2b1...",
    output_data_hash="b7e9d1f4a8c2...",
    reference_databases=["cv_database_v3"],
    user_id="recruiter_001",
    request_id="req_abc123",
    human_oversight_id="manager_sarah",
    human_oversight_decision="APPROVED"
)
```

---

## 🛡️ Conformité AI Act

### Articles couverts

| Article | Fonctionnalité | Statut |
|:--------|:---------------|:------:|
| Art. 5 | Pratiques interdites | ✅ |
| Art. 6 | Classification risques | ✅ |
| Art. 9 | Gestion risques | 📝 Documentation |
| Art. 10 | Gouvernance données | 📝 Documentation |
| Art. 11 | Documentation technique | 📝 Templates |
| Art. 12 | Logs traçabilité | ✅ |
| Art. 13 | Transparence | 📝 Documentation |
| Art. 14 | Supervision humaine | 📝 Documentation |
| Art. 15 | Robustesse/cybersécurité | ✅ |
| Art. 19 | Déclaration UE conformité | 📝 Template |
| Art. 43 | Évaluation conformité | 📝 Documentation |
| Art. 49 | Registre UE | 📝 Export |
| Art. 72 | Surveillance post-marché | 📝 Documentation |

Légende :
- ✅ Implémenté
- 📝 Documentation/template disponible

---

## 🤝 Intégration avec ai-act-iso42001-framework

Ce tool peut s'intégrer avec le framework ISO 42001 :

```python
from ai_act_audit.integrations.iso42001_bridge import export_audit_to_iso42001

# Exporter résultats vers framework ISO 42001
iso_data = export_audit_to_iso42001(
    audit_result=classification_result,
    workflow_id="WF-RECRUIT-001"
)
```

---

## 🗺️ Roadmap

### ✅ Version 0.1.0 (Actuelle)
- Classification Article 6
- Tests jailbreak (8 vecteurs)
- Audit logs Article 12

### 🚧 Version 0.2.0 (En cours)
- Génération artefacts réglementaires
- Dashboard de conformité
- CI/CD compliance checks

### 📅 Version 0.3.0 (Planifié)
- Intégration LLM pour tests dynamiques
- Mode audit tiers
- API REST

---

## 📄 Licence

MIT License - voir [LICENSE](LICENSE) pour les détails.

---

## 🙏 Contributions

Les contributions sont les bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les guidelines.

---

**Développé avec ❤️ pour la conformité AI Act européen.**
