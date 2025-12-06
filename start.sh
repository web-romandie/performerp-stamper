#!/bin/bash
# Script de démarrage pour macOS/Linux

echo "===================================="
echo "Système de Pointage RFID"
echo "===================================="
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "ERREUR: Python 3 n'est pas installé"
    echo "Veuillez installer Python 3.8 ou supérieur"
    exit 1
fi

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERREUR: Échec de la création de l'environnement virtuel"
        exit 1
    fi
fi

# Activer l'environnement virtuel
echo "Activation de l'environnement virtuel..."
source venv/bin/activate

# Vérifier si les dépendances sont installées
python3 -c "import PyQt5" &> /dev/null
if [ $? -ne 0 ]; then
    echo "Installation des dépendances..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERREUR: Échec de l'installation des dépendances"
        exit 1
    fi
fi

# Vérifier si .env existe
if [ ! -f ".env" ]; then
    echo ""
    echo "Le fichier .env n'existe pas."
    echo "Lancement de la configuration initiale..."
    echo ""
    python3 setup_env.py
    if [ $? -ne 0 ]; then
        echo "ERREUR: Échec de la configuration"
        exit 1
    fi
fi

# Lancer l'application
echo ""
echo "Démarrage de l'application..."
echo ""
python3 main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERREUR: L'application s'est terminée avec une erreur"
    read -p "Appuyez sur Entrée pour continuer..."
fi



