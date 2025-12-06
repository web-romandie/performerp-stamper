"""
Point d'entrée principal du système de pointage RFID
"""
import sys
import logging
from pathlib import Path
from PyQt5.QtWidgets import QApplication

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from src.database import DatabaseManager
from src.gui import MainWindow

# Auto-détection du type de lecteur RFID
def get_rfid_reader():
    """Détecte et retourne le bon type de lecteur RFID"""
    try:
        # Essayer d'abord PC/SC (pour ACR1252 et lecteurs smart card)
        from smartcard.System import readers as pcsc_readers
        if pcsc_readers():
            from src.rfid.reader_pcsc import RFIDReaderPCSC
            print("✓ Lecteur PC/SC détecté (ACR1252)")
            return RFIDReaderPCSC()
    except ImportError:
        pass
    except Exception as e:
        print(f"PC/SC non disponible: {e}")
    
    # Sinon, utiliser le lecteur série classique
    try:
        from src.rfid import RFIDReader
        print("✓ Utilisation du lecteur série")
        return RFIDReader(
            port=settings.RFID_PORT,
            baudrate=settings.RFID_BAUDRATE,
            timeout=settings.RFID_TIMEOUT
        )
    except Exception as e:
        print(f"Erreur création lecteur série: {e}")
        raise


def setup_logging():
    """Configure le système de logging"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Logger principal
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Handler fichier
    file_handler = logging.FileHandler(settings.LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)
    
    # Handler console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)
    
    logger.info("=" * 50)
    logger.info("Démarrage du système de pointage")
    logger.info("=" * 50)


def check_configuration():
    """Vérifie que la configuration est correcte"""
    issues = []
    
    # Vérifier que le fichier .env existe
    env_file = settings.BASE_DIR / ".env"
    if not env_file.exists():
        issues.append("Le fichier .env n'existe pas. Copiez .env.example vers .env et configurez-le.")
    
    # Vérifier que le fichier des employés existe
    if not settings.EMPLOYEES_FILE.exists():
        issues.append(f"Le fichier des employés n'existe pas: {settings.EMPLOYEES_FILE}")
    
    # Avertissements (non bloquants)
    warnings = []
    if not settings.FTP_HOST:
        warnings.append("Configuration FTP non définie. L'export automatique ne fonctionnera pas.")
    
    return issues, warnings


def main():
    """Fonction principale"""
    # Configuration du logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Vérification de la configuration
    issues, warnings = check_configuration()
    
    if issues:
        logger.error("Problèmes de configuration détectés:")
        for issue in issues:
            logger.error(f"  - {issue}")
        logger.error("Arrêt de l'application")
        return 1
    
    if warnings:
        logger.warning("Avertissements de configuration:")
        for warning in warnings:
            logger.warning(f"  - {warning}")
    
    try:
        # Initialiser la base de données
        logger.info(f"Initialisation de la base de données: {settings.DATABASE_PATH}")
        db_manager = DatabaseManager(str(settings.DATABASE_PATH))
        
        # Initialiser le lecteur RFID (auto-détection)
        logger.info("Initialisation du lecteur RFID")
        rfid_reader = get_rfid_reader()
        
        # Connecter le lecteur RFID
        if not rfid_reader.connect():
            logger.error("Impossible de connecter au lecteur RFID")
            return 1
        logger.info("Lecteur RFID connecté avec succès")
        
        # Créer l'application Qt
        app = QApplication(sys.argv)
        app.setApplicationName(settings.WINDOW_TITLE)
        
        # Créer la fenêtre principale
        window = MainWindow(db_manager, rfid_reader, settings.EMPLOYEES_FILE)
        
        if settings.FULLSCREEN:
            window.showFullScreen()
        else:
            window.show()
        
        logger.info("Interface graphique lancée")
        
        # Lancer l'application
        return app.exec_()
        
    except Exception as e:
        logger.exception(f"Erreur fatale: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())


