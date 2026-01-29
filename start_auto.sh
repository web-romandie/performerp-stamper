#!/bin/bash
# Script de démarrage automatique - détecte le type de lecteur

echo "===================================="
echo "Système de Pointage RFID"
echo "===================================="
echo ""

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Installer pyscard si nécessaire
python3 -c "import pyscard" &> /dev/null
if [ $? -ne 0 ]; then
    echo "Installation de pyscard..."
    pip install pyscard
fi

# Détecter le type de lecteur
echo "Détection du lecteur RFID..."
python3 diagnostic_lecteur.py > /tmp/rfid_detection.txt 2>&1

# Forcer l'utilisation de X11 au lieu de Wayland pour éviter les avertissements
export QT_QPA_PLATFORM=xcb

if grep -q "PC/SC" /tmp/rfid_detection.txt; then
    echo "✓ Lecteur PC/SC détecté (ACR1252)"
    echo "Lancement avec main_pcsc_auto.py"
    echo ""
    python3 main_pcsc_auto.py
elif grep -q "série" /tmp/rfid_detection.txt; then
    echo "✓ Lecteur série détecté"
    echo "Lancement avec main.py"
    echo ""
    python3 main.py
else
    echo "⚠️  Aucun lecteur détecté"
    echo "Vérifiez que votre lecteur RFID est bien connecté"
    echo ""
    cat /tmp/rfid_detection.txt
    exit 1
fi


