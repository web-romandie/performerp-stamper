#!/usr/bin/env python3
"""
Test continu - mode interactif
"""
import time
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import NoCardException, CardConnectionException
from smartcard.CardMonitoring import CardMonitor, CardObserver

print("=" * 60)
print("TEST CONTINU - DÉTECTION DE BADGES")
print("=" * 60)
print()

# Lister les lecteurs
reader_list = readers()
if not reader_list:
    print("❌ Aucun lecteur détecté!")
    exit(1)

print(f"✓ {len(reader_list)} lecteur(s) détecté(s):")
for i, reader in enumerate(reader_list):
    print(f"  {i+1}. {reader}")

print()
print("=" * 60)
print("MODE 1: Détection d'insertion/retrait de carte")
print("=" * 60)

class PrintObserver(CardObserver):
    """Observer qui affiche quand une carte est insérée/retirée"""
    
    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            print(f"\n✅ CARTE INSÉRÉE!")
            print(f"   ATR: {toHexString(card.atr)}")
            print(f"   Lecteur: {card.reader}")
            
            # Essayer de lire l'UID
            try:
                connection = card.createConnection()
                connection.connect()
                
                GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
                data, sw1, sw2 = connection.transmit(GET_UID)
                
                if sw1 == 0x90 and sw2 == 0x00:
                    uid = toHexString(data).replace(' ', '')
                    print(f"   UID: {uid}")
                else:
                    print(f"   Erreur lecture UID: {sw1:02X} {sw2:02X}")
                
                connection.disconnect()
            except Exception as e:
                print(f"   Erreur: {e}")
        
        for card in removedcards:
            print(f"\n❌ CARTE RETIRÉE de {card.reader}")

# Démarrer le monitoring
print("\n🔍 En attente de badges...")
print("   Passez votre badge sur le lecteur")
print("   Appuyez sur Ctrl+C pour arrêter\n")

cardmonitor = CardMonitor()
cardobserver = PrintObserver()
cardmonitor.addObserver(cardobserver)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\n✓ Test terminé")
    cardmonitor.deleteObserver(cardobserver)

