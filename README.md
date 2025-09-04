# 🥖 Baguette & Métro

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Security: Enterprise](https://img.shields.io/badge/Security-Enterprise-red.svg)](SECURITY.md)
[![Ethics: AI Governance](https://img.shields.io/badge/Ethics-AI%20Governance-blue.svg)](AI_ETHICS_POLICY.md)

**Optimisez votre trajet RATP avec une pause boulangerie !**

Une application intelligente qui combine les données temps réel des transports en commun (RATP) avec les informations locales des boulangeries pour optimiser vos trajets urbains.

## 🚀 Fonctionnalités

- **Calcul d'ETA intelligent** : Modèle ML pour prédire les temps de trajet
- **Données temps réel** : Intégration GTFS-RT RATP pour les horaires en temps réel
- **Recherche de boulangeries** : IA pour trouver les meilleures boulangeries
- **Assistant IA** : Chat intelligent pour guider les utilisateurs
- **Dashboard analytique** : Visualisations et recommandations
- **Interface moderne** : Application Streamlit responsive et intuitive
- **API RESTful** : Backend FastAPI pour l'intégration avec d'autres services
- **Support multilingue** : Français, Anglais, Japonais
- **CI/CD complet** : Pipeline automatisé avec tests et déploiement

## 🏗️ Architecture

```
baguette-metro/
├── src/
│   ├── api/                 # API FastAPI
│   │   ├── main.py         # Point d'entrée API
│   │   ├── routes.py       # Endpoints ETA
│   │   └── schemas.py      # Modèles Pydantic
│   ├── data/               # Gestion des données
│   │   ├── google_places.py # Client Google Places
│   │   ├── gtfs_ingestion.py # Ingestion données RATP
│   │   └── cache_manager.py # Gestion du cache
│   ├── frontend/           # Interface utilisateur
│   │   ├── app.py          # Application Streamlit
│   │   ├── chat_interface.py # Interface de chat
│   │   └── map_utils.py    # Utilitaires cartographie
│   ├── models/             # Modèles ML
│   │   ├── eta_model.py    # Modèle de prédiction ETA
│   │   └── train_model.py  # Script d'entraînement
│   └── tests/              # Tests unitaires
├── data/                   # Données et cache
├── docs/                   # Documentation
├── notebooks/              # Notebooks Jupyter
└── scripts/                # Scripts utilitaires
```

## 🛠️ Installation

### Prérequis

- Python 3.10+
- Docker (optionnel)

### Installation locale

1. **Cloner le repository**
```bash
git clone <repository-url>
cd baguette-metro
```

2. **Créer un environnement virtuel**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditer .env avec vos clés API
```

### Variables d'environnement requises

```env
# Clés API (optionnelles pour le mode démo)
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_PLACES_API_KEY=your_google_places_api_key_here

# Configuration RATP
RATP_GTFS_URL=https://api-ratp.pierre-grimaud.fr/v4

# Configuration de l'application
ENVIRONMENT=development
DEBUG=true
API_PORT=8000
STREAMLIT_PORT=8501
```

## 🚀 Utilisation

### Mode développement

1. **Démarrer l'API**
```bash
uvicorn src.api.main:app --reload --port 8000
```

2. **Démarrer l'interface**
```bash
streamlit run src/frontend/app.py --server.port 8501
```

3. **Accéder à l'application**
- Interface : http://localhost:8501
- API : http://0.0.0.0:8000
- Documentation API : http://0.0.0.0:8000/docs

### Mode Docker

```bash
docker-compose up --build
```

## 📊 API Endpoints

### Calcul d'ETA
```http
POST /eta/calculate
{
  "start_lat": 48.8566,
  "start_lon": 2.3522,
  "end_lat": 48.8606,
  "end_lon": 2.3376,
  "language": "fr"
}
```

### Boulangeries à proximité
```http
GET /eta/bakeries?lat=48.8566&lon=2.3522&radius=500
```

### Santé de l'application
```http
GET /health
```

## 🧪 Tests

```bash
# Tests unitaires
pytest src/tests/

# Tests spécifiques
python test_api.py
python test_app.py

# Tests d'environnement
python test_environment.py

# Tests d'intégration OpenRouter
python test_openrouter_integration.py
```

## 🚀 CI/CD

Le projet utilise un pipeline CI/CD complet avec GitHub Actions :

### 🔄 Pipeline automatique
- **Tests** : Validation du code sur Python 3.10, 3.11, 3.12
- **Qualité** : Linting, formatage, vérification de types
- **Sécurité** : Analyse de vulnérabilités avec Bandit et Safety
- **Build** : Construction et publication d'images Docker
- **Déploiement** : Déploiement automatique staging/production

### 🛠️ Outils de développement
```bash
# Installation de l'environnement complet
./scripts/setup_dev.sh

# Formatage du code
black src/
isort src/

# Linting
flake8 src/

# Vérification de types
mypy src/

# Tests de sécurité
bandit -r src/
safety check

# Pre-commit hooks
pre-commit run --all-files
```

### 📋 Configuration des secrets
Voir `.github/SECRETS.md` pour configurer tous les secrets nécessaires.

## 🔧 Configuration

### Mode démo
L'application fonctionne en mode démo sans clés API. Les données sont simulées pour permettre le test et le développement.

### Mode production
Pour utiliser les vraies données :
1. Obtenir une clé Google Places API
2. Configurer l'URL GTFS-RT RATP
3. Optionnel : configurer OpenAI pour des fonctionnalités avancées

## 📈 Roadmap

- [ ] Intégration temps réel RATP GTFS-RT
- [ ] Modèles ML pour prédiction ETA
- [ ] Interface de chat IA
- [ ] Support multi-villes
- [ ] Application mobile
- [ ] Analytics et métriques

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence [MIT](LICENSE) - voir le fichier [LICENSE](LICENSE) pour plus de détails.

### 🛡️ Sécurité et Éthique

- **Sécurité** : [Politique de sécurité](SECURITY.md) de niveau entreprise
- **Éthique AI** : [Gouvernance éthique](AI_ETHICS_POLICY.md) complète
- **Conformité** : Standards internationaux respectés

### 🔒 Protection des Données

- **Clés API** : Protégées par .gitignore et chiffrement
- **Sécrets** : Gestion sécurisée des variables d'environnement
- **Audit** : Monitoring continu de la sécurité

## 🙏 Remerciements

- **RATP** pour les données GTFS
- **Google Places API** pour les informations locales
- **Streamlit** pour l'interface utilisateur
- **FastAPI** pour l'API backend

---

**Développé avec ❤️ pour optimiser vos trajets parisiens !**
