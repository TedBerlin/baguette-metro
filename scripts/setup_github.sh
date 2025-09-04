#!/bin/bash

# Script de configuration GitHub pour Baguette Metro
# Usage: ./scripts/setup_github.sh [repository-name]

set -e

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

# Vérifier si GitHub CLI est installé
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) n'est pas installé."
        print_status "Installation de GitHub CLI..."
        
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            if command -v brew &> /dev/null; then
                brew install gh
            else
                print_error "Homebrew n'est pas installé. Veuillez installer GitHub CLI manuellement."
                exit 1
            fi
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
            sudo apt update
            sudo apt install gh
        else
            print_error "OS non supporté. Veuillez installer GitHub CLI manuellement."
            exit 1
        fi
    fi
    print_success "GitHub CLI est installé."
}

# Vérifier l'authentification GitHub
check_github_auth() {
    if ! gh auth status &> /dev/null; then
        print_warning "Vous n'êtes pas authentifié avec GitHub."
        print_status "Authentification en cours..."
        gh auth login
    fi
    print_success "Authentification GitHub OK."
}

# Créer le repository GitHub
create_github_repo() {
    local repo_name=${1:-"baguette-metro"}
    
    print_status "Création du repository GitHub: $repo_name"
    
    # Créer le repository
    gh repo create "$repo_name" \
        --public \
        --description "🥖 Baguette & Métro - MVP Enterprise Ready: Optimisez votre trajet RATP avec une pause boulangerie ! Application intelligente avec IA, données temps réel RATP, et interface moderne." \
        --add-readme=false \
        --clone=false
    
    print_success "Repository GitHub créé: https://github.com/$(gh api user --jq .login)/$repo_name"
}

# Configurer le remote origin
setup_remote() {
    local repo_name=${1:-"baguette-metro"}
    local username=$(gh api user --jq .login)
    
    print_status "Configuration du remote origin..."
    
    # Supprimer l'ancien remote s'il existe
    git remote remove origin 2>/dev/null || true
    
    # Ajouter le nouveau remote
    git remote add origin "https://github.com/$username/$repo_name.git"
    
    print_success "Remote origin configuré."
}

# Pousser le code
push_to_github() {
    print_status "Poussée du code vers GitHub..."
    
    # Pousser la branche main
    git push -u origin main
    
    print_success "Code poussé vers GitHub avec succès !"
}

# Créer les issues et milestones
setup_project_management() {
    local repo_name=${1:-"baguette-metro"}
    
    print_status "Configuration de la gestion de projet..."
    
    # Créer des labels
    gh label create "enhancement" --description "Nouvelles fonctionnalités" --color "a2eeef" --repo "$repo_name" 2>/dev/null || true
    gh label create "bug" --description "Corrections de bugs" --color "d73a4a" --repo "$repo_name" 2>/dev/null || true
    gh label create "documentation" --description "Amélioration de la documentation" --color "0075ca" --repo "$repo_name" 2>/dev/null || true
    gh label create "docker" --description "Docker et déploiement" --color "0e8a16" --repo "$repo_name" 2>/dev/null || true
    gh label create "ai" --description "Intelligence artificielle" --color "7057ff" --repo "$repo_name" 2>/dev/null || true
    
    print_success "Labels créés."
}

# Afficher les informations finales
show_final_info() {
    local repo_name=${1:-"baguette-metro"}
    local username=$(gh api user --jq .login)
    
    echo ""
    echo "🎉 ================================================"
    echo "   BAGUETTE METRO - GITHUB SETUP COMPLETE !"
    echo "================================================ 🎉"
    echo ""
    print_success "Repository GitHub: https://github.com/$username/$repo_name"
    print_success "Clone URL: https://github.com/$username/$repo_name.git"
    echo ""
    print_status "Prochaines étapes:"
    echo "  1. 🌐 Ouvrir le repository dans votre navigateur"
    echo "  2. 📝 Configurer les secrets GitHub (si nécessaire)"
    echo "  3. 🐳 Tester le déploiement Docker"
    echo "  4. 🚀 Préparer la démo !"
    echo ""
    print_status "Commandes utiles:"
    echo "  • Voir le repository: gh repo view $repo_name"
    echo "  • Cloner: git clone https://github.com/$username/$repo_name.git"
    echo "  • Docker: docker-compose up --build"
    echo ""
}

# Fonction principale
main() {
    local repo_name=${1:-"baguette-metro"}
    
    echo "🚀 Configuration GitHub pour Baguette Metro"
    echo "============================================="
    echo ""
    
    # Vérifications préalables
    check_gh_cli
    check_github_auth
    
    # Configuration du repository
    create_github_repo "$repo_name"
    setup_remote "$repo_name"
    push_to_github
    setup_project_management "$repo_name"
    
    # Informations finales
    show_final_info "$repo_name"
}

# Exécuter le script
main "$@"
