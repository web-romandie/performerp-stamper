"""
Interface graphique principale du système de pointage
"""
import sys
import json
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QColor
import logging

logger = logging.getLogger(__name__)


class RFIDSignal(QObject):
    """Signal pour la communication thread-safe avec l'UI"""
    card_detected = pyqtSignal(str)


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self, db_manager, rfid_reader, employees_file):
        super().__init__()
        
        self.db_manager = db_manager
        self.rfid_reader = rfid_reader
        self.employees_file = Path(employees_file)
        self.employees = self.load_employees()
        
        # Signal pour la lecture RFID
        self.rfid_signal = RFIDSignal()
        self.rfid_signal.card_detected.connect(self.on_card_detected)
        
        self.init_ui()
        self.start_rfid_reading()
        
        # Timer pour l'horloge
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        
        # Timer pour rafraîchir la liste
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_recent_pointages)
        self.refresh_timer.start(5000)  # Rafraîchir toutes les 5 secondes
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        self.setWindowTitle("Système de Pointage")
        self.setMinimumSize(1024, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # En-tête avec horloge et titre
        header_layout = QHBoxLayout()
        
        # Titre
        title_label = QLabel("SYSTÈME DE POINTAGE")
        title_label.setFont(QFont("Arial", 32, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        # Horloge
        self.clock_label = QLabel()
        self.clock_label.setFont(QFont("Arial", 24))
        self.clock_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.update_clock()
        header_layout.addWidget(self.clock_label)
        
        main_layout.addLayout(header_layout)
        
        # Séparateur
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator1)
        
        # Zone d'instruction
        self.instruction_label = QLabel("Présentez votre badge RFID")
        self.instruction_label.setFont(QFont("Arial", 28))
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.setStyleSheet("""
            QLabel {
                background-color: #3498db;
                color: white;
                padding: 40px;
                border-radius: 10px;
            }
        """)
        main_layout.addWidget(self.instruction_label)
        
        # Zone de feedback
        self.feedback_label = QLabel("")
        self.feedback_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.feedback_label.setAlignment(Qt.AlignCenter)
        self.feedback_label.setMinimumHeight(80)
        self.feedback_label.setStyleSheet("""
            QLabel {
                padding: 20px;
                border-radius: 10px;
            }
        """)
        main_layout.addWidget(self.feedback_label)
        
        # Séparateur
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator2)
        
        # Derniers pointages
        recent_label = QLabel("Derniers pointages")
        recent_label.setFont(QFont("Arial", 18, QFont.Bold))
        main_layout.addWidget(recent_label)
        
        # Table des pointages récents
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Heure", "Nom", "Type", ""])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 300)
        self.table.setColumnWidth(2, 150)
        self.table.setFont(QFont("Arial", 14))
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        main_layout.addWidget(self.table)
        
        # Boutons d'administration
        button_layout = QHBoxLayout()
        
        self.admin_button = QPushButton("Administration")
        self.admin_button.setFont(QFont("Arial", 14))
        self.admin_button.setMinimumHeight(50)
        self.admin_button.clicked.connect(self.open_admin)
        button_layout.addWidget(self.admin_button)
        
        self.quit_button = QPushButton("Quitter")
        self.quit_button.setFont(QFont("Arial", 14))
        self.quit_button.setMinimumHeight(50)
        self.quit_button.clicked.connect(self.close)
        button_layout.addWidget(self.quit_button)
        
        main_layout.addLayout(button_layout)
        
        central_widget.setLayout(main_layout)
        
        # Rafraîchir la liste
        self.refresh_recent_pointages()
    
    def update_clock(self):
        """Met à jour l'horloge"""
        now = datetime.now()
        self.clock_label.setText(now.strftime("%H:%M:%S\n%d/%m/%Y"))
    
    def load_employees(self):
        """Charge la liste des employés"""
        try:
            with open(self.employees_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {emp['rfid']: emp for emp in data['employees']}
        except Exception as e:
            logger.error(f"Erreur lors du chargement des employés: {e}")
            return {}
    
    def reload_employees(self):
        """Recharge le fichier employees.json et met à jour l'affichage"""
        logger.info("Rechargement du fichier employees.json...")
        old_count = len(self.employees)
        self.employees = self.load_employees()
        new_count = len(self.employees)
        
        logger.info(f"Fichier rechargé: {old_count} → {new_count} employés")
        
        # Afficher un message de confirmation
        if hasattr(self, 'instruction_label'):
            original_text = self.instruction_label.text()
            self.instruction_label.setText(f"✓ Fichier rechargé: {new_count} employés")
            self.instruction_label.setStyleSheet("""
                QLabel {
                    background-color: #27ae60;
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                }
            """)
            
            # Restaurer le texte original après 3 secondes
            QTimer.singleShot(3000, lambda: self.reset_instruction_label(original_text))
    
    def reset_instruction_label(self, text):
        """Restaure le texte d'instruction original"""
        if hasattr(self, 'instruction_label'):
            self.instruction_label.setText(text)
            self.instruction_label.setStyleSheet("""
                QLabel {
                    background-color: #3498db;
                    color: white;
                    padding: 40px;
                    border-radius: 10px;
                }
            """)
    
    def start_rfid_reading(self):
        """Démarre la lecture RFID"""
        if self.rfid_reader.connect():
            self.rfid_reader.start_reading(self.rfid_callback)
            logger.info("Lecture RFID démarrée")
        else:
            QMessageBox.warning(self, "Erreur RFID", 
                              "Impossible de se connecter au lecteur RFID.\n"
                              "Vérifiez la connexion.")
    
    def rfid_callback(self, rfid_code):
        """Callback appelé lors de la lecture d'une carte"""
        self.rfid_signal.card_detected.emit(rfid_code)
    
    def on_card_detected(self, rfid_code):
        """Traite la détection d'une carte RFID"""
        logger.info(f"Carte détectée: {rfid_code}")
        
        # Vérifier si l'employé existe
        if rfid_code not in self.employees:
            self.show_feedback("Badge non reconnu", False)
            return
        
        employee = self.employees[rfid_code]
        employee_id = employee['employee_id']
        employee_name = employee['name']
        
        # Déterminer le type de pointage
        last_pointage = self.db_manager.get_last_pointage(employee_id)
        
        if last_pointage is None or last_pointage['type'] == 'SORTIE':
            pointage_type = 'ENTREE'
        else:
            pointage_type = 'SORTIE'
        
        # Enregistrer le pointage
        try:
            self.db_manager.add_pointage(employee_id, employee_name, rfid_code, pointage_type)
            
            message = f"Bonjour {employee_name}"
            if pointage_type == 'ENTREE':
                message += "\n✓ ENTRÉE enregistrée"
            else:
                message += "\n✓ SORTIE enregistrée"
            
            self.show_feedback(message, True)
            self.refresh_recent_pointages()
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement: {e}")
            self.show_feedback("Erreur d'enregistrement", False)
    
    def show_feedback(self, message, success):
        """Affiche un message de feedback"""
        self.feedback_label.setText(message)
        
        if success:
            self.feedback_label.setStyleSheet("""
                QLabel {
                    background-color: #2ecc71;
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                }
            """)
        else:
            self.feedback_label.setStyleSheet("""
                QLabel {
                    background-color: #e74c3c;
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                }
            """)
        
        # Effacer le message après 3 secondes
        QTimer.singleShot(3000, lambda: self.feedback_label.setText(""))
    
    def refresh_recent_pointages(self):
        """Rafraîchit la liste des pointages récents"""
        from datetime import date
        today = date.today()
        pointages = self.db_manager.get_pointages_by_date(today, today)
        
        # Prendre les 10 derniers
        pointages = pointages[-10:]
        pointages.reverse()
        
        self.table.setRowCount(len(pointages))
        
        for i, pointage in enumerate(pointages):
            # Heure
            dt = datetime.fromisoformat(pointage['timestamp'])
            time_item = QTableWidgetItem(dt.strftime("%H:%M:%S"))
            self.table.setItem(i, 0, time_item)
            
            # Nom
            name_item = QTableWidgetItem(pointage['employee_name'])
            self.table.setItem(i, 1, name_item)
            
            # Type
            type_item = QTableWidgetItem(pointage['type'])
            if pointage['type'] == 'ENTREE':
                type_item.setForeground(QColor('#2ecc71'))
            else:
                type_item.setForeground(QColor('#e74c3c'))
            self.table.setItem(i, 2, type_item)
            
            # Statut export
            status_item = QTableWidgetItem('✓ Exporté' if pointage['exported'] else 'En attente')
            status_item.setForeground(QColor('#95a5a6'))
            self.table.setItem(i, 3, status_item)
    
    def open_admin(self):
        """Ouvre le panneau d'administration"""
        from .admin_panel import AdminPanel
        
        # Créer un callback pour restaurer le mode normal
        def restore_callback():
            """Callback pour restaurer la lecture normale"""
            if self.rfid_reader and not self.rfid_reader.running:
                self.rfid_reader.start_reading(lambda code: self.rfid_signal.card_detected.emit(code))
                logger.info("Lecture RFID normale restaurée")
        
        self.admin_window = AdminPanel(self.db_manager, self.rfid_reader, self, restore_callback)
        self.admin_window.show()
    
    def closeEvent(self, event):
        """Événement de fermeture"""
        self.rfid_reader.disconnect()
        event.accept()



