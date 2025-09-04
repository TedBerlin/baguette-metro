#!/bin/bash

# 🥖 Baguette & Métro - Script d'installation développement
# Ce script configure l'environnement de développement complet

set -e  # Arrêter en cas d'erreur

echo "🚀 Configuration de l'environnement de développement Baguette & Métro"
echo "=================================================================="

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier Python
print_status "Vérification de Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION détecté"
else
    print_error "Python 3 n'est pas installé"
    exit 1
fi

# Vérifier pip
print_status "Vérification de pip..."
if command -v pip3 &> /dev/null; then
    print_success "pip3 détecté"
else
    print_error "pip3 n'est pas installé"
    exit 1
fi

# Créer l'environnement virtuel
print_status "Création de l'environnement virtuel..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    print_success "Environnement virtuel créé"
else
    print_warning "Environnement virtuel déjà existant"
fi

# Activer l'environnement virtuel
print_status "Activation de l'environnement virtuel..."
source .venv/bin/activate

# Mettre à jour pip
print_status "Mise à jour de pip..."
pip install --upgrade pip

# Installer les dépendances de base
print_status "Installation des dépendances de base..."
pip install -r requirements.txt

# Installer les dépendances de développement
print_status "Installation des dépendances de développement..."
pip install pytest pytest-cov flake8 black isort mypy bandit safety pre-commit

# Installer pre-commit hooks
print_status "Installation des hooks pre-commit..."
pre-commit install

# Vérifier Docker
print_status "Vérification de Docker..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    print_success "Docker $DOCKER_VERSION détecté"
else
    print_warning "Docker n'est pas installé (optionnel pour le développement local)"
fi

# Vérifier Docker Compose
print_status "Vérification de Docker Compose..."
if command -v docker-compose &> /dev/null; then
    print_success "Docker Compose détecté"
else
    print_warning "Docker Compose n'est pas installé (optionnel pour le développement local)"
fi

# Créer les dossiers nécessaires
print_status "Création des dossiers de données..."
mkdir -p data/raw data/processed logs

# Vérifier les fichiers de configuration
print_status "Vérification des fichiers de configuration..."

# Vérifier .env
if [ ! -f ".env" ]; then
    print_warning "Fichier .env manquant - création d'un template"
    cat > .env << EOF
# Configuration de l'environnement
ENVIRONMENT=development
DEBUG=true

# Clés API (à remplacer par vos vraies clés)
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_PLACES_API_KEY=your_google_places_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Configuration RATP GTFS
RATP_GTFS_URL=https://api-ratp.pierre-grimaud.fr/v4

# Configuration de l'application
API_PORT=8000
STREAMLIT_PORT=8501

# Configuration de la base de données
DATABASE_URL=sqlite:///./data/baguette_metro.db

# Configuration des langues supportées
SUPPORTED_LANGUAGES=fr,en,ja
EOF
    print_success "Fichier .env créé"
else
    print_success "Fichier .env existant"
fi

# Tests de validation
print_status "Exécution des tests de validation..."

# Test de l'environnement
if python test_environment.py; then
    print_success "Tests d'environnement passés"
else
    print_error "Tests d'environnement échoués"
    exit 1
fi

# Test d'import des modules
print_status "Test d'import des modules..."
python -c "
try:
    from src.api.main import app
    from src.data.openrouter_client import openrouter_client
    from src.frontend.app import st
    print('✅ Tous les modules importés avec succès')
except ImportError as e:
    print(f'❌ Erreur d\'import: {e}')
    exit(1)
"

# Test de formatage
print_status "Test de formatage du code..."
if black --check src/; then
    print_success "Formatage Black OK"
else
    print_warning "Formatage Black - exécution de black src/"
    black src/
fi

# Test de linting
print_status "Test de linting..."
if flake8 src/ --count --exit-zero --max-complexity=10 --max-line-length=88; then
    print_success "Linting OK"
else
    print_warning "Problèmes de linting détectés"
fi

# Test de sécurité
print_status "Test de sécurité..."
if bandit -r src/ -f json -o bandit-report.json; then
    print_success "Tests de sécurité OK"
else
    print_warning "Problèmes de sécurité détectés"
fi

# Affichage des informations finales
echo ""
echo "🎉 Configuration terminée avec succès !"
echo "======================================"
echo ""
echo "📋 Prochaines étapes :"
echo "1. Configurer vos clés API dans le fichier .env"
echo "2. Lancer l'application : python start_app.py"
echo "3. Accéder à l'interface : http://localhost:8501"
echo "4. Accéder à l'API : http://0.0.0.0:8000"
echo ""
echo "🛠️  Commandes utiles :"
echo "- Tests : pytest src/tests/"
echo "- Formatage : black src/"
echo "- Linting : flake8 src/"
echo "- Sécurité : bandit -r src/"
echo "- Pre-commit : pre-commit run --all-files"
echo ""
echo "📚 Documentation :"
echo "- README.md : Guide principal"
echo "- GOOGLE_API_SETUP.md : Configuration Google Places"
echo "- .github/SECRETS.md : Configuration CI/CD"
echo ""

print_success "Environnement de développement prêt ! 🥖🚇"
