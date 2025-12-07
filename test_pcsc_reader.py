#!/usr/bin/env python3
"""
Script de test pour lecteur RFID PC/SC
Utilisez ce script pour découvrir l'UID de vos badges
"""
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from smartcard.System import readers
    from smartcard.util import toHexString
    from smartcard.Exceptions import NoCardException
except ImportError:
    print("❌ pyscard n'est pas installé!")
    print("   Installez-le avec: sudo apt install python3-pyscard")
    sys.exit(1)

def main():
    print("=" * 60)
    print("  Test Lecteur RFID PC/SC")
    print("=" * 60)
    print()
    
    # Lister les lecteurs
    try:
        r = readers()
        print(f"📡 {len(r)} lecteur(s) trouvé(s):")
        for i, reader in enumerate(r):
            print(f"   {i}: {reader}")
        print()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    if not r:
        print("❌ Aucun lecteur trouvé!")
        return
    
    # Utiliser le premier lecteur
    reader = r[0]
    print(f"🔍 Utilisation du lecteur: {reader}")
    print()
    print("💳 Présentez votre badge devant le lecteur...")
    print("   (Ctrl+C pour quitter)")
    print()
    
    last_uid = None
    
    try:
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
                    
                    # Afficher seulement si différent du dernier
                    if uid != last_uid:
                        print(f"✅ Badge détecté!")
                        print(f"   UID: {uid}")
                        print(f"   UID (brut): {toHexString(data)}")
                        print()
                        print(f"   → Ajoutez ce code dans config/employees.json:")
                        print(f'   "rfid": "{uid}"')
                        print()
                        last_uid = uid
                
                connection.disconnect()
                
            except NoCardException:
                # Pas de carte, attendre
                if last_uid is not None:
                    print("   Badge retiré")
                    print()
                    last_uid = None
                pass
            except Exception as e:
                # Ignorer les erreurs de connexion temporaires
                pass
            
            import time
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\n✓ Test terminé")

if __name__ == "__main__":
    main()



