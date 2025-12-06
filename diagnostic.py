"""
Script de diagnostic du système de pointage
Vérifie que tous les prérequis sont en place

Utilisation: python diagnostic.py
"""
import sys
import os
from pathlib import Path

def print_header(text):
    """Affiche un en-tête"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

def print_check(condition, success_msg, fail_msg):
    """Affiche le résultat d'une vérification"""
    if condition:
        print(f"✓ {success_msg}")
        return True
    else:
        print(f"✗ {fail_msg}")
        return False

def check_python_version():
    """Vérifie la version de Python"""
    version = sys.version_info
    required = (3, 8)
    
    condition = version >= required
    success = f"Python {version.major}.{version.minor}.{version.micro}"
    fail = f"Python {version.major}.{version.minor} (requis: {required[0]}.{required[1]}+)"
    
    return print_check(condition, success, fail)

def check_module(module_name, package_name=None):
    """Vérifie qu'un module Python est installé"""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        return print_check(True, f"{package_name} installé", f"{package_name} manquant")
    except ImportError:
        return print_check(False, f"{package_name} installé", 
                          f"{package_name} manquant (pip install {package_name})")

def check_file_exists(filepath, description):
    """Vérifie qu'un fichier existe"""
    path = Path(filepath)
    exists = path.exists()
    
    return print_check(exists, 
                      f"{description}: {path.name}",
                      f"{description} manquant: {filepath}")

def check_directory_writable(dirpath, description):
    """Vérifie qu'un répertoire est accessible en écriture"""
    path = Path(dirpath)
    
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    
    writable = os.access(path, os.W_OK)
    
    return print_check(writable,
                      f"{description} accessible: {dirpath}",
                      f"{description} non accessible: {dirpath}")

def check_rfid_ports():
    """Liste les ports série disponibles"""
    print("\nPorts série disponibles:")
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        
        if ports:
            for port in ports:
                print(f"  - {port.device}: {port.description}")
            return True
        else:
            print("  Aucun port série détecté")
            return False
    except ImportError:
        print("  ✗ Module pyserial non installé")
        return False
    except Exception as e:
        print(f"  ✗ Erreur: {e}")
        return False

def check_database():
    """Vérifie la base de données"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from config import settings
        from src.database import DatabaseManager
        
        db_path = settings.DATABASE_PATH
        
        if db_path.exists():
            print(f"✓ Base de données existe: {db_path}")
        else:
            print(f"ℹ Base de données sera créée: {db_path}")
        
        # Tester la connexion
        db = DatabaseManager(str(db_path))
        
        # Compter les pointages
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM pointages")
        count = cursor.fetchone()[0]
        conn.close()
        
        print(f"  Pointages enregistrés: {count}")
        return True
        
    except Exception as e:
        print(f"✗ Erreur base de données: {e}")
        return False

def check_config():
    """Vérifie la configuration"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from config import settings
        import json
        
        issues = []
        warnings = []
        
        # Vérifier .env
        env_file = settings.BASE_DIR / ".env"
        if not env_file.exists():
            issues.append("Fichier .env manquant")
        else:
            print("✓ Fichier .env existe")
        
        # Vérifier employees.json
        if not settings.EMPLOYEES_FILE.exists():
            issues.append(f"Fichier {settings.EMPLOYEES_FILE} manquant")
        else:
            with open(settings.EMPLOYEES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                num_employees = len(data.get('employees', []))
                print(f"✓ Fichier employés: {num_employees} employé(s) configuré(s)")
        
        # Vérifier config FTP
        if not settings.FTP_HOST:
            warnings.append("Configuration FTP non définie")
        else:
            print(f"✓ FTP configuré: {settings.FTP_HOST}")
        
        # Afficher les issues
        if issues:
            print("\nProblèmes de configuration:")
            for issue in issues:
                print(f"  ✗ {issue}")
        
        if warnings:
            print("\nAvertissements:")
            for warning in warnings:
                print(f"  ⚠ {warning}")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"✗ Erreur configuration: {e}")
        return False

def main():
    """Fonction principale"""
    print_header("DIAGNOSTIC DU SYSTÈME DE POINTAGE")
    
    all_ok = True
    
    # Vérifier Python
    print_header("1. VERSION PYTHON")
    all_ok &= check_python_version()
    
    # Vérifier les modules
    print_header("2. DÉPENDANCES PYTHON")
    all_ok &= check_module("PyQt5")
    all_ok &= check_module("serial", "pyserial")
    all_ok &= check_module("dotenv", "python-dotenv")
    
    # Vérifier les fichiers
    print_header("3. FICHIERS REQUIS")
    base_dir = Path(__file__).parent
    all_ok &= check_file_exists(base_dir / "main.py", "Fichier principal")
    all_ok &= check_file_exists(base_dir / "config" / "employees.json", "Fichier employés")
    
    env_exists = check_file_exists(base_dir / ".env", "Fichier configuration")
    if not env_exists:
        print("  → Lancez 'python setup_env.py' pour configurer")
    all_ok &= env_exists
    
    # Vérifier les répertoires
    print_header("4. RÉPERTOIRES")
    all_ok &= check_directory_writable(base_dir / "data", "Répertoire données")
    all_ok &= check_directory_writable(base_dir / "logs", "Répertoire logs")
    all_ok &= check_directory_writable(base_dir / "exports", "Répertoire exports")
    
    # Vérifier les ports RFID
    print_header("5. LECTEUR RFID")
    check_rfid_ports()
    
    # Vérifier la base de données
    print_header("6. BASE DE DONNÉES")
    check_database()
    
    # Vérifier la configuration
    print_header("7. CONFIGURATION")
    all_ok &= check_config()
    
    # Résumé
    print_header("RÉSUMÉ")
    
    if all_ok:
        print("✓ Tous les prérequis sont en place")
        print("\nVous pouvez lancer l'application avec:")
        print("  - Windows: start.bat")
        print("  - macOS/Linux: ./start.sh")
        print("  - Ou directement: python main.py")
        print("\nPour tester sans lecteur RFID:")
        print("  python test_rfid_simulator.py")
    else:
        print("✗ Certains prérequis sont manquants")
        print("\nActions recommandées:")
        print("  1. Installez les dépendances: pip install -r requirements.txt")
        print("  2. Configurez l'application: python setup_env.py")
        print("  3. Relancez ce diagnostic: python diagnostic.py")
    
    print("\n" + "=" * 60)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n✗ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)



