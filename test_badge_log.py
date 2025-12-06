#!/usr/bin/env python3
"""
Test avec log dans fichier
"""
import time
import sys
from datetime import datetime
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import NoCardException, CardConnectionException
from smartcard.CardMonitoring import CardMonitor, CardObserver

LOG_FILE = "test_badge.log"

def log(message):
    """Écrit dans le fichier et stdout"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    full_msg = f"[{timestamp}] {message}"
    print(full_msg, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(full_msg + "\n")

# Vider le log
with open(LOG_FILE, 'w') as f:
    f.write("")

log("=" * 60)
log("TEST CONTINU - DÉTECTION DE BADGES")
log("=" * 60)

# Lister les lecteurs
reader_list = readers()
if not reader_list:
    log("❌ Aucun lecteur détecté!")
    sys.exit(1)

log(f"✓ {len(reader_list)} lecteur(s) détecté(s):")
for i, reader in enumerate(reader_list):
    log(f"  {i+1}. {reader}")

log("")
log("🔍 En attente de badges... (log dans test_badge.log)")
log("   Passez votre badge sur le lecteur")
log("")

class PrintObserver(CardObserver):
    """Observer qui affiche quand une carte est insérée/retirée"""
    
    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            log("")
            log("✅ *** CARTE INSÉRÉE! ***")
            log(f"   ATR: {toHexString(card.atr)}")
            log(f"   Lecteur: {card.reader}")
            
            # Essayer de lire l'UID
            try:
                connection = card.createConnection()
                connection.connect()
                
                GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
                data, sw1, sw2 = connection.transmit(GET_UID)
                
                if sw1 == 0x90 and sw2 == 0x00:
                    uid = toHexString(data).replace(' ', '')
                    log(f"   UID: {uid}")
                    log(f"   *** C'EST CE CODE QUI DOIT ÊTRE DANS employees.json ***")
                else:
                    log(f"   Erreur lecture UID: {sw1:02X} {sw2:02X}")
                
                connection.disconnect()
            except Exception as e:
                log(f"   Erreur: {e}")
        
        for card in removedcards:
            log(f"❌ CARTE RETIRÉE")

# Démarrer le monitoring
cardmonitor = CardMonitor()
cardobserver = PrintObserver()
cardmonitor.addObserver(cardobserver)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    log("")
    log("✓ Test terminé")
    cardmonitor.deleteObserver(cardobserver)

