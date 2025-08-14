#!/usr/bin/env python3
"""
Script d'installation automatisé pour Vizaur-EDA-Tool
Ce script automatise tout le processus d'installation et de configuration.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

class Colors:
    """Codes couleur pour l'affichage dans le terminal"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header():
    """Affiche l'en-tête du script"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=" * 60)
    print("🚀 INSTALLATION AUTOMATISÉE - VIZAUR-EDA-TOOL")
    print("=" * 60)
    print(f"{Colors.ENDC}")

def print_step(step, message):
    """Affiche une étape avec formatage"""
    print(f"\n{Colors.OKBLUE}[ÉTAPE {step}]{Colors.ENDC} {Colors.BOLD}{message}{Colors.ENDC}")

def print_success(message):
    """Affiche un message de succès"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")

def print_warning(message):
    """Affiche un message d'avertissement"""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")

def print_error(message):
    """Affiche un message d'erreur"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")

def check_python_version():
    """Vérifie la version de Python"""
    print_step(1, "Vérification de la version Python")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8+ requis. Version actuelle : {version.major}.{version.minor}")
        sys.exit(1)
    
    print_success(f"Python {version.major}.{version.minor}.{version.micro} détecté")
    return True

def check_requirements_file():
    """Vérifie l'existence du fichier requirements.txt"""
    print_step(2, "Vérification du fichier requirements.txt")
    
    if not os.path.exists("requirements.txt"):
        print_error("Fichier requirements.txt introuvable")
        sys.exit(1)
    
    print_success("Fichier requirements.txt trouvé")
    return True

def create_virtual_environment():
    """Crée l'environnement virtuel"""
    print_step(3, "Création de l'environnement virtuel")
    
    venv_path = "venv"
    
    # Supprimer l'environnement virtuel existant s'il existe
    if os.path.exists(venv_path):
        print_warning("Environnement virtuel existant détecté, suppression...")
        try:
            shutil.rmtree(venv_path)
            print_success("Ancien environnement virtuel supprimé")
        except Exception as e:
            print_error(f"Erreur lors de la suppression : {e}")
            return False
    
    # Créer le nouvel environnement virtuel
    try:
        subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
        print_success("Environnement virtuel créé avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Erreur lors de la création de l'environnement virtuel : {e}")
        return False

def get_activate_script():
    """Retourne le chemin du script d'activation selon l'OS"""
    system = platform.system().lower()
    
    if system == "windows":
        return "venv\\Scripts\\activate"
    else:
        return "venv/bin/activate"

def install_dependencies():
    """Installe les dépendances"""
    print_step(4, "Installation des dépendances")
    
    # Déterminer le chemin de pip selon l'OS
    system = platform.system().lower()
    if system == "windows":
        pip_path = "venv\\Scripts\\pip"
    else:
        pip_path = "venv/bin/pip"
    
    try:
        # Mettre à jour pip
        print("Mise à jour de pip...")
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        
        # Installer les dépendances
        print("Installation des dépendances...")
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        
        print_success("Toutes les dépendances installées avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Erreur lors de l'installation des dépendances : {e}")
        return False

def setup_database():
    """Configure la base de données"""
    print_step(5, "Configuration de la base de données")
    
    # Déterminer le chemin de manage.py
    manage_py = "manage.py"
    if not os.path.exists(manage_py):
        print_error("Fichier manage.py introuvable")
        return False
    
    # Déterminer le chemin de python selon l'OS
    system = platform.system().lower()
    if system == "windows":
        python_path = "venv\\Scripts\\python"
    else:
        python_path = "venv/bin/python"
    
    try:
        # Exécuter les migrations
        print("Exécution des migrations...")
        subprocess.run([python_path, manage_py, "migrate"], check=True)
        
        print_success("Base de données configurée avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Erreur lors de la configuration de la base de données : {e}")
        return False

def create_superuser():
    """Propose de créer un superutilisateur"""
    print_step(6, "Création d'un superutilisateur (optionnel)")
    
    response = input("Voulez-vous créer un superutilisateur ? (y/N): ").strip().lower()
    
    if response in ['y', 'yes', 'oui', 'o']:
        system = platform.system().lower()
        if system == "windows":
            python_path = "venv\\Scripts\\python"
        else:
            python_path = "venv/bin/python"
        
        try:
            subprocess.run([python_path, "manage.py", "createsuperuser"], check=True)
            print_success("Superutilisateur créé avec succès")
        except subprocess.CalledProcessError as e:
            print_warning(f"Erreur lors de la création du superutilisateur : {e}")
    else:
        print_warning("Création du superutilisateur ignorée")

def launch_server():
    """Lance le serveur de développement"""
    print_step(7, "Lancement du serveur de développement")
    
    system = platform.system().lower()
    if system == "windows":
        python_path = "venv\\Scripts\\python"
    else:
        python_path = "venv/bin/python"
    
    print_success("Serveur en cours de lancement...")
    print(f"{Colors.OKCYAN}🌐 L'application sera accessible sur : http://127.0.0.1:8000{Colors.ENDC}")
    print(f"{Colors.WARNING}💡 Appuyez sur Ctrl+C pour arrêter le serveur{Colors.ENDC}")
    
    try:
        subprocess.run([python_path, "manage.py", "runserver"])
    except KeyboardInterrupt:
        print(f"\n{Colors.OKGREEN}👋 Serveur arrêté. Merci d'avoir utilisé Vizaur-EDA-Tool !{Colors.ENDC}")
    except Exception as e:
        print_error(f"Erreur lors du lancement du serveur : {e}")

def main():
    """Fonction principale"""
    print_header()
    
    # Vérifications préliminaires
    if not check_python_version():
        return
    
    if not check_requirements_file():
        return
    
    # Installation
    if not create_virtual_environment():
        return
    
    if not install_dependencies():
        return
    
    if not setup_database():
        return
    
    # Configuration optionnelle
    create_superuser()
    
    # Lancement
    launch_server()

if __name__ == "__main__":
    main() 