#!/usr/bin/env python3
"""
Test simple de lecture de badges RFID
"""
import time
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import NoCardException, CardConnectionException

print("=" * 60)
print("TEST DE LECTURE RFID - ACR1252")
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
print("Utilisation du premier lecteur...")
reader = reader_list[0]

print()
print("🔍 En attente de badge... (Ctrl+C pour arrêter)")
print("   Placez votre badge sur le lecteur...")
print()

try:
    last_uid = None
    while True:
        try:
            # Créer une connexion
            connection = reader.createConnection()
            connection.connect()
            
            # Lire l'UID
            GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            data, sw1, sw2 = connection.transmit(GET_UID)
            
            if sw1 == 0x90 and sw2 == 0x00:
                uid = toHexString(data).replace(' ', '')
                
                # Afficher seulement si c'est un nouveau badge
                if uid != last_uid:
                    print(f"✅ BADGE DÉTECTÉ!")
                    print(f"   UID: {uid}")
                    print(f"   Données brutes: {data}")
                    print(f"   Statut: {sw1:02X} {sw2:02X}")
                    print()
                    last_uid = uid
            
            connection.disconnect()
            
        except NoCardException:
            # Pas de carte = normal
            if last_uid:
                print("   Badge retiré")
                last_uid = None
            pass
        
        except CardConnectionException as e:
            # Erreur de connexion
            pass
        
        time.sleep(0.2)
        
except KeyboardInterrupt:
    print("\n\n✓ Test terminé")
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    import traceback
    traceback.print_exc()


