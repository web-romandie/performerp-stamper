#!/bin/bash
# Script d'installation directe sur Raspberry Pi
# À copier-coller dans le terminal du Raspberry Pi

echo "========================================="
echo "  Installation Système de Pointage"
echo "  Raspberry Pi - Installation Directe"
echo "========================================="
echo ""

# Créer la structure
mkdir -p ~/timbrage/{config,src/{gui,rfid,database,export},data,logs,exports}
cd ~/timbrage

# Mise à jour système
echo "Mise à jour du système..."
sudo apt update
sudo apt upgrade -y

# Installation des dépendances
echo "Installation des dépendances..."
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-pyqt5 \
    python3-serial \
    git

# Installation des packages Python
echo "Installation des packages Python..."
pip3 install python-dotenv

# Permissions pour le port série
sudo usermod -a -G dialout $USER

echo ""
echo "========================================="
echo "  Installation Terminée !"
echo "========================================="
echo ""
echo "IMPORTANT : Les fichiers Python doivent être"
echo "ajoutés manuellement dans ~/timbrage/"
echo ""
echo "Déconnectez-vous et reconnectez-vous pour"
echo "activer les permissions du port série."
echo ""


