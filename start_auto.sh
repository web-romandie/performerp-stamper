#!/bin/bash
# Script de démarrage automatique - détecte le type de lecteur

echo "===================================="
echo "Système de Pointage RFID"
echo "===================================="
echo ""

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv --system-site-packages
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier si les dépendances sont installées
python3 -c "import PyQt5" &> /dev/null
if [ $? -ne 0 ]; then
    echo "PyQt5 non trouvé. Installation des dépendances système..."
    echo "Veuillez exécuter d'abord : sudo apt-get install -y python3-pyqt5"
    echo "Ou lancez le script d'installation complet : ./install_raspberry.sh"
    exit 1
fi

# Installer les autres dépendances (sans PyQt5)
python3 -c "import serial" &> /dev/null
if [ $? -ne 0 ]; then
    echo "Installation des dépendances Python..."
    pip install pyserial python-dotenv schedule
fi

# Installer pyscard si nécessaire (optionnel pour PC/SC)
python3 -c "import pyscard" &> /dev/null
if [ $? -ne 0 ]; then
    echo "Installation de pyscard..."
    pip install pyscard
fi

# Détecter le type de lecteur
echo "Détection du lecteur RFID..."
python3 diagnostic_lecteur.py > /tmp/rfid_detection.txt 2>&1

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


