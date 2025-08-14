#!/bin/bash

# Script d'installation automatisé pour Vizaur-EDA-Tool (Linux/Mac)
# Ce script automatise tout le processus d'installation et de configuration.

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Fonctions d'affichage
print_header() {
    echo -e "${PURPLE}${BOLD}"
    echo "============================================================"
    echo "🚀 INSTALLATION AUTOMATISÉE - VIZAUR-EDA-TOOL"
    echo "============================================================"
    echo -e "${NC}"
}

print_step() {
    echo -e "\n${BLUE}[ÉTAPE $1]${NC} ${BOLD}$2${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérification de Python
check_python() {
    print_step "1" "Vérification de Python"
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
        PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_success "Python $PYTHON_VERSION détecté"
            return 0
        else
            print_error "Python 3.8+ requis. Version actuelle : $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python 3 non trouvé. Veuillez installer Python 3.8+"
        return 1
    fi
}

# Vérification des fichiers requis
check_files() {
    print_step "2" "Vérification des fichiers requis"
    
    if [ ! -f "requirements.txt" ]; then
        print_error "Fichier requirements.txt introuvable"
        return 1
    fi
    
    if [ ! -f "manage.py" ]; then
        print_error "Fichier manage.py introuvable"
        return 1
    fi
    
    print_success "Tous les fichiers requis trouvés"
    return 0
}

# Création de l'environnement virtuel
create_venv() {
    print_step "3" "Création de l'environnement virtuel"
    
    if [ -d "venv" ]; then
        print_warning "Environnement virtuel existant détecté, suppression..."
        rm -rf venv
        print_success "Ancien environnement virtuel supprimé"
    fi
    
    if python3 -m venv venv; then
        print_success "Environnement virtuel créé avec succès"
        return 0
    else
        print_error "Erreur lors de la création de l'environnement virtuel"
        return 1
    fi
}

# Installation des dépendances
install_deps() {
    print_step "4" "Installation des dépendances"
    
    # Activation de l'environnement virtuel
    source venv/bin/activate
    
    # Mise à jour de pip
    echo "Mise à jour de pip..."
    pip install --upgrade pip
    
    # Installation des dépendances
    echo "Installation des dépendances..."
    if pip install -r requirements.txt; then
        print_success "Toutes les dépendances installées avec succès"
        return 0
    else
        print_error "Erreur lors de l'installation des dépendances"
        return 1
    fi
}

# Configuration de la base de données
setup_db() {
    print_step "5" "Configuration de la base de données"
    
    # Activation de l'environnement virtuel
    source venv/bin/activate
    
    # Exécution des migrations
    echo "Exécution des migrations..."
    if python manage.py migrate; then
        print_success "Base de données configurée avec succès"
        return 0
    else
        print_error "Erreur lors de la configuration de la base de données"
        return 1
    fi
}

# Création du superutilisateur
create_superuser() {
    print_step "6" "Création d'un superutilisateur (optionnel)"
    
    read -p "Voulez-vous créer un superutilisateur ? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Activation de l'environnement virtuel
        source venv/bin/activate
        
        if python manage.py createsuperuser; then
            print_success "Superutilisateur créé avec succès"
        else
            print_warning "Erreur lors de la création du superutilisateur"
        fi
    else
        print_warning "Création du superutilisateur ignorée"
    fi
}

# Lancement du serveur
launch_server() {
    print_step "7" "Lancement du serveur de développement"
    
    # Activation de l'environnement virtuel
    source venv/bin/activate
    
    print_success "Serveur en cours de lancement..."
    echo -e "${CYAN}🌐 L'application sera accessible sur : http://127.0.0.1:8000${NC}"
    echo -e "${YELLOW}💡 Appuyez sur Ctrl+C pour arrêter le serveur${NC}"
    
    # Lancement du serveur
    python manage.py runserver
}

# Fonction principale
main() {
    print_header
    
    # Vérifications préliminaires
    if ! check_python; then
        exit 1
    fi
    
    if ! check_files; then
        exit 1
    fi
    
    # Installation
    if ! create_venv; then
        exit 1
    fi
    
    if ! install_deps; then
        exit 1
    fi
    
    if ! setup_db; then
        exit 1
    fi
    
    # Configuration optionnelle
    create_superuser
    
    # Lancement
    launch_server
}

# Gestion de l'interruption
trap 'echo -e "\n${GREEN}👋 Installation interrompue. Merci d'avoir essayé Vizaur-EDA-Tool !${NC}"; exit 0' INT

# Exécution du script principal
main 