# 💼 Emploi Store

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)

> **Extracteur et analyseur d'offres d'emploi France Travail**  
> API moderne, dashboard interactif et visualisations de données en temps réel.

## ✨ Fonctionnalités

- 🔍 **Extraction automatique** des offres d'emploi via l'API France Travail
- 🗄️ **Stockage SQLite** local et performant
- 🚀 **API REST** avec FastAPI (documentation auto-générée)
- 📊 **Dashboard interactif** avec Streamlit
- 🎨 **Visualisations** Plotly (cartes, graphiques, statistiques)
- ⚡ **Async/Await** pour des performances optimales
- 🧪 **Tests** avec pytest et couverture de code
- 🐳 **Docker** prêt à l'emploi

## 🚀 Démarrage rapide

### Prérequis

- Python 3.10+
- [Compte API France Travail](https://francetravail.io/produits-partages/catalogue)

### Installation

```bash
# Cloner le repository
git clone https://github.com/votre-username/emploi-store.git
cd emploi-store

# Installation
pip install -e ".[dev]"

# Configuration
cp .env.example .env
# Éditer .env avec vos credentials France Travail
```

### Utilisation

```bash
# Initialiser la base de données
emploi-store init

# Extraire les offres (ex: Développeur Python)
emploi-store extract "Développeur Python"

# Voir les statistiques
emploi-store stats

# Lancer l'API REST
emploi-store api

# Lancer le dashboard (dans un autre terminal)
emploi-store dashboard
```

## 📊 Dashboard

Le dashboard Streamlit offre plusieurs vues :

- **Vue d'ensemble** : KPIs et distribution des contrats
- **Salaires** : Analyse par département avec graphiques interactifs
- **Compétences** : Top compétences demandées
- **Géographie** : Répartition par département
- **Liste des offres** : Recherche et filtres

Accès : http://localhost:8501

## 🛠️ Architecture

```
emploi_store/
├── config/          # Configuration et settings
├── models/          # Modèles SQLAlchemy (ORM)
├── api/             # Client API France Travail (async)
├── services/        # Logique métier
└── tests/           # Tests unitaires

api/                 # API FastAPI
dashboard/           # Dashboard Streamlit
cli.py               # Interface CLI
```

### Stack technique

| Composant | Technologie |
|-----------|-------------|
| Backend | Python 3.10+, FastAPI |
| Database | SQLite + SQLAlchemy 2.0 |
| API Client | aiohttp (async) |
| Dashboard | Streamlit + Plotly |
| CLI | Typer + Rich |
| Tests | pytest + pytest-asyncio |

## 📡 API Endpoints

L'API REST est accessible sur http://localhost:8000

### Endpoints principaux

```
GET  /                  → Info API
GET  /health            → Health check
GET  /offers            → Liste des offres
GET  /offers/{id}       → Détails d'une offre
GET  /stats/salaries    → Stats salaires par dépt
GET  /stats/skills      → Top compétences
GET  /stats/offers-by-department
GET  /stats/contracts   → Distribution contrats
GET  /stats/summary     → Résumé global
```

### Documentation interactive

- Swagger UI : http://localhost:8000/docs
- ReDoc : http://localhost:8000/redoc

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Avec couverture
pytest --cov=emploi_store

# Linting
ruff check emploi_store/
black --check emploi_store/
mypy emploi_store/
```

## 🐳 Docker

```bash
# Build et démarrage
docker-compose up --build

# L'API sera accessible sur http://localhost:8000
# Le dashboard sur http://localhost:8501
```

## 📝 Configuration

### Variables d'environnement

Créez un fichier `.env` :

```env
# API France Travail (obligatoire)
FRANCETRAVAIL_CLIENT_ID=votre_client_id
FRANCETRAVAIL_CLIENT_SECRET=votre_client_secret

# Database (optionnel)
DATABASE_URL=sqlite:///./data/emploi_store.db

# API (optionnel)
API_HOST=0.0.0.0
API_PORT=8000
```

### Obtenir les credentials France Travail

1. Créez un compte sur [francetravail.io](https://francetravail.io)
2. Créez un projet dans le catalogue
3. Souscrivez à l'API "Offres d'emploi"
4. Récupérez votre `CLIENT_ID` et `CLIENT_SECRET`

## 📈 Exemples d'utilisation

### Extraction par programmation

```python
from emploi_store.services.extraction import ExtractionService
from emploi_store.models.database import SessionLocal

async def extract_data():
    db = SessionLocal()
    service = ExtractionService(db)
    
    result = await service.extract_offers(
        keyword="Data Scientist",
        max_departments=10  # Limite pour les tests
    )
    
    print(f"{result['saved']} offres sauvegardées")
```

### Analyse des données

```python
from emploi_store.services.analysis import AnalysisService

service = AnalysisService(db)

# Top 10 compétences
top_skills = service.get_top_skills(limit=10)

# Stats salaires par département
salary_stats = service.get_salary_stats_by_department()
```

## 📄 License

Distribué sous licence MIT. Voir [LICENSE](LICENSE) pour plus d'informations.
