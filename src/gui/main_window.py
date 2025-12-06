"""
Interface moderne de pointage - Version horizontale
Inspirée de l'application Tipee avec un design épuré et intuitif
"""

import json
import logging
from datetime import datetime, time
from pathlib import Path

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame, QGridLayout, QApplication, QLineEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPalette

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


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
        self.show_admin_on_start = False  # Flag pour afficher l'admin au démarrage
        self.employees = self.load_employees()
        
        # Afficher le bouton Admin si aucun employé configuré
        if not self.employees or len(self.employees) == 0:
            # Pas d'employés = premier démarrage, afficher le bouton admin
            # Le bouton sera créé plus tard dans create_header
            self.show_admin_on_start = True
            logger.info("Aucun employé configuré - bouton Admin sera affiché")
        else:
            self.show_admin_on_start = False
        
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
        
        # Signal pour la lecture RFID
        self.rfid_signal = RFIDSignal()
        self.rfid_signal.card_detected.connect(self.on_card_detected)
        
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
        
        # Logo/Titre
        title_label = QLabel("Pointage")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Bouton Administration (masqué par défaut, visible uniquement pour rang=1)
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
        self.clock_label.setFont(QFont("Arial", 120, QFont.Bold))
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.clock_label.setStyleSheet("color: #2c3e50; background: transparent;")
        layout.addWidget(self.clock_label)
        
        # Date
        self.date_label = QLabel()
        self.date_label.setFont(QFont("Arial", 28))
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setStyleSheet("color: #7f8c8d; background: transparent;")
        layout.addWidget(self.date_label)
        
        # Liste des pointages du jour
        self.pointages_label = QLabel()
        self.pointages_label.setFont(QFont("Arial", 16))
        self.pointages_label.setAlignment(Qt.AlignCenter)
        self.pointages_label.setStyleSheet("color: #7f8c8d; background: transparent; padding: 10px;")
        self.pointages_label.setVisible(False)  # Caché par défaut
        layout.addWidget(self.pointages_label)
        
        # Message d'instruction
        self.instruction_label = QLabel("Présentez votre badge RFID")
        self.instruction_label.setFont(QFont("Arial", 24))
        self.instruction_label.setAlignment(Qt.AlignCenter)
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
        self.employee_name_label.setFont(QFont("Arial", 36, QFont.Bold))
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
        
        # Solde d'heures
        self.solde_heures_widget = self.create_info_card(
            "Solde de travail",
            "+0h00",
            "#9b59b6"
        )
        info_grid.addWidget(self.solde_heures_widget, 1, 0)
        
        # Solde de vacances
        self.solde_vacances_widget = self.create_info_card(
            "Solde de vacances",
            "0.00",
            "#e67e22"
        )
        info_grid.addWidget(self.solde_vacances_widget, 1, 1)
        
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
        
        # Valeur
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 32, QFont.Bold))
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
        
    def load_employees(self):
        """Charge la liste des employés depuis le fichier JSON"""
        try:
            with open(self.employees_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {emp['rfid']: emp for emp in data['employees']}
        except Exception as e:
            logger.error(f"Erreur lors du chargement des employés: {e}")
            return {}
            
    def reload_employees(self):
        """Recharge le fichier employees.json"""
        logger.info("Rechargement du fichier employees.json...")
        self.employees = self.load_employees()
        logger.info(f"Fichier rechargé: {len(self.employees)} employés")
        
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
        
        # Rechercher l'employé
        employee = self.employees.get(rfid_code)
        
        if not employee:
            logger.warning(f"Badge inconnu: {rfid_code}")
            self.show_error_message("Badge non reconnu")
            self.is_processing = False
            return
        
        # Marquer comme présent
        self.current_rfid = rfid_code
        self.current_employee = employee
        self.is_card_present = True
        
        # Afficher le nom immédiatement
        self.show_employee_info(employee)
        
        # Afficher "Enregistrement en cours..."
        self.show_status_message("⏳ Enregistrement en cours...")
        
        # Enregistrer le pointage
        id_emp = int(employee['employee_id'].replace('EMP', '').lstrip('0'))
        success = self.save_pointage(id_emp)
        
        if success:
            # Afficher "Timbrage enregistré"
            self.show_status_message("✓ Timbrage enregistré", success=True)
            
            # Attendre 2 secondes avant de charger les données détaillées
            if self.delayed_fetch_timer:
                self.delayed_fetch_timer.stop()
            self.delayed_fetch_timer = QTimer()
            self.delayed_fetch_timer.setSingleShot(True)
            self.delayed_fetch_timer.timeout.connect(lambda: self.fetch_employee_dashboard(id_emp))
            self.delayed_fetch_timer.start(2000)
        else:
            self.show_status_message("❌ Erreur d'enregistrement", success=False)
        
        # Réinitialiser le flag après un court délai
        QTimer.singleShot(3000, lambda: setattr(self, 'is_processing', False))
    
    def save_pointage(self, id_emp):
        """Enregistre un pointage via l'API ET en local (retourne True si succès)"""
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
                
                return True
            else:
                logger.error(f"Erreur API pointage: {result.get('error', 'Erreur inconnue')}")
                return False
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du pointage: {e}")
            return False
    
    def show_employee_info(self, employee):
        """Affiche les informations de base de l'employé"""
        self.employee_name_label.setText(employee['name'])
        
        # Masquer le message d'instruction
        self.instruction_label.setVisible(False)
        
        # Afficher la colonne de droite
        self.right_column.setVisible(True)
        
        # Afficher le message de chargement
        self.loading_label.setVisible(True)
        
        # Afficher le bouton Admin si l'employé est administrateur (rang=1)
        if employee.get('rang') == 1:
            self.admin_btn.setVisible(True)
            logger.info("Bouton Administration affiché (employé rang=1)")
        
    
    def show_status_message(self, message, success=None):
        """Affiche un message de statut temporaire"""
        # Changer la couleur selon le statut
        if success is True:
            color = "#27ae60"  # Vert pour succès
        elif success is False:
            color = "#e74c3c"  # Rouge pour erreur
        else:
            color = "#3498db"  # Bleu pour info/en cours
        
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
        restant = data['temps_travaille']['heures_restantes_formatted']
        self.planif_widget.value_label.setText(restant)
        
        # Temps réalisé
        realise = data['temps_travaille']['heures_realisees_formatted']
        self.realise_widget.value_label.setText(realise)
        
        # Solde d'heures
        solde_h = data['soldes']['heures']['valeur']
        signe = "+" if solde_h >= 0 else ""
        self.solde_heures_widget.value_label.setText(f"{signe}{data['soldes']['heures']['formatted']}")
        
        # Mettre la couleur en rouge si négatif
        if solde_h < 0:
            self.solde_heures_widget.value_label.setStyleSheet("color: #e74c3c; border: none;")
        else:
            self.solde_heures_widget.value_label.setStyleSheet("color: #9b59b6; border: none;")
        
        # Solde de vacances
        solde_v = data['soldes']['vacances']['jours']
        self.solde_vacances_widget.value_label.setText(f"{solde_v:.2f}")
        
        # Afficher les pointages du jour par paires
        pointages_paires = data['temps_travaille'].get('pointages_paires', [])
        if pointages_paires:
            pointages_text = "Pointages du jour :\n"
            for i, paire in enumerate(pointages_paires, 1):
                entree = paire['entree']
                sortie = paire['sortie'] if paire['sortie'] else "..."
                duree = paire['duree_formatted']
                pointages_text += f"{i}. {entree} → {sortie}  ({duree})\n"
            self.pointages_label.setText(pointages_text.strip())
            self.pointages_label.setVisible(True)
        else:
            self.pointages_label.setVisible(False)
        
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
    
    def hide_employee_info(self):
        """Cache les informations de l'employé quand la carte est retirée"""
        self.is_card_present = False
        self.current_rfid = None
        self.current_employee = None
        self.dashboard_data = None
        self.is_processing = False  # Réinitialiser le flag de traitement
        
        # Arrêter les timers
        if self.delayed_fetch_timer:
            self.delayed_fetch_timer.stop()
            self.delayed_fetch_timer = None
        
        if self.data_fetch_timer:
            self.data_fetch_timer.stop()
            self.data_fetch_timer = None
        
        # Masquer la colonne de droite
        self.right_column.setVisible(False)
        
        # Masquer les pointages
        self.pointages_label.setVisible(False)
        
        # Masquer le bouton Administration
        self.admin_btn.setVisible(False)
        
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
        """Restaure le message d'instruction par défaut"""
        self.instruction_label.setText("Présentez votre badge RFID")
        self.instruction_label.setStyleSheet("color: #3498db; background: transparent; padding: 30px;")
        
    def request_admin_pin(self):
        """Demande le code PIN avant d'ouvrir l'administration"""
        from PyQt5.QtWidgets import QInputDialog, QMessageBox
        
        # Demander le code PIN
        pin, ok = QInputDialog.getText(
            self,
            "Code PIN requis",
            "Entrez le code PIN administrateur:",
            echo=QLineEdit.Password
        )
        
        if ok:
            # Vérifier le PIN (8179)
            if pin == "8179":
                logger.info("Code PIN correct - Ouverture administration")
                self.open_admin()
            else:
                logger.warning("Code PIN incorrect")
                QMessageBox.warning(
                    self,
                    "Accès refusé",
                    "Code PIN incorrect.",
                    QMessageBox.Ok
                )
    
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
            
        event.accept()

