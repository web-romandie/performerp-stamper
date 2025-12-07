#!/bin/bash
# Script simplifié pour trouver un Raspberry Pi (sans sudo)

echo "========================================="
echo "  Recherche de Raspberry Pi (simple)"
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
echo "⏳ Scan en cours (environ 30 secondes)..."
echo "   Appareils trouvés :"
echo ""

# Ping sweep simple (ne nécessite pas sudo)
count=0
for i in {1..254}; do
    {
        if ping -c 1 -W 1 -t 1 $NETWORK_PREFIX.$i &> /dev/null; then
            echo "   ✓ $NETWORK_PREFIX.$i"
            ((count++))
        fi
    } &
    
    # Limiter le nombre de processus parallèles
    if [ $(( i % 20 )) -eq 0 ]; then
        wait
    fi
done
wait

echo ""
echo "========================================="
echo "  $count appareil(s) trouvé(s)"
echo "========================================="
echo ""
echo "💡 Pour identifier votre Raspberry Pi :"
echo ""
echo "1. Testez chaque IP avec SSH :"
echo "   ssh pi@IP_TROUVEE"
echo "   (mot de passe par défaut : raspberry)"
echo ""
echo "2. OU consultez votre box Internet :"
echo "   - Swisscom : http://192.168.1.1"
echo "   - UPC/Sunrise : http://192.168.0.1"
echo "   - Cherchez 'raspberrypi' dans les appareils"
echo ""
echo "3. OU si vous avez accès au Raspberry Pi :"
echo "   - Connectez écran et clavier"
echo "   - Tapez : hostname -I"
echo ""



