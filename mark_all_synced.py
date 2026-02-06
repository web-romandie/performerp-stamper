#!/usr/bin/env python3
"""
Script pour marquer tous les pointages existants comme synchronisés
Utile lors de la migration vers le nouveau système de synchronisation
"""

import sqlite3
import sys
from pathlib import Path

def mark_all_synced():
    """Marque tous les pointages comme déjà synchronisés"""
    
    # Chemin vers la base de données
    db_path = Path(__file__).parent / "data" / "pointage.db"
    
    if not db_path.exists():
        print(f"❌ Base de données non trouvée: {db_path}")
        sys.exit(1)
    
    print(f"📂 Base de données: {db_path}")
    print()
    
    # Connexion à la base
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Vérifier si la colonne synced existe
    cursor.execute("PRAGMA table_info(pointages)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'synced' not in columns:
        print("⚠️  La colonne 'synced' n'existe pas encore")
        print("   Elle sera créée au prochain démarrage de l'application")
        conn.close()
        sys.exit(0)
    
    # Compter les pointages non synchronisés
    cursor.execute("SELECT COUNT(*) FROM pointages WHERE synced = 0")
    unsynced_count = cursor.fetchone()[0]
    
    # Compter le total
    cursor.execute("SELECT COUNT(*) FROM pointages")
    total_count = cursor.fetchone()[0]
    
    print(f"📊 Pointages dans la base: {total_count}")
    print(f"   - Non synchronisés: {unsynced_count}")
    print(f"   - Déjà synchronisés: {total_count - unsynced_count}")
    print()
    
    if unsynced_count == 0:
        print("✅ Tous les pointages sont déjà marqués comme synchronisés!")
        conn.close()
        sys.exit(0)
    
    # Demander confirmation
    print(f"⚠️  Voulez-vous marquer les {unsynced_count} pointages comme synchronisés?")
    print("   Cela évitera qu'ils soient envoyés à l'API lors de la prochaine sync.")
    print()
    response = input("   Confirmer? (oui/non): ").strip().lower()
    
    if response not in ['oui', 'o', 'yes', 'y']:
        print("❌ Opération annulée")
        conn.close()
        sys.exit(0)
    
    # Marquer tous les pointages comme synchronisés
    cursor.execute("UPDATE pointages SET synced = 1 WHERE synced = 0")
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    
    print()
    print(f"✅ {updated} pointages marqués comme synchronisés!")
    print("   Ils ne seront plus envoyés vers l'API.")
    print()

if __name__ == "__main__":
    try:
        mark_all_synced()
    except KeyboardInterrupt:
        print("\n❌ Opération annulée par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)
