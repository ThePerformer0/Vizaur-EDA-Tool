@echo off
setlocal enabledelayedexpansion

REM Script d'installation automatisé pour Vizaur-EDA-Tool (Windows)
REM Ce script automatise tout le processus d'installation et de configuration.

echo.
echo ============================================================
echo 🚀 INSTALLATION AUTOMATISÉE - VIZAUR-EDA-TOOL
echo ============================================================
echo.

REM Vérification de Python
echo [ÉTAPE 1] Vérification de Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python non trouvé. Veuillez installer Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% détecté

REM Vérification des fichiers requis
echo.
echo [ÉTAPE 2] Vérification des fichiers requis
if not exist "requirements.txt" (
    echo ❌ Fichier requirements.txt introuvable
    pause
    exit /b 1
)

if not exist "manage.py" (
    echo ❌ Fichier manage.py introuvable
    pause
    exit /b 1
)

echo ✅ Tous les fichiers requis trouvés

REM Création de l'environnement virtuel
echo.
echo [ÉTAPE 3] Création de l'environnement virtuel
if exist "venv" (
    echo ⚠️  Environnement virtuel existant détecté, suppression...
    rmdir /s /q venv
    echo ✅ Ancien environnement virtuel supprimé
)

python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Erreur lors de la création de l'environnement virtuel
    pause
    exit /b 1
)
echo ✅ Environnement virtuel créé avec succès

REM Installation des dépendances
echo.
echo [ÉTAPE 4] Installation des dépendances
echo Mise à jour de pip...
venv\Scripts\pip.exe install --upgrade pip

echo Installation des dépendances...
venv\Scripts\pip.exe install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Erreur lors de l'installation des dépendances
    pause
    exit /b 1
)
echo ✅ Toutes les dépendances installées avec succès

REM Configuration de la base de données
echo.
echo [ÉTAPE 5] Configuration de la base de données
echo Exécution des migrations...
venv\Scripts\python.exe manage.py migrate
if %errorlevel% neq 0 (
    echo ❌ Erreur lors de la configuration de la base de données
    pause
    exit /b 1
)
echo ✅ Base de données configurée avec succès

REM Création du superutilisateur
echo.
echo [ÉTAPE 6] Création d'un superutilisateur (optionnel)
set /p CREATE_SUPERUSER="Voulez-vous créer un superutilisateur ? (y/N): "
if /i "!CREATE_SUPERUSER!"=="y" (
    venv\Scripts\python.exe manage.py createsuperuser
    if %errorlevel% equ 0 (
        echo ✅ Superutilisateur créé avec succès
    ) else (
        echo ⚠️  Erreur lors de la création du superutilisateur
    )
) else (
    echo ⚠️  Création du superutilisateur ignorée
)

REM Lancement du serveur
echo.
echo [ÉTAPE 7] Lancement du serveur de développement
echo ✅ Serveur en cours de lancement...
echo 🌐 L'application sera accessible sur : http://127.0.0.1:8000
echo 💡 Appuyez sur Ctrl+C pour arrêter le serveur
echo.

venv\Scripts\python.exe manage.py runserver

echo.
echo 👋 Serveur arrêté. Merci d'avoir utilisé Vizaur-EDA-Tool !
pause 