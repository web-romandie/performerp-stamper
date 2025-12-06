#!/bin/bash
# Installation de la dépendance requests pour la configuration RFID

echo "🔧 Installation de la configuration RFID..."
echo ""

# Activer l'environnement virtuel
if [ -d "venv" ]; then
    echo "✓ Activation de l'environnement virtuel..."
    source venv/bin/activate
else
    echo "❌ Environnement virtuel non trouvé !"
    echo "Veuillez d'abord installer l'application avec ./start.sh"
    exit 1
fi

# Installer requests
echo "📦 Installation de requests..."
pip install requests==2.31.0

echo ""
echo "✅ Installation terminée !"
echo ""
echo "📖 Documentation : voir CONFIGURATION_RFID.md"
echo ""
echo "Pour lancer l'application :"
echo "  ./start.sh"
echo ""

