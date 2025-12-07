@echo off
REM Script d'installation automatique des dépendances
REM Ce script gère les différentes configurations de Python sur Windows

echo ====================================
echo Installation des Dependances
echo ====================================
echo.

REM Tester si Python est disponible
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo Python detecte: python
    set PYTHON_CMD=python
    goto :install
)

REM Tester py (lanceur Python Windows)
py --version >nul 2>&1
if %errorlevel% == 0 (
    echo Python detecte: py
    set PYTHON_CMD=py
    goto :install
)

REM Tester python3
python3 --version >nul 2>&1
if %errorlevel% == 0 (
    echo Python detecte: python3
    set PYTHON_CMD=python3
    goto :install
)

REM Aucune commande Python trouvée
echo.
echo ERREUR: Python n'est pas installe ou pas dans le PATH
echo.
echo SOLUTION:
echo 1. Telechargez Python depuis https://www.python.org/downloads/
echo 2. Pendant l'installation, COCHEZ "Add Python to PATH"
echo 3. Relancez ce script
echo.
pause
exit /b 1

:install
echo.
echo Installation en cours...
echo.

REM Installer les dépendances
%PYTHON_CMD% -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo.
    echo ERREUR: Impossible de mettre a jour pip
    echo Tentative d'installation quand meme...
    echo.
)

%PYTHON_CMD% -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ERREUR: L'installation des dependances a echoue
    echo.
    echo SOLUTIONS:
    echo - Verifiez votre connexion Internet
    echo - Lancez ce script en tant qu'administrateur
    echo - Installez manuellement: %PYTHON_CMD% -m pip install PyQt5 pyserial python-dotenv
    echo.
    pause
    exit /b 1
)

echo.
echo ====================================
echo Installation reussie!
echo ====================================
echo.
echo Toutes les dependances sont installees.
echo Vous pouvez maintenant lancer l'application.
echo.
pause




