"""
Interface moderne de pointage - Version horizontale
Inspirée de l'application Tipee avec un design épuré et intuitif
"""

import json
import logging
from datetime import datetime, time
from pathlib import Path

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame, QGridLayout, QApplication)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPalette

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class RFIDSignal(QObject):
    """Signal pour la détection de carte RFID"""
    card_detected = pyqtSignal(str)


class ModernMainWindow(QMainWindow):
    """Fenêtre principale moderne de l'application de timbrage"""
    
    def __init__(self, db_manager, rfid_reader, employees_file, parent=None):
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.rfid_reader = rfid_reader
        self.employees_file = Path(employees_file)
        self.employees = self.load_employees()
        
        # Configuration API
        self.api_url = "https://prestest.ddev.site"
        self.id_compte = 2  # TODO: Configurable
        
        # État de l'application
        self.current_employee = None
        self.current_rfid = None
        self.is_card_present = False
        self.dashboard_data = None
        self.data_fetch_timer = None
        
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
        
        # Bouton Administration
        admin_btn = QPushButton("⚙️ Administration")
        admin_btn.setObjectName("adminBtn")
        admin_btn.clicked.connect(self.open_admin)
        admin_btn.setFixedHeight(50)
        admin_btn.setFixedWidth(200)
        layout.addWidget(admin_btn)
        
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
            
        # Rechercher l'employé
        employee = self.employees.get(rfid_code)
        
        if not employee:
            logger.warning(f"Badge inconnu: {rfid_code}")
            self.show_error_message("Badge non reconnu")
            return
            
        # Enregistrer le pointage
        id_emp = int(employee['employee_id'].replace('EMP', '').lstrip('0'))
        self.save_pointage(id_emp)
        
        # Afficher les informations de l'employé
        self.current_rfid = rfid_code
        self.current_employee = employee
        self.is_card_present = True
        
        self.show_employee_info(employee)
        
        # Attendre 3 secondes avant de charger les données détaillées
        QTimer.singleShot(3000, lambda: self.fetch_employee_dashboard(id_emp))
        
    def save_pointage(self, id_emp):
        """Enregistre un pointage dans la base de données"""
        try:
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            heure_str = now.strftime("%H:%M:%S")
            
            self.db_manager.save_pointage(id_emp, date_str, heure_str)
            logger.info(f"Pointage enregistré pour l'employé {id_emp} à {heure_str}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du pointage: {e}")
            
    def show_employee_info(self, employee):
        """Affiche les informations de base de l'employé"""
        self.employee_name_label.setText(employee['name'])
        
        # Masquer le message d'instruction
        self.instruction_label.setVisible(False)
        
        # Afficher la colonne de droite
        self.right_column.setVisible(True)
        
        # Afficher le message de chargement
        self.loading_label.setVisible(True)
        
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
            
            response = requests.get(url, params=params, timeout=10, verify=False)
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
        self.realise_widget.value_label.setText(restant)
        
        # Temps réalisé
        realise = data['temps_travaille']['heures_realisees_formatted']
        self.planif_widget.value_label.setText(realise)
        
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
        
    def check_card_presence(self):
        """Vérifie si la carte est toujours présente"""
        if not self.is_card_present:
            return
            
        # TODO: Implémenter une vraie détection de retrait de carte
        # Pour l'instant, on simule avec un timeout de 10 secondes
        # Dans une vraie implémentation, le lecteur RFID devrait nous dire
        # quand la carte est retirée
        
    def hide_employee_info(self):
        """Cache les informations de l'employé quand la carte est retirée"""
        self.is_card_present = False
        self.current_rfid = None
        self.current_employee = None
        self.dashboard_data = None
        
        # Arrêter le timer de rafraîchissement
        if self.data_fetch_timer:
            self.data_fetch_timer.stop()
            self.data_fetch_timer = None
        
        # Masquer la colonne de droite
        self.right_column.setVisible(False)
        
        # Réafficher le message d'instruction
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
        
    def open_admin(self):
        """Ouvre le panneau d'administration"""
        from .admin_panel import AdminPanel
        self.admin_window = AdminPanel(self.db_manager, self.rfid_reader, self)
        self.admin_window.show()
        self.admin_window.activateWindow()
        self.admin_window.raise_()
        
    def closeEvent(self, event):
        """Gestion de la fermeture de la fenêtre"""
        if self.rfid_reader.is_reading():
            self.rfid_reader.stop_reading()
        
        if self.data_fetch_timer:
            self.data_fetch_timer.stop()
            
        event.accept()

