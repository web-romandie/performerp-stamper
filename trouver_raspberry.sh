#!/bin/bash
# Script pour trouver un Raspberry Pi sur le réseau

echo "========================================="
echo "  Recherche de Raspberry Pi"
echo "========================================="
echo ""

# Détecter l'IP locale
LOCAL_IP=$(ifconfig 2>/dev/null | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
if [ -z "$LOCAL_IP" ]; then
    # Essayer avec ip addr (Linux)
    LOCAL_IP=$(ip addr 2>/dev/null | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | cut -d'/' -f1 | head -1)
fi

NETWORK_PREFIX=$(echo $LOCAL_IP | cut -d. -f1-3)

if [ -z "$NETWORK_PREFIX" ]; then
    echo "❌ Impossible de détecter votre réseau local"
    echo "Veuillez vous assurer d'être connecté à un réseau"
    exit 1
fi

echo "📡 Votre IP locale : $LOCAL_IP"
echo "🔍 Recherche sur le réseau : $NETWORK_PREFIX.0/24"
echo ""

# Méthode 1 : Vérifier si nmap est disponible
if command -v nmap &> /dev/null; then
    echo "Méthode 1 : Scan avec nmap..."
    echo "----------------------------------------"
    sudo nmap -sn $NETWORK_PREFIX.0/24 | grep -B 2 -i "Raspberry\|B8:27:EB\|DC:A6:32\|E4:5F:01"
    echo ""
else
    echo "ℹ nmap non installé (optionnel)"
fi

# Méthode 2 : Vérifier si arp-scan est disponible
if command -v arp-scan &> /dev/null; then
    echo "Méthode 2 : Scan avec arp-scan..."
    echo "----------------------------------------"
    sudo arp-scan --localnet | grep -i "Raspberry\|b8:27:eb\|dc:a6:32\|e4:5f:01"
    echo ""
else
    echo "ℹ arp-scan non installé (optionnel)"
fi

# Méthode 3 : Ping sweep simple
echo "Méthode 3 : Ping sweep..."
echo "----------------------------------------"
echo "Scan en cours (cela peut prendre 1-2 minutes)..."
echo ""

for i in {1..254}; do
    ping -c 1 -W 1 $NETWORK_PREFIX.$i &> /dev/null && \
    echo "✓ Appareil trouvé : $NETWORK_PREFIX.$i" &
done
wait

echo ""
echo "========================================="
echo "  Méthodes Alternatives"
echo "========================================="
echo ""
echo "1. Via votre box Internet :"
echo "   - Connectez-vous à l'interface web de votre box"
echo "   - Consultez la liste des appareils connectés"
echo "   - Cherchez 'raspberrypi' ou 'Raspberry Pi'"
echo ""
echo "2. Avec Angry IP Scanner (Windows/Mac) :"
echo "   - Téléchargez depuis https://angryip.org/"
echo "   - Scannez votre réseau local"
echo "   - Cherchez un appareil avec hostname 'raspberrypi'"
echo ""
echo "3. Vérifier sur le Raspberry Pi directement :"
echo "   - Connectez écran et clavier au Raspberry Pi"
echo "   - Ouvrez un terminal"
echo "   - Tapez : hostname -I"
echo ""
echo "========================================="
echo "  Connexion SSH"
echo "========================================="
echo ""
echo "Une fois l'IP trouvée, connectez-vous :"
echo "   ssh pi@IP_DU_RASPBERRY"
echo "   (mot de passe par défaut : raspberry)"
echo ""
echo "Ensuite, consultez : INSTALLATION_RASPBERRY.md"
echo ""


