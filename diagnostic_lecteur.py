#!/usr/bin/env python3
"""
Diagnostic rapide du lecteur RFID
"""
import sys

print("=" * 60)
print("DIAGNOSTIC LECTEUR RFID")
print("=" * 60)
print()

# Test 1: Lecteurs PC/SC (ACR1252, etc.)
print("1. Recherche de lecteurs PC/SC...")
try:
    from smartcard.System import readers
    reader_list = readers()
    if reader_list:
        print(f"   ✅ {len(reader_list)} lecteur(s) PC/SC détecté(s):")
        for i, reader in enumerate(reader_list):
            print(f"      {i+1}. {reader}")
        print()
        print("   👉 Votre lecteur est un lecteur PC/SC")
        print("   👉 Utilisez: python3 main_pcsc_auto.py")
        sys.exit(0)
    else:
        print("   ❌ Aucun lecteur PC/SC détecté")
except ImportError:
    print("   ⚠️  Module pyscard non installé")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

print()

# Test 2: Ports série (lecteurs série classiques)
print("2. Recherche de ports série...")
try:
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    
    if ports:
        print(f"   ✅ {len(ports)} port(s) série détecté(s):")
        for port in ports:
            print(f"      - {port.device}")
            print(f"        Description: {port.description}")
            print(f"        HWID: {port.hwid}")
            print()
        
        # Filtrer les ports non pertinents
        real_ports = [p for p in ports if 'debug' not in p.device.lower() and 'bluetooth' not in p.device.lower()]
        
        if real_ports:
            print(f"   👉 {len(real_ports)} port(s) utilisable(s) pour lecteur série")
            print(f"   👉 Essayez: python3 main.py")
            print(f"   👉 Ou configurez RFID_PORT={real_ports[0].device} dans .env")
        else:
            print("   ⚠️  Aucun port série réel détecté")
    else:
        print("   ❌ Aucun port série détecté")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")

print()
print("=" * 60)
print("RÉSUMÉ:")
print("  - Si vous avez un ACR1252 ou lecteur USB NFC: main_pcsc_auto.py")
print("  - Si vous avez un lecteur série classique: main.py")
print("=" * 60)

