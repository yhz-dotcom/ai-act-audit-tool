# Arbre de Décision - Classification Article 6 AI Act

**Référence**: docs/CLASSIFICATION_LOGIC.md  
**Version**: 1.0  
**Date**: 2026-03-02

---

## 🎯 Vue d'ensemble

Cette documentation décrit l'algorithme de classification utilisé par `ai-act-audit-tool` pour déterminer le niveau de risque d'un système d'IA selon l'Article 6 du AI Act.

---

## 🌳 Arbre de Décision Complet

```
START: Système IA
│
├─► Article 5? (Interdit?)
│   ├─► OUI ──► 🚫 PROHIBITED (Arrêt immédiat)
│   └─► NON
│       │
│       ├─► Annexe I? (Composant sécurité?)
│       │   ├─► OUI ──► 🔴 HIGH_RISK (Régime complet)
│       │   └─► NON
│       │       │
│       │       ├─► Annexe III?
│       │       │   ├─► NON
│       │       │   │   ├─► Article 50? (Transparence?)
│       │       │   │   │   ├─► OUI ──► 🟡 LIMITED_RISK (Transparence)
│       │       │   │   │   └─► NON ──► 🟢 MINIMAL_RISK (Pas d'obligation)
│       │       │   │
│       │       │   └─► OUI
│       │       │       │
│       │       │       ├─► Exemption Article 6(3)?
│       │       │       │   ├─► NON ──► 🔴 HIGH_RISK (Régime complet)
│       │       │       │   └─► OUI
│       │       │       │       │
│       │       │       │       ├─► Profilage?
│       │       │       │       │   ├─► OUI ──► 🔴 HIGH_RISK (Maintien haut risque)
│       │       │       │       │   └─► NON ──► 🟡 LIMITED_RISK (Exemption Art 6(3))
```

---

## 📋 Décision Step-by-Step

### Étape 1: Article 5 - Pratiques Interdites

**Vérification**: Le système utilise-t-il des pratiques interdites ?

| Pratique | Détection | Action |
|:---------|:----------|:-------|
| Manipulation subliminale | Keywords: "subliminal", "inconscient" | 🚫 INTERDIT |
| Exploitation vulnérabilités | Keywords: "handicap", "enfant", "vulnérable" | 🚫 INTERDIT |
| Scoring social | Keywords: "score social", "crédit social" | 🚫 INTERDIT |
| Biométrie temps réel publique | Keywords: "biométrie", "temps réel", "espace public" | 🚫 INTERDIT |
| Émotions écoles/bureaux | Keywords: "émotions", "école", "bureau" | 🚫 INTERDIT |

**Code**:
```python
def _is_prohibited(self, system: AISystem) -> bool:
    prohibited_keywords = [
        "manipulation subliminale",
        "exploitation handicap", 
        "scoring social",
        "biométrie temps réel public"
    ]
    desc_lower = system.description.lower()
    return any(kw in desc_lower for kw in prohibited_keywords)
```

---

### Étape 2: Annexe I - Composants Sécurité

**Vérification**: Le système est-il un composant de sécurité d'un produit réglementé ?

| Produit | Exemple SIA | Classification |
|:--------|:------------|:---------------|
| Machines | Système arrêt d'urgence | 🔴 Haut risque |
| Jouets | IA reconnaissance formes | 🔴 Haut risque |
| Équipements médicaux | Diagnostic IA | 🔴 Haut risque |
| Véhicules | Conduite autonome | 🔴 Haut risque |

**Note**: Actuellement non implémenté dans `ai-act-audit-tool` - à ajouter.

---

### Étape 3: Annexe III - Secteurs Haut Risque

**Vérification**: L'usage prévu figure-t-il dans l'Annexe III ?

| Secteur (Point) | Détection | Exemples |
|:----------------|:----------|:---------|
| Biométrie (1) | `is_biometric_system=True` | Reconnaissance faciale, empreintes |
| Éducation (2) | `is_education_related=True` | Notation automatique, orientation |
| Emploi (3) | `is_employment_related=True` | Tri CV, évaluation candidats |
| Accès services publics (4) | `is_public_services=True` | Aide bénéficiaires |
| Services essentiels privés (5) | `is_essential_services=True` | Crédit, assurance |
| Justice (6) | `is_justice_related=True` | Aide juges, évaluation preuves |
| Migration/Asile (7) | `is_migration_asylum=True` | Évaluation demandes |
| Application loi (8) | `is_law_enforcement=True` | Profilage, évaluation risque |
| Démocratie (9) | `is_democracy_related=True` | Diffusion contenu électoral |

