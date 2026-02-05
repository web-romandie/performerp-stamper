"""
Interface moderne de pointage - Version horizontale
Inspirée de l'application Tipee avec un design épuré et intuitif
"""

import csv
import json
import logging
from datetime import datetime, time
from pathlib import Path

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame, QGridLayout, QApplication, QLineEdit, 
                             QDialog, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap, QIcon, QImage, QPainter

# Import optionnel pour le support SVG (rendu en pixmap pour éviter plantage sur Raspberry)
try:
    from PyQt5.QtSvg import QSvgRenderer
    SVG_AVAILABLE = True
except ImportError:
    SVG_AVAILABLE = False
    QSvgRenderer = None

logger = logging.getLogger(__name__)
if not SVG_AVAILABLE:
    logger.warning("PyQt5.QtSvg non disponible - support SVG désactivé")


def _svg_to_pixmap(svg_path: Path, height_px: int):
    """
    Rend le SVG en QPixmap une seule fois (sans QSvgWidget).
    Évite les plantages sur Raspberry tout en gardant la qualité vectorielle.
    Retourne None en cas d'échec.
    """
    if not SVG_AVAILABLE or not svg_path.exists():
        return None
    try:
        renderer = QSvgRenderer(str(svg_path))
        if not renderer.isValid():
            return None
        default_size = renderer.defaultSize()
        if default_size.height() <= 0:
            return None
        ratio = default_size.width() / default_size.height()
        width = int(height_px * ratio)
        image = QImage(width, height_px, QImage.Format_ARGB32)
        image.fill(0)
        painter = QPainter(image)
        renderer.render(painter)
        painter.end()
        return QPixmap.fromImage(image)
    except Exception as e:
        logger.warning(f"Rendu SVG échoué ({svg_path.name}): {e}")
        return None

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from config import settings


class RFIDSignal(QObject):
    """Signal pour la détection de carte RFID"""
    card_detected = pyqtSignal(str)


