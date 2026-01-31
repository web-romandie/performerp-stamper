"""
Configuration de l'application de pointage
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Chemins
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
EXPORTS_DIR = BASE_DIR / "exports"
CONFIG_DIR = BASE_DIR / "config"

# Créer les dossiers s'ils n'existent pas
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)

# Base de données
DATABASE_PATH = DATA_DIR / "pointage.db"

# Fichier des employés
EMPLOYEES_FILE = CONFIG_DIR / "employees.json"

# Configuration FTP
FTP_HOST = os.getenv("FTP_HOST", "")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER", "")
FTP_PASSWORD = os.getenv("FTP_PASSWORD", "")
FTP_REMOTE_PATH = os.getenv("FTP_REMOTE_PATH", "/pointage")

# Configuration générale
COMPANY_NAME = os.getenv("COMPANY_NAME", "Entreprise")
AUTO_EXPORT_INTERVAL = int(os.getenv("AUTO_EXPORT_INTERVAL", "3600"))  # en secondes
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# Configuration RFID
RFID_PORT = os.getenv("RFID_PORT", "")  # Laissez vide pour auto-détection
RFID_BAUDRATE = int(os.getenv("RFID_BAUDRATE", "9600"))
RFID_TIMEOUT = float(os.getenv("RFID_TIMEOUT", "1.0"))

# Synchronisation automatique des employés (employees.json) depuis l'API
# 0 = désactivée, sinon intervalle en secondes (ex: 1800 = 30 min, 3600 = 1 h)
EMPLOYEES_SYNC_INTERVAL = int(os.getenv("EMPLOYEES_SYNC_INTERVAL", "0"))

# Configuration de l'interface
WINDOW_TITLE = f"Système de Pointage - {COMPANY_NAME}"
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 600
FULLSCREEN = os.getenv("FULLSCREEN", "False").lower() == "true"
SIMPLE_MODE = os.getenv("SIMPLE_MODE", "False").lower() == "true"

# Logs
LOG_FILE = LOGS_DIR / "pointage.log"
LOG_LEVEL = "DEBUG" if DEBUG_MODE else "INFO"