**Code**:
```python
def _is_high_risk(self, system: AISystem) -> bool:
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
```

---

### Étape 4: Exemption Article 6(3)

**Vérification**: Le système remplit-il les 4 conditions cumulatives ?

**⚠️ IMPORTANT**: Toutes les conditions doivent être remplies ET pas de profilage.

| Condition | Champ AISystem | Validation |
|:----------|:---------------|:-----------|
| **C1**: Tâche procédurale étroite | `narrow_procedural_task=True` | Liste blanche tâches |
| **C2**: Améliore résultat humain | `improves_human_work=True` | Benchmark avant/après |
| **C3**: Supervision humaine | `human_oversight=True` | Dans la boucle |
| **C4**: Pas de profilage | `uses_personal_data=False` | Vérification données |

**⚠️ CRITIQUE**: Si profilage détecté → Maintien haut risque même si C1-C3 OK

**Code** (CORRECTION À APPORTER):
```python
def _has_article_6_3_exception(self, system: AISystem) -> bool:
    """Vérifie si le système bénéficie d'une exception Article 6(3)."""
    
    # CRITIQUE: Si profilage détecté → Pas d'exemption possible
    if system.uses_personal_data and system.automated_decision_making:
        return False  # Profilage = maintien haut risque
    
    # Toutes les conditions doivent être cumulées (ET logique, pas OU)
    return (
        system.narrow_procedural_task and
        system.improves_human_work and
        system.non_material_influence and
        system.human_oversight
    )
```

---

### Étape 5: Article 50 - Risque Limité (Transparence)

**Vérification**: Le système nécessite-t-il une obligation de transparence ?

| Type | Détection | Obligations |
|:-----|:----------|:------------|
| Chatbots | Keywords: "chatbot", "conversationnel" | Informer utilisateur |
| Deepfakes | Keywords: "deepfake", "synthétique" | Marquer contenu |
| Génération texte | Keywords: "génération", "rédaction automatique" | Divulguer IA |

**Code**:
```python
def _is_limited_risk(self, system: AISystem) -> bool:
    limited_risk_keywords = ["chatbot", "bot conversationnel", "deepfake", "contenu synthétique"]
    desc_lower = system.description.lower()
    return any(kw in desc_lower for kw in limited_risk_keywords)
```

---

### Étape 6: Risque Minimal

**Défaut**: Si aucune des conditions précédentes n'est remplie.

**Obligations**: Aucune obligation réglementaire spécifique.

**Recommandations**: Bonnes pratiques volontaires (code de conduite, etc.)

---

## 🔍 Matrice de Décision Complète

| Article 5 | Annexe I | Annexe III | Art 6(3) | Profilage | Article 50 | Résultat |
|:---------:|:--------:|:----------:|:--------:|:---------:|:----------:|:---------|
| ✅ | - | - | - | - | - | 🚫 INTERDIT |
| ❌ | ✅ | - | - | - | - | 🔴 HAUT RISQUE |
| ❌ | ❌ | ✅ | ❌ | - | - | 🔴 HAUT RISQUE |
| ❌ | ❌ | ✅ | ✅ | ✅ | - | 🔴 HAUT RISQUE (profilage) |
| ❌ | ❌ | ✅ | ✅ | ❌ | - | 🟡 RISQUE LIMITÉ (exemption) |
| ❌ | ❌ | ❌ | - | - | ✅ | 🟡 RISQUE LIMITÉ (transparence) |
| ❌ | ❌ | ❌ | - | - | ❌ | 🟢 RISQUE MINIMAL |

---

## ⚠️ Points d'Attention

### 1. Faux Négatifs Potentiels

| Scénario | Risque | Mitigation |
|:---------|:-------|:-----------|
| Description ambiguë | Non-détection haut risque | Analyse sémantique plus poussée |
| Exemption abusive | Sous-classification | Validation manuelle obligatoire |
| Profilage indirect | Non-détection | Audit données entrées |

### 2. Évolutions à Prévoir

- [ ] Intégration Annexe I (composants sécurité)
- [ ] Détection automatique profilage
- [ ] Analyse sémantique avancée (LLM)
- [ ] Base de cas jurisprudentiels

---

## 🧪 Tests de Validation

Voir `tests/test_classification_cases.py` pour les cas tests validés.

---

**Document mis à jour**: 2026-03-02  
**Prochaine revue**: Après publication guidelines Commission UE
