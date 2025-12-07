#!/bin/bash
# Script pour détecter correctement votre réseau local

echo "========================================="
echo "  Détection de votre réseau local"
echo "========================================="
echo ""

# Méthode 1 : Détecter toutes les interfaces
echo "📡 Vos interfaces réseau :"
echo "----------------------------------------"

# WiFi (en0 sur Mac)
WIFI_IP=$(ipconfig getifaddr en0 2>/dev/null)
if [ ! -z "$WIFI_IP" ]; then
    echo "✓ WiFi (en0) : $WIFI_IP"
fi

# Ethernet (en1 sur Mac)
ETH_IP=$(ipconfig getifaddr en1 2>/dev/null)
if [ ! -z "$ETH_IP" ]; then
    echo "✓ Ethernet (en1) : $ETH_IP"
fi

# Ethernet alternatif (en2)
ETH2_IP=$(ipconfig getifaddr en2 2>/dev/null)
if [ ! -z "$ETH2_IP" ]; then
    echo "✓ Ethernet (en2) : $ETH2_IP"
fi

# Thunderbolt/USB (en3, en4, en5)
for i in {3..5}; do
    USB_IP=$(ipconfig getifaddr en$i 2>/dev/null)
    if [ ! -z "$USB_IP" ]; then
        echo "✓ Interface en$i : $USB_IP"
    fi
done

echo ""
echo "🔍 Toutes vos adresses IP :"
echo "----------------------------------------"
ifconfig | grep "inet " | grep -v "127.0.0" | awk '{print "   " $2}'

echo ""
echo "========================================="
echo "  Votre passerelle (routeur/box)"
echo "========================================="
GATEWAY=$(netstat -nr | grep default | grep -v "utun\|awdl" | head -1 | awk '{print $2}')
if [ ! -z "$GATEWAY" ]; then
    echo "🌐 Adresse de votre box : $GATEWAY"
    echo ""
    echo "💡 Ouvrez votre navigateur et allez sur :"
    echo "   http://$GATEWAY"
else
    echo "⚠️  Passerelle non détectée"
fi

echo ""
echo "========================================="
echo "  Que faire maintenant ?"
echo "========================================="
echo ""
echo "OPTION 1 (Recommandée) - Via votre box :"
if [ ! -z "$GATEWAY" ]; then
    echo "   1. Ouvrez : http://$GATEWAY"
else
    echo "   1. Ouvrez : http://192.168.1.1 ou http://192.168.0.1"
fi
echo "   2. Connectez-vous (identifiants au dos de la box)"
echo "   3. Cherchez 'Appareils connectés' ou 'Réseau'"
echo "   4. Trouvez 'raspberrypi' et notez son IP"
echo ""
echo "OPTION 2 - Scan manuel :"
echo "   Si vous avez une IP ci-dessus (ex: 192.168.1.123),"
echo "   lancez le script de scan :"
echo "   ./trouver_raspberry_simple.sh"
echo ""
echo "OPTION 3 - Directement sur le Raspberry Pi :"
echo "   Connectez écran + clavier et tapez :"
echo "   hostname -I"
echo ""



