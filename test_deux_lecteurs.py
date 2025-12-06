#!/usr/bin/env python3
"""
Test des deux lecteurs (SAM et PICC) pour trouver le bon
"""
import time
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import NoCardException, CardConnectionException

print("=" * 60)
print("TEST DES DEUX LECTEURS ACR1252")
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
print("🔍 Test de CHAQUE lecteur...")
print("   Placez votre badge sur le lecteur et maintenez-le...")
print()

# Tester chaque lecteur
for reader_index, reader in enumerate(reader_list):
    print(f"\n📡 Test du lecteur {reader_index + 1}: {reader}")
    print("   En attente de badge (5 secondes)...")
    
    detected = False
    start_time = time.time()
    
    while time.time() - start_time < 5:
        try:
            connection = reader.createConnection()
            connection.connect()
            
            GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            data, sw1, sw2 = connection.transmit(GET_UID)
            
            if sw1 == 0x90 and sw2 == 0x00:
                uid = toHexString(data).replace(' ', '')
                print(f"\n   ✅ BADGE DÉTECTÉ sur lecteur {reader_index + 1}!")
                print(f"   UID: {uid}")
                print(f"   Données: {data}")
                detected = True
                connection.disconnect()
                break
            
            connection.disconnect()
            
        except NoCardException:
            pass
        except CardConnectionException:
            pass
        except Exception as e:
            print(f"   ⚠️  Erreur: {e}")
        
        time.sleep(0.3)
    
    if not detected:
        print(f"   ❌ Aucun badge détecté sur lecteur {reader_index + 1}")

print("\n" + "=" * 60)
print("Test terminé!")
print("=" * 60)

