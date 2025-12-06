#!/bin/bash
# Script d'installation automatique pour Raspberry Pi

echo "========================================="
echo "  Installation - Système de Pointage"
echo "  Raspberry Pi"
echo "========================================="
echo ""

# Vérifier qu'on est bien sur un Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "⚠️  Avertissement : Ce script est conçu pour Raspberry Pi"
    echo "   Voulez-vous continuer quand même ? (o/N)"
    read -r response
    if [ "$response" != "o" ] && [ "$response" != "O" ]; then
        echo "Installation annulée"
        exit 0
    fi
fi

# Fonction pour afficher les étapes
step() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  $1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Étape 1 : Mise à jour du système
step "Étape 1/6 : Mise à jour du système"
echo "Cela peut prendre plusieurs minutes..."
sudo apt update
sudo apt upgrade -y

# Étape 2 : Installation de Python et dépendances système
step "Étape 2/6 : Installation de Python et outils"
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-pyqt5 \
    python3-serial \
    git \
    xvfb

# Étape 3 : Permissions pour le port série
step "Étape 3/6 : Configuration des permissions"
sudo usermod -a -G dialout $USER
echo "✓ Utilisateur ajouté au groupe dialout"

# Étape 4 : Installation des dépendances Python
step "Étape 4/6 : Installation des bibliothèques Python"

# Créer une version modifiée de requirements.txt sans PyQt5
# (car on utilise la version système)
if [ -f "requirements.txt" ]; then
    echo "Installation des dépendances..."
    
    # Installer python-dotenv et autres (sauf PyQt5)
    pip3 install python-dotenv
    pip3 install pyserial
    
    echo "✓ Dépendances installées"
else
    echo "⚠️  Fichier requirements.txt non trouvé"
    echo "   Installation manuelle des dépendances..."
    pip3 install python-dotenv pyserial
fi

# Étape 5 : Configuration
step "Étape 5/6 : Configuration de l'application"

if [ ! -f ".env" ]; then
    echo "Le fichier .env n'existe pas."
    echo "Voulez-vous lancer la configuration maintenant ? (o/N)"
    read -r response
    if [ "$response" = "o" ] || [ "$response" = "O" ]; then
        python3 setup_env.py
    else
        echo "ℹ️  Vous pourrez configurer plus tard avec : python3 setup_env.py"
    fi
else
    echo "✓ Fichier .env existe déjà"
fi

# Étape 6 : Diagnostic
step "Étape 6/6 : Vérification de l'installation"
python3 diagnostic.py

# Résumé
echo ""
echo "========================================="
echo "  Installation Terminée !"
echo "========================================="
echo ""
echo "📋 Prochaines étapes :"
echo ""
echo "1. Configurez vos employés :"
echo "   nano config/employees.json"
echo ""
echo "2. Testez l'application :"
echo "   python3 test_rfid_simulator.py"
echo ""
echo "3. Lancez l'application :"
echo "   python3 main.py"
echo ""
echo "4. Pour le démarrage automatique :"
echo "   Consultez : INSTALLATION_RASPBERRY.md"
echo "   Section 'Lancement Automatique au Démarrage'"
echo ""
echo "⚠️  IMPORTANT : Déconnectez-vous et reconnectez-vous"
echo "   pour que les permissions du port série soient actives :"
echo "   exit"
echo "   puis reconnectez-vous en SSH"
echo ""
echo "📖 Documentation : INSTALLATION_RASPBERRY.md"
echo ""


