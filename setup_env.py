"""
Script d'aide à la configuration initiale
"""
import shutil
from pathlib import Path


def setup_environment():
    """Configure l'environnement pour la première utilisation"""
    base_dir = Path(__file__).parent
    
    print("=" * 60)
    print("Configuration du Système de Pointage RFID")
    print("=" * 60)
    print()
    
    # Vérifier et créer .env
    env_file = base_dir / ".env"
    env_example = base_dir / ".env.example"
    
    if env_file.exists():
        print("✓ Le fichier .env existe déjà")
        overwrite = input("  Voulez-vous le remplacer? (o/N): ").lower()
        if overwrite != 'o':
            print("  Conservé")
        else:
            create_env_file(env_example, env_file)
    else:
        print("Création du fichier .env...")
        create_env_file(env_example, env_file)
    
    print()
    print("=" * 60)
    print("Configuration terminée!")
    print("=" * 60)
    print()
    print("Prochaines étapes:")
    print("1. Éditez le fichier .env avec vos paramètres FTP")
    print("2. Configurez vos employés dans config/employees.json")
    print("3. Connectez votre lecteur RFID")
    print("4. Lancez l'application avec: python main.py")
    print()


def create_env_file(source, destination):
    """Crée le fichier .env à partir de l'exemple"""
    # Copier le fichier exemple
    shutil.copy(source, destination)
    
    print("✓ Fichier .env créé")
    print()
    print("Veuillez configurer les paramètres suivants dans .env:")
    
    # Demander les paramètres FTP
    print("\n--- Configuration FTP ---")
    ftp_host = input("Hôte FTP (ex: ftp.example.com): ").strip()
    ftp_port = input("Port FTP (par défaut: 21): ").strip() or "21"
    ftp_user = input("Nom d'utilisateur FTP: ").strip()
    ftp_password = input("Mot de passe FTP: ").strip()
    ftp_path = input("Chemin distant (par défaut: /pointage): ").strip() or "/pointage"
    
    print("\n--- Configuration générale ---")
    company_name = input("Nom de l'entreprise: ").strip() or "Votre Entreprise"
    
    # Écrire dans le fichier
    with open(destination, 'w', encoding='utf-8') as f:
        f.write("# Configuration FTP\n")
        f.write(f"FTP_HOST={ftp_host}\n")
        f.write(f"FTP_PORT={ftp_port}\n")
        f.write(f"FTP_USER={ftp_user}\n")
        f.write(f"FTP_PASSWORD={ftp_password}\n")
        f.write(f"FTP_REMOTE_PATH={ftp_path}\n")
        f.write("\n")
        f.write("# Configuration générale\n")
        f.write(f"COMPANY_NAME={company_name}\n")
        f.write("AUTO_EXPORT_INTERVAL=3600\n")
        f.write("DEBUG_MODE=False\n")
        f.write("\n")
        f.write("# Configuration RFID\n")
        f.write("RFID_PORT=\n")
        f.write("RFID_BAUDRATE=9600\n")
        f.write("RFID_TIMEOUT=1.0\n")
        f.write("\n")
        f.write("# Interface\n")
        f.write("FULLSCREEN=False\n")
    
    print("\n✓ Configuration enregistrée")


if __name__ == "__main__":
    setup_environment()