class MainWindow(QMainWindow):
    """Fenêtre principale moderne de l'application de timbrage"""
    
    def __init__(self, db_manager, rfid_reader, employees_file, parent=None):
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.rfid_reader = rfid_reader
        self.employees_file = Path(employees_file)
        self.employees = self.load_employees()
        # Afficher le bouton Admin seulement s'il n'y a aucun utilisateur de rang 1 (accès admin par code)
        self.show_admin_on_start = not self._has_rank1_employee()
        if self.show_admin_on_start:
            logger.info("Aucun employé rang 1 - bouton Administration affiché (accès par code)")
        
        # Configuration API (chargée depuis config/api_config.py)
        try:
            from config import api_config
            self.api_url = api_config.API_URL
            self.id_compte = api_config.ACCOUNT_ID
            self.api_key = api_config.API_KEY
            logger.info(f"Configuration API chargée: {self.api_url}, compte {self.id_compte}")
        except ImportError as e:
            logger.error("ERREUR CRITIQUE: Fichier config/api_config.py manquant!")
            logger.error("Copiez config/api_config.example.py vers config/api_config.py")
            logger.error("et configurez votre URL API, ID compte et clé API")
            raise RuntimeError("Configuration API manquante. L'application ne peut pas démarrer.") from e
        
        
        # État de l'application
        self.current_employee = None
        self.current_rfid = None
        self.is_card_present = False
        self.dashboard_data = None
        self.data_fetch_timer = None
        self.delayed_fetch_timer = None  # Timer pour le chargement différé
        self.is_processing = False  # Flag pour éviter les détections multiples
        self.consultation_mode = False  # Mode consultation (badge maintenu 5s)
        self.badge_detection_time = None  # Timestamp de la détection du badge
        
        # Signal pour la lecture RFID
        self.rfid_signal = RFIDSignal()
        self.rfid_signal.card_detected.connect(self.on_card_detected)
        
        self.default_instruction = self._get_ephemeride_du_jour() or "Présentez votre badge RFID"
        self.init_ui()
        self.start_rfid_reading()
        
        # Timer pour l'horloge
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        
        # Timer pour vérifier si la carte est toujours présente
        self.card_check_timer = QTimer()
        self.card_check_timer.timeout.connect(self.check_card_presence)
        self.card_check_timer.start(2000)  # Vérifier toutes les 2 secondes
        
        # Synchronisation automatique des employés depuis l'API (optionnel)
        self.employees_sync_timer = None
        if getattr(settings, 'EMPLOYEES_SYNC_INTERVAL', 0) > 0:
            interval_ms = settings.EMPLOYEES_SYNC_INTERVAL * 1000
            self.employees_sync_timer = QTimer()
            self.employees_sync_timer.timeout.connect(self.sync_employees_from_api)
            self.employees_sync_timer.start(interval_ms)
            logger.info(f"Synchronisation automatique employés activée (toutes les {settings.EMPLOYEES_SYNC_INTERVAL}s)")
            QTimer.singleShot(5000, self.sync_employees_from_api)  # Premier sync 5 s après démarrage
        
        # Timer pour rafraîchir l'éphéméride à minuit
        self.current_date = datetime.now().date()
        self.ephemeride_timer = QTimer()
        self.ephemeride_timer.timeout.connect(self.check_date_change)
        self.ephemeride_timer.start(60000)  # Vérifier toutes les minutes
        
    def init_ui(self):
        """Initialise l'interface utilisateur moderne"""
        self.setWindowTitle("Pointage - Application Moderne")
        self.setGeometry(100, 100, 1920, 1080)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal horizontal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Barre supérieure avec le logo et boutons
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Zone de contenu principale (layout horizontal)
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(40)
        
        # Colonne gauche - Horloge et instruction
        left_column = self.create_left_column()
        content_layout.addWidget(left_column, stretch=1)
        
        # Colonne droite - Informations employé (cachée par défaut)
        self.right_column = self.create_right_column()
        self.right_column.setVisible(False)
        content_layout.addWidget(self.right_column, stretch=1)
        
        main_layout.addWidget(content_widget)
        
        # Appliquer le style
        self.apply_styles()
        
    def get_api_headers(self):
        """Retourne les headers d'authentification pour les requêtes API"""
        return {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key,
            'X-Account-ID': str(self.id_compte)
        }
    
    def create_header(self):
        """Crée la barre d'en-tête"""
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(80)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 0, 30, 0)
        
        # Logo : SVG rendu en pixmap (qualité vectorielle, stable sur Raspberry), sinon PNG, sinon texte
        logo_path_svg = Path(__file__).parent.parent.parent / 'assets' / 'prevenir.svg'
        logo_path_png = Path(__file__).parent.parent.parent / 'assets' / 'prevenir.png'
        logo_loaded = False
        header_height_px = 42

        # 1. SVG → rendu une fois en pixmap (pas de QSvgWidget = pas de plantage, qualité vectorielle)
        pixmap = _svg_to_pixmap(logo_path_svg, header_height_px)
        if pixmap is not None and not pixmap.isNull():
            logo_label = QLabel()
            logo_label.setPixmap(pixmap)
            layout.addWidget(logo_label)
            logo_loaded = True
            logger.debug("Logo SVG affiché")
        elif logo_path_svg.exists():
            logger.info("Logo SVG non affiché (rendu échoué ou Qt SVG absent) — utilisation PNG ou texte")

        # 2. Fallback PNG
        if not logo_loaded and logo_path_png.exists():
            try:
                logo_label = QLabel()
                pixmap = QPixmap(str(logo_path_png))
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaledToHeight(header_height_px, Qt.SmoothTransformation)
                    logo_label.setPixmap(scaled_pixmap)
                    layout.addWidget(logo_label)
                    logo_loaded = True
                    logger.debug("Logo PNG affiché")
            except Exception as e:
                logger.warning(f"Erreur chargement logo PNG: {e}")

        # 3. Fallback texte
        if not logo_loaded:
            logger.info("Logo non affiché — fallback texte 'Pointage' (placez assets/prevenir.png sur le Pi si le SVG échoue)")
            logo_label = QLabel("Pointage")
            logo_label.setFont(QFont("Arial", 24, QFont.Bold))
            logo_label.setStyleSheet("color: white;")
            layout.addWidget(logo_label)
            if not logo_path_png.exists() and not logo_path_svg.exists():
                logger.warning("Logo non trouvé (ni SVG ni PNG)")
        
        layout.addStretch()
        
        # Bouton Administration (visible s'il n'y a aucun employé rang 1 — accès par code)
        self.admin_btn = QPushButton("⚙️ Administration")
        self.admin_btn.setObjectName("adminBtn")
        self.admin_btn.clicked.connect(self.request_admin_pin)
        self.admin_btn.setFixedHeight(50)
        self.admin_btn.setFixedWidth(200)
        # Visible si aucun employé, sinon masqué
        self.admin_btn.setVisible(self.show_admin_on_start)
        layout.addWidget(self.admin_btn)
        return header
        
    def create_left_column(self):
        """Crée la colonne gauche avec l'horloge"""
        widget = QFrame()
        widget.setObjectName("leftColumn")
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(40)
        
        # Horloge principale
        self.clock_label = QLabel("00:00:00")
        self.clock_label.setFont(QFont("Arial", 102, QFont.Bold))  # -15% par rapport à 120
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.clock_label.setStyleSheet("color: #2c3e50; background: transparent;")
        layout.addWidget(self.clock_label)
        
        # Date
        self.date_label = QLabel()
        self.date_label.setFont(QFont("Arial", 28))
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setStyleSheet("color: #7f8c8d; background: transparent;")
        layout.addWidget(self.date_label)
        
        # Liste des pointages du jour (taille réduite de 20% : 16 → 13)
        self.pointages_label = QLabel()
        self.pointages_label.setFont(QFont("Arial", 13))
        self.pointages_label.setAlignment(Qt.AlignCenter)
        self.pointages_label.setStyleSheet("color: #7f8c8d; background: transparent; padding: 10px;")
        self.pointages_label.setVisible(False)  # Caché par défaut
        layout.addWidget(self.pointages_label)
        
        # Message d'instruction : éphéméride du jour (saint + journée mondiale) ou texte par défaut
        self.instruction_label = QLabel(self.default_instruction)
        self.instruction_label.setFont(QFont("Arial", 24))
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.setWordWrap(True)
        self.instruction_label.setStyleSheet("""
            color: #3498db;
            background: transparent;
            padding: 30px;
        """)
        layout.addWidget(self.instruction_label)
        
        layout.addStretch()
        
        return widget
        
    def create_right_column(self):
        """Crée la colonne droite avec les informations employé"""
        widget = QFrame()
        widget.setObjectName("rightColumn")
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Nom de l'employé
        self.employee_name_label = QLabel()
        self.employee_name_label.setFont(QFont("Arial", 29, QFont.Bold))  # -20% par rapport à 36
        self.employee_name_label.setStyleSheet("color: #2c3e50;")
        self.employee_name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.employee_name_label)
        
        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #ecf0f1;")
        separator.setFixedHeight(2)
        layout.addWidget(separator)
        
        # Grille d'informations
        info_grid = QGridLayout()
        info_grid.setSpacing(30)
        info_grid.setContentsMargins(0, 20, 0, 20)
        
        # Planifié aujourd'hui
        self.planif_widget = self.create_info_card(
            "Reste à faire",
            "0h00",
            "#3498db"
        )
        info_grid.addWidget(self.planif_widget, 0, 0)
        
        # Temps réalisé
        self.realise_widget = self.create_info_card(
            "Temps réalisé",
            "0h00",
            "#2ecc71"
        )
        info_grid.addWidget(self.realise_widget, 0, 1)
        
        layout.addLayout(info_grid)
        
        # Message de chargement
        self.loading_label = QLabel("⏳ Chargement des données...")
        self.loading_label.setFont(QFont("Arial", 16))
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("color: #95a5a6; padding: 20px;")
        layout.addWidget(self.loading_label)
        
        layout.addStretch()
        
        return widget
        
    def create_info_card(self, title, value, color):
        """Crée une carte d'information stylisée"""
        card = QFrame()
        card.setObjectName("infoCard")
        card.setStyleSheet(f"""
            QFrame#infoCard {{
                background-color: white;
                border-radius: 15px;
                border-left: 5px solid {color};
                padding: 20px;
            }}
        """)
        card.setMinimumHeight(150)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        # Titre
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 16))
        title_label.setStyleSheet("color: #7f8c8d; border: none;")
        layout.addWidget(title_label)
        
        # Valeur (taille réduite de 20% : 32 → 26)
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 26, QFont.Bold))
        value_label.setStyleSheet(f"color: {color}; border: none;")
        value_label.setObjectName("valueLabel")
        layout.addWidget(value_label)
        
        layout.addStretch()
        
        # Stocker les labels pour mise à jour ultérieure
        card.title_label = title_label
        card.value_label = value_label
        
        return card
        
    def apply_styles(self):
        """Applique les styles CSS à l'application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            
            QFrame#header {
                background-color: #2c3e50;
                border-bottom: 3px solid #3498db;
            }
            
            QFrame#leftColumn {
                background-color: transparent;
            }
            
            QFrame#rightColumn {
                background-color: white;
                border-radius: 20px;
                border: 1px solid #ecf0f1;
            }
            
            QPushButton#adminBtn {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 25px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
            }
            
            QPushButton#adminBtn:hover {
                background-color: #2980b9;
            }
            
            QPushButton#adminBtn:pressed {
                background-color: #21618c;
            }
        """)
        
    def update_clock(self):
        """Met à jour l'horloge et la date"""
        now = datetime.now()
        self.clock_label.setText(now.strftime("%H:%M:%S"))
        
        # Jours de la semaine en français
        jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        mois = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 
                'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
        
        jour_semaine = jours[now.weekday()]
        mois_nom = mois[now.month - 1]
        
        self.date_label.setText(f"{jour_semaine} {now.day} {mois_nom} {now.year}")
        
    def _has_rank1_employee(self):
        """Indique s'il existe au moins un employé de rang 1 (administrateur)."""
        if not self.employees:
            return False
        return any(emp.get('rang') == 1 for emp in self.employees.values())

    def load_employees(self):
        """Charge la liste des employés depuis le fichier JSON"""
        try:
            with open(self.employees_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Support pour les deux formats : tableau direct ou objet avec clé 'employees'
                if isinstance(data, list):
                    employees = data
                else:
                    employees = data.get('employees', [])
                return {emp['rfid']: emp for emp in employees}
        except Exception as e:
            logger.error(f"Erreur lors du chargement des employés: {e}")
            return {}
            
    def reload_employees(self):
        """Recharge le fichier employees.json"""
        logger.info("Rechargement du fichier employees.json...")
        self.employees = self.load_employees()
        logger.info(f"Fichier rechargé: {len(self.employees)} employés")
    
    def _get_ephemeride_du_jour(self):
        """Retourne l'éphéméride du jour (saint + journée mondiale) depuis ephemeride_2ans.csv."""
        try:
            csv_path = Path(__file__).resolve().parent.parent.parent / "ephemeride_2ans.csv"
            if not csv_path.exists():
                return ""
            today = datetime.now().date().isoformat()
            # utf-8-sig pour ignorer un éventuel BOM (Excel, Windows)
            with open(csv_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f, delimiter=";")
                for row in reader:
                    if row.get("date") != today:
                        continue
                    # Saint : 2e colonne (clé "saint")
                    saint = (row.get("saint") or "").strip()
                    # Journée mondiale : 3e colonne (plusieurs clés possibles selon encodage/export)
                    journee = (row.get("journee_mondiale") or row.get("journée_mondiale") or "").strip()
                    if not journee and len(row) >= 3:
                        vals = list(row.values())
                        if len(vals) >= 3:
                            journee = (vals[2] or "").strip()
                    # Toujours afficher saint et/ou journée mondiale quand présents
            parts = []
            if saint:
                parts.append(saint)
            if journee:
                parts.append(journee)
            if parts:
                # Saint et journée mondiale sur des lignes séparées
                return "\n".join(parts)
            return ""
            return ""
        except Exception as e:
            logger.debug(f"Éphéméride non chargée: {e}")
            return ""
    
    def check_date_change(self):
        """Vérifie si la date a changé (minuit passé) et rafraîchit l'éphéméride."""
        new_date = datetime.now().date()
        if new_date != self.current_date:
            self.current_date = new_date
            logger.info(f"Changement de date détecté: {new_date.isoformat()}")
            # Rafraîchir l'éphéméride
            self.default_instruction = self._get_ephemeride_du_jour() or "Présentez votre badge RFID"
            # Si on est sur l'écran d'accueil, mettre à jour le message
            if not self.current_employee:
                self.instruction_label.setText(self.default_instruction)
                logger.info(f"Éphéméride rafraîchie: {self.default_instruction}")
    
    def sync_employees_from_api(self):
        """Synchronise employees.json depuis l'API (télécharge et recharge la liste)."""
        try:
            url = f"{self.api_url}/api_download_employees_json.php?id_compte={self.id_compte}"
            response = requests.get(url, headers=self.get_api_headers(), timeout=15, verify=False)
            response.raise_for_status()
            with open(self.employees_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            data = json.loads(response.text)
            count = len(data) if isinstance(data, list) else len(data.get('employees', []))
            self.reload_employees()
            logger.info(f"Synchronisation employés OK: {count} employé(s)")
        except Exception as e:
            logger.warning(f"Synchronisation employés échouée: {e}")
        
    def start_rfid_reading(self):
        """Démarre la lecture RFID"""
        if not self.rfid_reader.is_reading():
            self.rfid_reader.start_reading(self.on_rfid_badge_detected)
            logger.info("Lecture RFID démarrée")
            
    def on_rfid_badge_detected(self, rfid_code):
        """Callback appelé quand un badge RFID est détecté"""
        # Émettre le signal pour traiter dans le thread principal
        self.rfid_signal.card_detected.emit(rfid_code)
        
    def on_card_detected(self, rfid_code):
        """Traite la détection d'une carte RFID"""
        logger.info(f"Badge détecté: {rfid_code}")
        
        # Vérifier si c'est une nouvelle carte ou la même
        if self.current_rfid == rfid_code and self.is_card_present:
            # Même carte, ne rien faire
            return
        
        # Éviter les détections multiples pendant le traitement
        if self.is_processing:
            logger.debug("Détection ignorée: traitement en cours")
            return
        
        self.is_processing = True
        
        # IMPORTANT: Effacer immédiatement les données de la personne précédente (confidentialité)
        self.clear_employee_data()
        
        # Rechercher l'employé
        employee = self.employees.get(rfid_code)
        
        if not employee:
            logger.warning(f"Badge inconnu: {rfid_code}")
            self.show_error_message("Badge non reconnu")
            self.is_processing = False
            return
        
        # Rang 1 = administrateur : ouvrir directement l'admin sans timbrage ni code
        if employee.get('rang') == 1:
            logger.info("Badge rang 1 — ouverture directe de l'administration")
            self.is_processing = False
            self.open_admin()
            return
        
        # Marquer comme présent
        self.current_rfid = rfid_code
        self.current_employee = employee
        self.is_card_present = True
        self.badge_detection_time = datetime.now()
        self.consultation_mode = False
        self.pointage_done = False  # Flag pour savoir si le pointage a déjà été fait
        
        # Afficher le nom immédiatement
        self.show_employee_info(employee)
        
        # Timer pour détecter si badge maintenu 5 secondes = mode consultation
        id_emp = int(employee['employee_id'].replace('EMP', '').lstrip('0'))
        
        self.pointage_timer = QTimer()
        self.pointage_timer.setSingleShot(True)
        self.pointage_timer.timeout.connect(lambda: self.activate_consultation_mode(id_emp))
        self.pointage_timer.start(5000)  # 5 secondes
        
        # Message: l'utilisateur peut retirer pour pointer ou maintenir pour consulter
        self.show_status_message("👆 Retirez pour pointer | Maintenez 5s pour consulter")
        
        # Charger le dashboard (reste à faire / temps réalisé) dans tous les cas : succès ou erreur (ex. délai 60 s)
        if self.delayed_fetch_timer:
            self.delayed_fetch_timer.stop()
        self.delayed_fetch_timer = QTimer()
        self.delayed_fetch_timer.setSingleShot(True)
        self.delayed_fetch_timer.timeout.connect(lambda: self.fetch_employee_dashboard(id_emp))
        self.delayed_fetch_timer.start(2000)
        
        # Réinitialiser le flag après un court délai
        QTimer.singleShot(3000, lambda: setattr(self, 'is_processing', False))
    
    def activate_consultation_mode(self, id_emp):
        """
        Appelé après 5 secondes si le badge est toujours présent.
        Active le mode consultation (affiche les infos SANS enregistrer de pointage)
        """
        if not self.is_card_present or not self.current_employee:
            # Badge déjà retiré
            return
        
        # Badge toujours présent après 5 secondes = MODE CONSULTATION
        self.consultation_mode = True
        self.pointage_done = True  # Marquer comme "traité" pour éviter le pointage au retrait
        logger.info(f"Mode consultation activé pour employé {id_emp} (badge maintenu 5s)")
        
        # Afficher message de consultation
        self.show_status_message("👀 Consultation - Aucun pointage enregistré", success=None)
        
        # Charger et afficher le dashboard
        self.fetch_employee_dashboard(id_emp)
        
        # Réinitialiser le flag
        self.is_processing = False
    
    def save_pointage(self, id_emp):
        """Enregistre un pointage via l'API ET en local (retourne (True, None) si succès ou (False, message_erreur))"""
        try:
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            heure_str = now.strftime("%H:%M:%S")
            
            # 1. Appeler l'API pour enregistrer le pointage dans MySQL
            url = f"{self.api_url}/api_save_pointage.php"
            data = {
                'id_emp': id_emp,
                'id_compte': self.id_compte,
                'date': date_str,
                'heure': heure_str
            }
            
            response = requests.post(url, json=data, headers=self.get_api_headers(), timeout=5, verify=False)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('success'):
                logger.info(f"Pointage MySQL enregistré pour l'employé {id_emp} à {heure_str}")
                
                # 2. Enregistrer aussi en local dans SQLite
                try:
                    # Déterminer le type (ENTREE/SORTIE) en fonction du dernier pointage
                    last_pointage = self.db_manager.get_last_pointage(str(id_emp))
                    
                    if last_pointage and last_pointage.get('type') == 'ENTREE':
                        pointage_type = 'SORTIE'
                    else:
                        pointage_type = 'ENTREE'
                    
                    # Enregistrer dans SQLite
                    employee_name = self.current_employee.get('name', 'Inconnu')
                    rfid_code = self.current_rfid
                    
                    local_id = self.db_manager.add_pointage(
                        employee_id=str(id_emp),
                        employee_name=employee_name,
                        rfid=rfid_code,
                        pointage_type=pointage_type
                    )
                    
                    logger.info(f"Pointage SQLite enregistré (ID: {local_id}, Type: {pointage_type})")
                    
                except Exception as e:
                    logger.error(f"Erreur lors de l'enregistrement SQLite: {e}")
                    # Ne pas bloquer si l'enregistrement local échoue
                
                return True, None
            else:
                error = result.get('error', 'Erreur inconnue')
                logger.error(f"Erreur API pointage: {error}")
                return False, f"API: {error}"
            
        except requests.exceptions.Timeout:
            error = "Délai d'attente dépassé (serveur trop lent)"
            logger.error(f"Timeout lors de l'enregistrement du pointage: {error}")
            return False, error
        except requests.exceptions.ConnectionError:
            error = "Impossible de se connecter au serveur"
            logger.error(f"Erreur de connexion: {error}")
            return False, error
        except Exception as e:
            error = str(e)
            logger.error(f"Erreur lors de l'enregistrement du pointage: {error}")
            return False, f"Erreur système: {error}"
    
    def show_employee_info(self, employee):
        """Affiche les informations de base de l'employé"""
        name = employee.get('name', '')
        if len(name) > 30:
            name = name[:27] + "..."
        self.employee_name_label.setText(name)
        
        # Masquer le message d'instruction
        self.instruction_label.setVisible(False)
        
        # Afficher la colonne de droite
        self.right_column.setVisible(True)
        
        # Afficher le message de chargement
        self.loading_label.setVisible(True)
    
    def show_status_message(self, message, success=None):
        """Affiche un message de statut temporaire"""
        # Changer la couleur selon le statut
        if success is True:
            color = "#27ae60"  # Vert pour succès
        elif success is False:
            color = "#e74c3c"  # Rouge pour erreur
        else:
            color = "#3498db"  # Bleu pour info/en cours
        
        # Si le message contient un saut de ligne, formater avec la première ligne en gros et le reste en petit
        if '\n' in message:
            lines = message.split('\n', 1)
            formatted_message = f'<div style="font-size: 24px; font-weight: bold;">{lines[0]}</div>'
            if len(lines) > 1 and lines[1].strip():
                formatted_message += f'<div style="font-size: 14px; margin-top: 10px; opacity: 0.9;">{lines[1]}</div>'
            self.instruction_label.setText(formatted_message)
        else:
            self.instruction_label.setText(message)
        
        self.instruction_label.setStyleSheet(f"""
            color: white;
            background-color: {color};
            padding: 30px;
            border-radius: 10px;
        """)
        self.instruction_label.setVisible(True)
        
        # Si c'est un message de succès ou d'erreur, restaurer après 2 secondes
        if success is not None:
            QTimer.singleShot(2000, lambda: self.hide_status_message())
    
    def hide_status_message(self):
        """Masque le message de statut"""
        if self.is_card_present:
            # Si le badge est toujours là, masquer simplement le message
            self.instruction_label.setVisible(False)
        else:
            # Sinon, restaurer le message par défaut
            self.reset_instruction_message()
    
    def fetch_employee_dashboard(self, id_emp):
        """Récupère les données du dashboard depuis l'API"""
        try:
            url = f"{self.api_url}/api_get_employee_dashboard.php"
            params = {
                'id_emp': id_emp,
                'id_compte': self.id_compte,
                'date': datetime.now().strftime("%Y-%m-%d")
            }
            
            logger.info(f"Récupération des données dashboard pour employé {id_emp}...")
            
            response = requests.get(url, params=params, headers=self.get_api_headers(), timeout=10, verify=False)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success'):
                self.dashboard_data = data['data']
                self.update_dashboard_display()
                
                # Démarrer un timer pour rafraîchir les données toutes les 30 secondes
                if self.data_fetch_timer:
                    self.data_fetch_timer.stop()
                    
                self.data_fetch_timer = QTimer()
                self.data_fetch_timer.timeout.connect(lambda: self.fetch_employee_dashboard(id_emp))
                self.data_fetch_timer.start(30000)  # 30 secondes
                
            else:
                logger.error(f"Erreur API: {data.get('error', 'Erreur inconnue')}")
                self.show_error_message("Erreur lors du chargement des données")
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données: {e}")
            self.show_error_message(f"Erreur: {str(e)}")
            
    def update_dashboard_display(self):
        """Met à jour l'affichage du dashboard avec les données"""
        if not self.dashboard_data:
            return
            
        # Masquer le message de chargement
        self.loading_label.setVisible(False)
        
        # Mettre à jour les cartes d'information
        data = self.dashboard_data
        
        # Reste à faire
        heures_restantes = data['temps_travaille'].get('heures_restantes', 0)
        self.planif_widget.value_label.setText(self.format_hours(heures_restantes))
        
        # Temps réalisé
        heures_realisees = data['temps_travaille'].get('heures_realisees', 0)
        self.realise_widget.value_label.setText(self.format_hours(heures_realisees))
        
        # Afficher les pointages du jour par paires
        pointages_paires = data['temps_travaille'].get('pointages_paires', [])
        if pointages_paires:
            pointages_text = "Pointages du jour :\n"
            for i, paire in enumerate(pointages_paires, 1):
                entree = paire['entree']
                sortie = paire['sortie'] if paire['sortie'] else "..."
                duree = paire.get('duree', 0)
                pointages_text += f"{i}. {entree} → {sortie}  ({self.format_hours(duree)})\n"
            self.pointages_label.setText(pointages_text.strip())
            self.pointages_label.setVisible(True)
        else:
            self.pointages_label.setVisible(False)
    
    def format_hours(self, hours):
        """Formate les heures décimales en HH:MM:SS"""
        if hours is None:
            hours = 0
        total_seconds = int(hours * 3600)
        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
        
    def check_card_presence(self):
        """Vérifie si la carte est toujours présente"""
        if not self.is_card_present or not self.current_rfid:
            return
        
        # Vérifier si le dernier scan de cette carte est récent (moins de 4 secondes)
        # Le lecteur RFID scanne toutes les ~300ms quand une carte est présente
        # Donc 4 secondes = ~13 tentatives manquées = carte vraiment retirée
        try:
            from time import time
            current_time = time()
            
            # Vérifier si le lecteur RFID a un dernier temps de lecture
            if hasattr(self.rfid_reader, 'last_read_time'):
                time_since_last_read = current_time - self.rfid_reader.last_read_time
                
                # Si pas de lecture depuis 4 secondes, la carte a été retirée
                # (le lecteur scanne toutes les 300ms, donc 4s = vraiment absent)
                if time_since_last_read > 2:
                    logger.info(f"Badge retiré (pas de lecture depuis {time_since_last_read:.2f}s)")
                    self.hide_employee_info()
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de présence de carte: {e}")
    
    def clear_employee_data(self):
        """Efface immédiatement toutes les données affichées (pour confidentialité)"""
        # Effacer le nom de l'employé
        self.employee_name_label.setText("")
        
        # Masquer/réinitialiser la colonne de droite
        self.right_column.setVisible(False)
        
        # Effacer les données du dashboard
        self.dashboard_data = None
        
        # Masquer les pointages
        self.pointages_label.setVisible(False)
        self.pointages_label.setText("")
        
        # Bouton Admin visible seulement s'il n'y a aucun employé rang 1
        self.admin_btn.setVisible(not self._has_rank1_employee())
        
        # Réinitialiser les cartes d'information si elles existent
        if hasattr(self, 'planif_widget') and hasattr(self.planif_widget, 'value_label'):
            self.planif_widget.value_label.setText("--:--:--")
        if hasattr(self, 'realise_widget') and hasattr(self.realise_widget, 'value_label'):
            self.realise_widget.value_label.setText("--:--:--")
        
        # Masquer le message de chargement
        if hasattr(self, 'loading_label'):
            self.loading_label.setVisible(False)
        
        logger.debug("Données de l'employé précédent effacées")
    
    def hide_employee_info(self):
        """Cache les informations de l'employé quand la carte est retirée"""
        # Si le badge est retiré ET qu'aucun pointage n'a été fait (pas en mode consultation)
        # = Enregistrer le pointage IMMÉDIATEMENT (badge retiré rapidement)
        if self.current_employee and not getattr(self, 'pointage_done', False):
            # Annuler le timer de consultation
            if hasattr(self, 'pointage_timer') and self.pointage_timer.isActive():
                self.pointage_timer.stop()
            
            id_emp = int(self.current_employee['employee_id'].replace('EMP', '').lstrip('0'))
            logger.info(f"Badge retiré rapidement - enregistrement INSTANTANÉ du pointage pour employé {id_emp}")
            
            success, pointage_type, error_msg = self.save_pointage(id_emp)
            
            if success:
                # Afficher "ENTRÉE enregistrée" ou "SORTIE enregistrée"
                self.show_status_message(f"✓ {pointage_type} enregistrée", success=True)
                # Charger le dashboard en arrière-plan (optionnel, après 2s)
                QTimer.singleShot(2000, lambda: self.fetch_employee_dashboard(id_emp) if self.is_card_present else None)
            else:
                self.show_status_message(f"❌ Erreur: {error_msg}", success=False)
        
        self.is_card_present = False
        self.current_rfid = None
        self.current_employee = None
        self.dashboard_data = None
        self.is_processing = False
        self.consultation_mode = False
        self.pointage_done = False
        
        # Arrêter les timers
        if self.delayed_fetch_timer:
            self.delayed_fetch_timer.stop()
            self.delayed_fetch_timer = None
        
        if self.data_fetch_timer:
            self.data_fetch_timer.stop()
            self.data_fetch_timer = None
        
        if hasattr(self, 'pointage_timer'):
            self.pointage_timer.stop()
        
        # Masquer la colonne de droite
        self.right_column.setVisible(False)
        
        # Masquer les pointages
        self.pointages_label.setVisible(False)
        
        # Bouton Admin visible seulement s'il n'y a aucun employé rang 1
        self.admin_btn.setVisible(not self._has_rank1_employee())
        
        # Restaurer le message d'instruction par défaut
        self.reset_instruction_message()
        self.instruction_label.setVisible(True)
        
        logger.info("Informations employé masquées")
        
    def show_error_message(self, message):
        """Affiche un message d'erreur temporaire"""
        self.instruction_label.setText(f"❌ {message}")
        self.instruction_label.setStyleSheet("color: #e74c3c; background: transparent; padding: 30px;")
        
        # Restaurer le message d'origine après 3 secondes
        QTimer.singleShot(3000, lambda: self.reset_instruction_message())
        
    def reset_instruction_message(self):
        """Restaure le message d'instruction par défaut (éphéméride du jour)"""
        self.instruction_label.setText(self.default_instruction)
        self.instruction_label.setStyleSheet("color: #3498db; background: transparent; padding: 30px;")
        
    def request_admin_pin(self):
        """Demande le code PIN avec un pavé numérique tactile"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QMessageBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Code PIN Administrateur")
        dialog.setModal(True)
        dialog.setFixedSize(400, 550)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Label instruction
        instruction = QLabel("Entrez le code PIN :")
        instruction.setFont(QFont("Arial", 18))
        instruction.setAlignment(Qt.AlignCenter)
        layout.addWidget(instruction)
        
        # Affichage du code (masqué avec des points)
        pin_display = QLabel("••••")
        pin_display.setFont(QFont("Arial", 36, QFont.Bold))
        pin_display.setAlignment(Qt.AlignCenter)
        pin_display.setStyleSheet("""
            background-color: white;
            border: 2px solid #3498db;
            border-radius: 10px;
            padding: 20px;
            color: #2c3e50;
        """)
        layout.addWidget(pin_display)
        
        # Variable pour stocker le PIN
        pin_value = []
        
        def update_display():
            pin_display.setText("•" * len(pin_value) if pin_value else "••••")
        
        def on_number_click(num):
            if len(pin_value) < 4:
                pin_value.append(str(num))
                update_display()
        
        def on_clear():
            pin_value.clear()
            update_display()
        
        def on_validate():
            if len(pin_value) == 4:
                entered_pin = "".join(pin_value)
                if entered_pin == "8179":
                    logger.info("Code PIN correct - Ouverture administration")
                    dialog.accept()
                    self.open_admin()
                else:
                    logger.warning("Code PIN incorrect")
                    QMessageBox.warning(dialog, "Accès refusé", "Code PIN incorrect.", QMessageBox.Ok)
                    pin_value.clear()
                    update_display()
        
        # Grille de boutons numériques (3x4)
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Boutons 1-9
        for i in range(1, 10):
            btn = QPushButton(str(i))
            btn.setFixedSize(100, 80)
            btn.setFont(QFont("Arial", 24, QFont.Bold))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ecf0f1;
                    border: 2px solid #bdc3c7;
                    border-radius: 10px;
                    color: #2c3e50;
                }
                QPushButton:pressed {
                    background-color: #3498db;
                    color: white;
                }
            """)
            btn.clicked.connect(lambda checked, num=i: on_number_click(num))
            row = (i - 1) // 3
            col = (i - 1) % 3
            grid.addWidget(btn, row, col)
        
        # Bouton 0, Effacer, Valider
        btn_clear = QPushButton("⌫")
        btn_clear.setFixedSize(100, 80)
        btn_clear.setFont(QFont("Arial", 28, QFont.Bold))
        btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                border: none;
                border-radius: 10px;
                color: white;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
        """)
        btn_clear.clicked.connect(on_clear)
        grid.addWidget(btn_clear, 3, 0)
        
        btn_zero = QPushButton("0")
        btn_zero.setFixedSize(100, 80)
        btn_zero.setFont(QFont("Arial", 24, QFont.Bold))
        btn_zero.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                color: #2c3e50;
            }
            QPushButton:pressed {
                background-color: #3498db;
                color: white;
            }
        """)
        btn_zero.clicked.connect(lambda: on_number_click(0))
        grid.addWidget(btn_zero, 3, 1)
        
        btn_validate = QPushButton("✓")
        btn_validate.setFixedSize(100, 80)
        btn_validate.setFont(QFont("Arial", 28, QFont.Bold))
        btn_validate.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                border: none;
                border-radius: 10px;
                color: white;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        btn_validate.clicked.connect(on_validate)
        grid.addWidget(btn_validate, 3, 2)
        
        layout.addLayout(grid)
        
        # Bouton Annuler
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setFont(QFont("Arial", 14))
        btn_cancel.setFixedHeight(50)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:pressed {
                background-color: #7f8c8d;
            }
        """)
        btn_cancel.clicked.connect(dialog.reject)
        layout.addWidget(btn_cancel)
        
        dialog.exec_()
    
    def open_admin(self):
        """Ouvre le panneau d'administration"""
        from .admin_panel import AdminPanel
        
        # Arrêter temporairement la lecture RFID principale
        if self.rfid_reader.is_reading():
            self.rfid_reader.stop_reading()
            logger.info("Lecture RFID principale arrêtée pour l'administration")
        
        # Ouvrir le panneau avec un callback pour restaurer la lecture
        self.admin_window = AdminPanel(
            self.db_manager, 
            self.rfid_reader, 
            self,
            restore_rfid_callback=self.restore_main_rfid_reading
        )
        self.admin_window.show()
        self.admin_window.activateWindow()
        self.admin_window.raise_()
    
    def restore_main_rfid_reading(self):
        """Restaure la lecture RFID principale après fermeture de l'admin"""
        try:
            # Recharger les employés (un rang 1 peut avoir été ajouté/supprimé)
            self.reload_employees()
            self.admin_btn.setVisible(not self._has_rank1_employee())
            if not self.rfid_reader.is_reading():
                self.start_rfid_reading()
                logger.info("Lecture RFID principale restaurée après administration")
        except Exception as e:
            logger.error(f"Erreur lors de la restauration de la lecture RFID: {e}")
    
    def closeEvent(self, event):
        """Gestion de la fermeture de la fenêtre"""
        if self.rfid_reader.is_reading():
            self.rfid_reader.stop_reading()
        
        if self.data_fetch_timer:
            self.data_fetch_timer.stop()
        
        if self.employees_sync_timer:
            self.employees_sync_timer.stop()
            
        event.accept()


