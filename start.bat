@echo off
REM Script de démarrage pour Windows

echo ====================================
echo Système de Pointage RFID
echo ====================================
echo.

REM Détecter quelle commande Python utiliser
set PYTHON_CMD=

python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    goto :check_dependencies
)

py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=py
    goto :check_dependencies
)

python3 --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python3
    goto :check_dependencies
)

REM Aucune commande Python trouvée
echo ERREUR: Python n'est pas installé ou pas dans le PATH
echo.
echo SOLUTION:
echo 1. Téléchargez Python depuis https://www.python.org/downloads/
echo 2. Pendant l'installation, COCHEZ "Add Python to PATH"
echo 3. Relancez ce script
echo.
pause
exit /b 1

:check_dependencies
echo Python détecté: %PYTHON_CMD%
echo.

REM Vérifier si les dépendances sont installées
%PYTHON_CMD% -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo Installation des dépendances...
    echo.
    %PYTHON_CMD% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERREUR: Échec de l'installation des dépendances
        echo.
        echo SOLUTION: Lancez install_dependencies.bat
        echo Ou consultez DEPANNAGE_INSTALLATION.md
        echo.
        pause
        exit /b 1
    )
    echo.
    echo Dépendances installées avec succès!
    echo.
)

REM Vérifier si .env existe
if not exist ".env" (
    echo.
    echo Le fichier .env n'existe pas.
    echo Lancement de la configuration initiale...
    echo.
    %PYTHON_CMD% setup_env.py
    if errorlevel 1 (
        echo ERREUR: Échec de la configuration
        pause
        exit /b 1
    )
)

REM Lancer l'application
echo.
echo Démarrage de l'application...
echo.
%PYTHON_CMD% main.py

if errorlevel 1 (
    echo.
    echo ERREUR: L'application s'est terminée avec une erreur
    echo.
    echo Consultez logs\pointage.log pour plus de détails
    echo Ou lancez: %PYTHON_CMD% diagnostic.py
    echo.
    pause
)

