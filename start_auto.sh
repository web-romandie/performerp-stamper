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

# Forcer l'utilisation de X11 au lieu de Wayland pour éviter les avertissements
export QT_QPA_PLATFORM=xcb

# Vérifier si pcscd est actif (service PC/SC)
if systemctl is-active --quiet pcscd; then
    echo "✓ Lecteur PC/SC détecté (service pcscd actif)"
    echo "Lancement avec main_pcsc_auto.py"
    echo ""
    python3 main_pcsc_auto.py
else
    echo "⚠️  Service PC/SC (pcscd) non actif"
    echo "Démarrage du service..."
    sudo systemctl start pcscd
    sleep 2
    echo "✓ Lancement de l'application"
    echo ""
    python3 main_pcsc_auto.py
fi


