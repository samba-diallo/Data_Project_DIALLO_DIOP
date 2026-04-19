# Tests Unitaires – Documentation

Tests unitaires du projet **Projet Data - Dashboard** réalisés avec **pytest**.

Aucune donnée fictive n'est utilisée. Les tests vérifient la **structure, les imports et la configuration** du projet.

---

## Fichiers de tests

| Fichier | Objectif | # Tests |
|---------|----------|---------|
| `test_config.py` | Vérifie que la configuration est correcte | 6 |
| `test_imports.py` | Vérifie que tous les modules s'importent | 10 |
| `test_structure.py` | Vérifie les signatures, docstrings, types | ~30 |
| `test_requirements.py` | Vérifie que les packages requis sont installés | 7 |
| `test_get_data.py` | Vérifie la structure de `get_data.py` | 9 |
| `test_clean_data.py` | Vérifie la structure de `clean_data.py` | 14 |
| `test_common_functions.py` | Vérifie la structure de `common_functions.py` | 11 |
| **TOTAL** | | **~87 tests** |

---

## Exécuter les tests

### 1. S'assurer que pytest est installé

```bash
python -m pip install pytest
```

### 2. Lancer TOUS les tests

```bash
pytest tests/
```

Ou avec plus de détails :

```bash
pytest tests/ -v
```

### 3. Lancer les tests d'un fichier spécifique

```bash
pytest tests/test_config.py -v
```

### 4. Lancer un test spécifique

```bash
pytest tests/test_config.py::test_config_base_dir_exists -v
```

### 5. Afficher les prints (output de debug)

```bash
pytest tests/ -v -s
```

### 6. Arrêter au premier échec

```bash
pytest tests/ -x
```

### 7. Compte-rendu avec couverture de code (optionnel)

```bash
# Installer coverage
python -m pip install pytest-cov

# Générer le rapport
pytest tests/ --cov=src --cov-report=html
```

---

## Ce que testent les fichiers

### `test_config.py` – Configuration

- [x] `BASE_DIR` exist et est valide
- [x] `DATA_RAW` et `DATA_CLEAN` sont définis
- [x] Répertoires `data/raw/` et `data/cleaned/` existent
- [x] `DATA_URL` est défini
- [x] Paramètres Dash (`APP_TITLE`, `DEBUG_MODE`, `HOST`, `PORT`) sont valides
- [x] Port est entre 1 et 65535

### `test_imports.py` – Imports

- [x] Module `config` s'importe
- [x] Module `main` s'importe
- [x] Packages `src/`, `src.components/`, `src.pages/`, `src.utils/` s'importent
- [x] Toutes les sous-modules s'importent sans erreur
- [x] Toutes les fonctions peuvent être importées (`download_data`, `filter_data`, etc.)

### `test_structure.py` – Structure du code

#### Backend (`get_data.py`, `clean_data.py`, `common_functions.py`)
- [x] Fonction existe et est callable
- [x] Chaque fonction a une docstring
- [x] Signatures de paramètres correctes (types, nombre)
- [x] Annotations de retour présentes (`-> pd.DataFrame`, `-> None`, etc.)
- [x] Paramètres attendus (`df`, `group_by`, `metric`, etc.)

#### Frontend (`main.py`, pages, composants)
- [x] Fonction existe et est callable
- [x] Docstrings présentes
- [x] Annotations de retour (`-> html.Div`, `-> go.Figure`, etc.)
- [x] Paramètres corrects (ex: `app` pour les callbacks)

### `test_requirements.py` – Dépendances

- [x] `pandas` installé
- [x] `dash` installé
- [x] `plotly` installé
- [x] `pytest` installé
- [x] Versions correctes (pandas >= 1.0, dash >= 2.0, plotly >= 4.0)

### `test_get_data.py` – Module get_data

- [x] `download_data()` callable et avec docstring
- [x] Annotation de retour `pd.DataFrame`
- [x] `save_raw_data()` a au least 1 paramètre
- [x] `save_raw_data()` retourne `None`
- [x] `main()` callable et sans paramètres obligatoires
- [x] Toutes les docstrings présentes

### `test_clean_data.py` – Module clean_data

- [x] Toutes les fonctions callable (`load_raw_data`, `remove_duplicates`, `handle_missing_values`, `normalize_columns`, `save_cleaned_data`)
- [x] Chaque fonction a une docstring
- [x] Signatures correctes (paramètres, retours)
- [x] `main()` sans paramètres obligatoires
- [x] Retours attendus (`pd.DataFrame` ou `None`)

### `test_common_functions.py` – Utilitaires

- [x] `load_cleaned_data()` sans paramètres obligatoires, retourne `DataFrame`
- [x] `filter_data()` accepte `**kwargs` pour les critères de filtrage
- [x] `aggregate_data()` a 3+ paramètres (`df`, `group_by`, `metric`)
- [x] Toutes les docstrings présentes
- [x] Annotations de type correctes

---

## Résultats attendus

### Quand TOUS les tests passent

```
collected 87 items

tests/test_config.py ..................... PASSED
tests/test_imports.py .................... PASSED
tests/test_structure.py .................. PASSED
tests/test_requirements.py ............... PASSED
tests/test_get_data.py ................... PASSED
tests/test_clean_data.py ................. PASSED
tests/test_common_functions.py ........... PASSED

======================== 87 passed in 2.45s =========================
```

### En cas d'erreur : Exemples

**Erreur : Missing docstring**
```
FAILED tests/test_get_data.py::test_download_data_has_docstring
AssertionError: download_data() doit avoir une docstring
```
→ Ajoute une docstring à `download_data()` dans `src/utils/get_data.py`

**Erreur : Missing return annotation**
```
FAILED tests/test_clean_data.py::test_load_raw_data_return_annotation
AssertionError: load_raw_data() doit avoir une annotation...
```
→ Change `def load_raw_data():` en `def load_raw_data() -> pd.DataFrame:`

**Erreur : Package not installed**
```
FAILED tests/test_requirements.py::test_dash_installed
AssertionError: dash doit être installé...
```
→ Exécute `python -m pip install -r requirements.txt`

---

## Stratégie de test

### Tests SANS données fictives (tous les tests actuels)

- Structure du code (fonctions existent)
- Types et signatures
- Documentation (docstrings)
- Imports (modules s'importent)
- Configuration (fichiers, répertoires)
- Dépendances (packages installés)

### ⏳ Tests AVEC données (à ajouter plus tard)

Une fois que tu auras des données réelles dans `data/cleaned/cleaneddata.csv`:

- Comportement des fonctions (résultats exacts)
- Nettoyage correct des NaN
- Suppression des doublons
- Filtrage et agrégation
- Génération des graphiques
- Callbacks Dash

---

## 💡 Astuce : Exécution continue (Watch mode)

Pour relancer les tests à chaque modification de fichier :

```bash
# Installer pytest-watch
python -m pip install pytest-watch

# Lancer en watch mode
ptw tests/
```

---

## Documentation pytest

- **Docs officielles** : https://docs.pytest.org/
- **Fixtures** : https://docs.pytest.org/en/stable/how-to/fixtures.html
- **Assertions** : https://docs.pytest.org/en/stable/how-to/assert.html
- **Parametrize** : https://docs.pytest.org/en/stable/how-to/parametrize.html

---

**Créé** : 8 avril 2026  
**Dernière mise à jour** : 8 avril 2026
