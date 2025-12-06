"""
Panneau d'administration
"""
from datetime import date, datetime
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                             QDateEdit, QMessageBox, QTabWidget, QTextEdit, QComboBox,
                             QLineEdit, QGroupBox, QFrame)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QFont
import logging
import requests
import urllib3

# Désactiver les avertissements SSL pour les requêtes locales
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class AdminPanel(QMainWindow):
    """Panneau d'administration"""
    
    def __init__(self, db_manager, rfid_reader=None, parent=None, restore_rfid_callback=None):
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.rfid_reader = rfid_reader
        self.restore_rfid_callback = restore_rfid_callback  # Callback pour restaurer la lecture normale
        
        # Charger la configuration API
        try:
            from config import api_config
            self.api_url = api_config.API_URL
            self.id_compte = api_config.ACCOUNT_ID
            self.api_key = api_config.API_KEY
        except (ImportError, AttributeError) as e:
            logger.error(f"Configuration API manquante: {e}")
            raise RuntimeError("Fichier config/api_config.py requis avec API_URL, ACCOUNT_ID et API_KEY")
        
        self.init_ui()
    
    def get_api_headers(self):
        """Retourne les headers HTTP pour les appels API"""
        return {
            'X-API-Key': self.api_key,
            'X-Account-ID': str(self.id_compte)
        }
    
    def init_ui(self):
        """Initialise l'interface"""
        self.setWindowTitle("Panneau d'Administration")
        self.setMinimumSize(1000, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre
        title_label = QLabel("Administration du Système de Pointage")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Onglets
        tabs = QTabWidget()
        
        # Onglet Pointages
        pointages_tab = self.create_pointages_tab()
        tabs.addTab(pointages_tab, "Pointages")
        
        # Onglet Rapports
        reports_tab = self.create_reports_tab()
        tabs.addTab(reports_tab, "Rapports")
        
        # Onglet Export
        export_tab = self.create_export_tab()
        tabs.addTab(export_tab, "Export")
        
        # Onglet Configuration RFID
        if self.rfid_reader:
            rfid_tab = self.create_rfid_config_tab()
            tabs.addTab(rfid_tab, "Configuration RFID")
        
        main_layout.addWidget(tabs)
        
        # Bouton fermer
        close_button = QPushButton("Fermer")
        close_button.setFont(QFont("Arial", 12))
        close_button.setMinimumHeight(40)
        close_button.clicked.connect(self.close)
        main_layout.addWidget(close_button)
        
        central_widget.setLayout(main_layout)
    
    def create_pointages_tab(self):
        """Crée l'onglet des pointages"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Sélection de dates
        date_layout = QHBoxLayout()
        
        date_layout.addWidget(QLabel("Du:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("Au:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        date_layout.addWidget(self.end_date)
        
        refresh_button = QPushButton("Rafraîchir")
        refresh_button.clicked.connect(self.refresh_pointages_table)
        date_layout.addWidget(refresh_button)
        
        date_layout.addStretch()
        
        layout.addLayout(date_layout)
        
        # Table des pointages
        self.pointages_table = QTableWidget()
        self.pointages_table.setColumnCount(6)
        self.pointages_table.setHorizontalHeaderLabels([
            "Date/Heure", "Matricule", "Nom", "RFID", "Type", "Exporté"
        ])
        self.pointages_table.horizontalHeader().setStretchLastSection(True)
        self.pointages_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.pointages_table)
        
        widget.setLayout(layout)
        
        # Charger les données initiales
        self.refresh_pointages_table()
        
        return widget
    
    def create_reports_tab(self):
        """Crée l'onglet des rapports"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Zone de rapport
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setFont(QFont("Courier New", 10))
        layout.addWidget(self.report_text)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        daily_button = QPushButton("Rapport du jour")
        daily_button.clicked.connect(self.generate_daily_report)
        button_layout.addWidget(daily_button)
        
        weekly_button = QPushButton("Rapport de la semaine")
        weekly_button.clicked.connect(self.generate_weekly_report)
        button_layout.addWidget(weekly_button)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_export_tab(self):
        """Crée l'onglet d'export"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Instructions
        info_label = QLabel(
            "Exportez les pointages en fichier CSV et envoyez-les par FTP.\n"
            "Les pointages non exportés seront marqués comme exportés après l'envoi."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Statistiques
        self.export_stats = QLabel()
        self.export_stats.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.export_stats)
        
        self.update_export_stats()
        
        # Boutons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        export_csv_button = QPushButton("Exporter en CSV uniquement")
        export_csv_button.setMinimumHeight(50)
        export_csv_button.clicked.connect(self.export_csv_only)
        button_layout.addWidget(export_csv_button)
        
        export_ftp_button = QPushButton("Exporter et envoyer par FTP")
        export_ftp_button.setMinimumHeight(50)
        export_ftp_button.clicked.connect(self.export_and_send_ftp)
        button_layout.addWidget(export_ftp_button)
        
        test_ftp_button = QPushButton("Tester la connexion FTP")
        test_ftp_button.setMinimumHeight(50)
        test_ftp_button.clicked.connect(self.test_ftp_connection)
        button_layout.addWidget(test_ftp_button)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def refresh_pointages_table(self):
        """Rafraîchit la table des pointages"""
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        
        pointages = self.db_manager.get_pointages_by_date(start, end)
        
        self.pointages_table.setRowCount(len(pointages))
        
        for i, pointage in enumerate(pointages):
            dt = datetime.fromisoformat(pointage['timestamp'])
            
            self.pointages_table.setItem(i, 0, QTableWidgetItem(dt.strftime("%d/%m/%Y %H:%M:%S")))
            self.pointages_table.setItem(i, 1, QTableWidgetItem(pointage['employee_id']))
            self.pointages_table.setItem(i, 2, QTableWidgetItem(pointage['employee_name']))
            self.pointages_table.setItem(i, 3, QTableWidgetItem(pointage['rfid']))
            self.pointages_table.setItem(i, 4, QTableWidgetItem(pointage['type']))
            self.pointages_table.setItem(i, 5, QTableWidgetItem('Oui' if pointage['exported'] else 'Non'))
    
    def generate_daily_report(self):
        """Génère un rapport journalier"""
        today = date.today()
        pointages = self.db_manager.get_pointages_by_date(today, today)
        
        report = f"=== RAPPORT JOURNALIER - {today.strftime('%d/%m/%Y')} ===\n\n"
        report += f"Nombre total de pointages: {len(pointages)}\n\n"
        
        # Grouper par employé
        employees = {}
        for p in pointages:
            emp_id = p['employee_id']
            if emp_id not in employees:
                employees[emp_id] = {'name': p['employee_name'], 'pointages': []}
            employees[emp_id]['pointages'].append(p)
        
        for emp_id, data in employees.items():
            report += f"\n{data['name']} ({emp_id}):\n"
            for p in data['pointages']:
                dt = datetime.fromisoformat(p['timestamp'])
                report += f"  - {dt.strftime('%H:%M:%S')} : {p['type']}\n"
        
        self.report_text.setText(report)
    
    def generate_weekly_report(self):
        """Génère un rapport hebdomadaire"""
        from datetime import timedelta
        
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        pointages = self.db_manager.get_pointages_by_date(week_start, week_end)
        
        report = f"=== RAPPORT HEBDOMADAIRE ===\n"
        report += f"Du {week_start.strftime('%d/%m/%Y')} au {week_end.strftime('%d/%m/%Y')}\n\n"
        report += f"Nombre total de pointages: {len(pointages)}\n\n"
        
        # Grouper par employé
        employees = {}
        for p in pointages:
            emp_id = p['employee_id']
            if emp_id not in employees:
                employees[emp_id] = {'name': p['employee_name'], 'pointages': []}
            employees[emp_id]['pointages'].append(p)
        
        for emp_id, data in employees.items():
            hours_data = self.db_manager.get_employee_hours(emp_id, week_start, week_end)
            report += f"\n{data['name']} ({emp_id}):\n"
            report += f"  Total heures: {hours_data['total_hours']:.2f}h\n"
            report += f"  Nombre de pointages: {hours_data['num_pointages']}\n"
        
        self.report_text.setText(report)
    
    def update_export_stats(self):
        """Met à jour les statistiques d'export"""
        non_exported = self.db_manager.get_non_exported_pointages()
        self.export_stats.setText(f"Pointages en attente d'export: {len(non_exported)}")
    
    def export_csv_only(self):
        """Exporte uniquement en CSV"""
        from config.settings import EXPORTS_DIR
        from src.export import CSVExporter
        
        try:
            non_exported = self.db_manager.get_non_exported_pointages()
            
            if not non_exported:
                QMessageBox.information(self, "Export", "Aucun pointage à exporter.")
                return
            
            exporter = CSVExporter(EXPORTS_DIR)
            filepath = exporter.export_pointages(non_exported)
            
            QMessageBox.information(self, "Export réussi", 
                                  f"Export CSV réussi!\n\nFichier: {filepath}\n"
                                  f"Pointages exportés: {len(non_exported)}")
            
            # Marquer comme exportés
            ids = [p['id'] for p in non_exported]
            self.db_manager.mark_as_exported(ids)
            self.update_export_stats()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export:\n{str(e)}")
    
    def export_and_send_ftp(self):
        """Exporte et envoie par FTP"""
        from config.settings import EXPORTS_DIR, FTP_HOST, FTP_PORT, FTP_USER, FTP_PASSWORD, FTP_REMOTE_PATH
        from src.export import CSVExporter, FTPUploader
        
        try:
            # Vérifier la configuration FTP
            if not FTP_HOST or not FTP_USER:
                QMessageBox.warning(self, "Configuration manquante",
                                  "La configuration FTP est incomplète.\n"
                                  "Vérifiez le fichier .env")
                return
            
            non_exported = self.db_manager.get_non_exported_pointages()
            
            if not non_exported:
                QMessageBox.information(self, "Export", "Aucun pointage à exporter.")
                return
            
            # Export CSV
            exporter = CSVExporter(EXPORTS_DIR)
            filepath = exporter.export_pointages(non_exported)
            
            # Upload FTP
            uploader = FTPUploader(FTP_HOST, FTP_PORT, FTP_USER, FTP_PASSWORD, FTP_REMOTE_PATH)
            success = uploader.upload_file(filepath)
            
            if success:
                # Marquer comme exportés
                ids = [p['id'] for p in non_exported]
                self.db_manager.mark_as_exported(ids)
                self.update_export_stats()
                
                QMessageBox.information(self, "Export réussi",
                                      f"Export et envoi FTP réussis!\n\n"
                                      f"Fichier: {filepath}\n"
                                      f"Pointages exportés: {len(non_exported)}")
            else:
                QMessageBox.warning(self, "Erreur FTP",
                                  f"Export CSV réussi mais l'envoi FTP a échoué.\n\n"
                                  f"Fichier: {filepath}\n"
                                  f"Vérifiez les logs pour plus de détails.")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur:\n{str(e)}")
    
    def test_ftp_connection(self):
        """Teste la connexion FTP"""
        from config.settings import FTP_HOST, FTP_PORT, FTP_USER, FTP_PASSWORD, FTP_REMOTE_PATH
        from src.export import FTPUploader
        
        try:
            if not FTP_HOST or not FTP_USER:
                QMessageBox.warning(self, "Configuration manquante",
                                  "La configuration FTP est incomplète.\n"
                                  "Vérifiez le fichier .env")
                return
            
            uploader = FTPUploader(FTP_HOST, FTP_PORT, FTP_USER, FTP_PASSWORD, FTP_REMOTE_PATH)
            
            if uploader.test_connection():
                QMessageBox.information(self, "Test FTP",
                                      f"Connexion FTP réussie!\n\n"
                                      f"Hôte: {FTP_HOST}:{FTP_PORT}\n"
                                      f"Utilisateur: {FTP_USER}\n"
                                      f"Chemin distant: {FTP_REMOTE_PATH}")
            else:
                QMessageBox.warning(self, "Test FTP",
                                  "La connexion FTP a échoué.\n"
                                  "Vérifiez vos paramètres et les logs.")
        
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du test:\n{str(e)}")
    
    def create_rfid_config_tab(self):
        """Crée l'onglet de configuration RFID"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Variables pour stocker l'état
        self.rfid_employees = []
        self.rfid_selected_employee = None
        self.rfid_waiting_for_scan = False
        self.rfid_buffer = ''
        self.rfid_timeout = None
        
        # Section 1: Connexion à l'API
        api_group = QGroupBox("Connexion au serveur")
        api_layout = QVBoxLayout()
        
        # Afficher les informations de connexion (lecture seule)
        info_label = QLabel(f"URL de l'API: <b>{self.api_url}</b><br>ID du compte: <b>{self.id_compte}</b>")
        info_label.setStyleSheet("color: #666; padding: 5px;")
        api_layout.addWidget(info_label)
        
        # Bouton pour charger les employés
        load_layout = QHBoxLayout()
        self.rfid_load_btn = QPushButton("Charger les employés")
        self.rfid_load_btn.clicked.connect(self.load_rfid_employees)
        load_layout.addWidget(self.rfid_load_btn)
        load_layout.addStretch()
        api_layout.addLayout(load_layout)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # Section 2: Sélection de l'employé
        employee_group = QGroupBox("Sélection de l'employé")
        employee_layout = QVBoxLayout()
        
        self.rfid_employee_combo = QComboBox()
        self.rfid_employee_combo.setEnabled(False)
        self.rfid_employee_combo.currentIndexChanged.connect(self.on_rfid_employee_selected)
        employee_layout.addWidget(QLabel("Employé:"))
        employee_layout.addWidget(self.rfid_employee_combo)
        
        self.rfid_employee_info = QLabel("Aucun employé sélectionné")
        self.rfid_employee_info.setStyleSheet("color: gray; font-style: italic;")
        employee_layout.addWidget(self.rfid_employee_info)
        
        # Bouton pour retirer le badge (visible seulement si badge existant)
        self.rfid_remove_btn = QPushButton("🗑️ Retirer le badge RFID")
        self.rfid_remove_btn.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        self.rfid_remove_btn.setMinimumHeight(40)
        self.rfid_remove_btn.clicked.connect(self.remove_rfid_badge)
        self.rfid_remove_btn.setVisible(False)  # Caché par défaut
        employee_layout.addWidget(self.rfid_remove_btn)
        
        employee_group.setLayout(employee_layout)
        layout.addWidget(employee_group)
        
        # Section 3: Scan du badge
        scan_group = QGroupBox("Configuration du badge RFID")
        scan_layout = QVBoxLayout()
        
        # Status du lecteur
        self.rfid_reader_status = QLabel("Lecteur RFID: Vérification...")
        scan_layout.addWidget(self.rfid_reader_status)
        self.check_rfid_reader_status()
        
        # Boutons pour scanner et annuler
        scan_btn_layout = QHBoxLayout()
        
        self.rfid_scan_btn = QPushButton("Scannez le badge maintenant")
        self.rfid_scan_btn.setEnabled(False)
        self.rfid_scan_btn.setMinimumHeight(60)
        self.rfid_scan_btn.setFont(QFont("Arial", 14))
        self.rfid_scan_btn.clicked.connect(self.start_rfid_scanning)
        scan_btn_layout.addWidget(self.rfid_scan_btn)
        
        self.rfid_cancel_btn = QPushButton("Annuler")
        self.rfid_cancel_btn.setEnabled(False)
        self.rfid_cancel_btn.setMinimumHeight(60)
        self.rfid_cancel_btn.setFont(QFont("Arial", 12))
        self.rfid_cancel_btn.setMaximumWidth(150)
        self.rfid_cancel_btn.clicked.connect(self.cancel_rfid_scanning)
        scan_btn_layout.addWidget(self.rfid_cancel_btn)
        
        scan_layout.addLayout(scan_btn_layout)
        
        # Code RFID scanné
        rfid_layout = QHBoxLayout()
        rfid_layout.addWidget(QLabel("Code RFID:"))
        self.rfid_display = QLineEdit()
        self.rfid_display.setReadOnly(True)
        self.rfid_display.setPlaceholderText("En attente du scan...")
        rfid_layout.addWidget(self.rfid_display)
        scan_layout.addLayout(rfid_layout)
        
        # Bouton pour enregistrer
        self.rfid_save_btn = QPushButton("Enregistrer l'association")
        self.rfid_save_btn.setEnabled(False)
        self.rfid_save_btn.setMinimumHeight(50)
        self.rfid_save_btn.setFont(QFont("Arial", 12))
        self.rfid_save_btn.clicked.connect(self.save_rfid_association)
        scan_layout.addWidget(self.rfid_save_btn)
        
        scan_group.setLayout(scan_layout)
        layout.addWidget(scan_group)
        
        # Section 4: Log/Messages
        log_group = QGroupBox("Messages")
        log_layout = QVBoxLayout()
        
        self.rfid_log_display = QTextEdit()
        self.rfid_log_display.setReadOnly(True)
        self.rfid_log_display.setMaximumHeight(150)
        log_layout.addWidget(self.rfid_log_display)
        
        # Bouton pour regénérer manuellement le fichier
        regen_btn_layout = QHBoxLayout()
        regen_btn_layout.addStretch()
        self.rfid_regen_btn = QPushButton("🔄 Regénérer employees.json")
        self.rfid_regen_btn.setMinimumHeight(35)
        self.rfid_regen_btn.setStyleSheet("background-color: #3498db; color: white;")
        self.rfid_regen_btn.clicked.connect(self.manual_generate_employees_json)
        regen_btn_layout.addWidget(self.rfid_regen_btn)
        log_layout.addLayout(regen_btn_layout)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def check_rfid_reader_status(self):
        """Vérifie l'état du lecteur RFID"""
        if self.rfid_reader and self.rfid_reader.is_connected():
            self.rfid_reader_status.setText("✓ Lecteur RFID: Connecté")
            self.rfid_reader_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.rfid_reader_status.setText("✗ Lecteur RFID: Non connecté")
            self.rfid_reader_status.setStyleSheet("color: red; font-weight: bold;")
    
    def load_rfid_employees(self):
        """Charge la liste des employés depuis l'API"""
        api_url = self.api_url
        id_compte = str(self.id_compte)
        
        self.rfid_log(f"📡 Chargement des employés du compte {id_compte}...")
        self.rfid_load_btn.setEnabled(False)
        
        try:
            url = f"{api_url}/api_list_employees.php?id_compte={id_compte}"
            response = requests.get(url, headers=self.get_api_headers(), timeout=10, verify=False)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success'):
                self.rfid_employees = data.get('employees', [])
                self.rfid_employee_combo.clear()
                self.rfid_employee_combo.addItem("-- Sélectionnez un employé --", None)
                
                for emp in self.rfid_employees:
                    rfid_status = "✓" if emp.get('has_rfid') else "✗"
                    label = f"{emp['nom']} {emp['prenom']} [{rfid_status}]"
                    self.rfid_employee_combo.addItem(label, emp)
                
                self.rfid_employee_combo.setEnabled(True)
                self.rfid_log(f"✓ {len(self.rfid_employees)} employés chargés")
            else:
                error = data.get('error', 'Erreur inconnue')
                self.rfid_log(f"❌ Erreur API: {error}")
                QMessageBox.warning(self, "Erreur", f"Erreur lors du chargement:\n{error}")
        except Exception as e:
            self.rfid_log(f"❌ Erreur: {str(e)}")
            QMessageBox.critical(self, "Erreur", f"Impossible de se connecter à l'API:\n{str(e)}")
        finally:
            self.rfid_load_btn.setEnabled(True)
    
    def on_rfid_employee_selected(self, index):
        """Appelé quand un employé est sélectionné"""
        employee = self.rfid_employee_combo.currentData()
        
        if employee:
            self.rfid_selected_employee = employee
            info = f"Sélectionné: {employee['nom']} {employee['prenom']}"
            
            # Afficher le badge actuel s'il existe
            if employee.get('has_rfid') and employee.get('carte') and employee['carte'] != '0':
                info += f"\n✓ Badge RFID actuel: {employee['carte']}"
                info += "\n(Vous pouvez le remplacer ou le retirer)"
                # Afficher le bouton pour retirer le badge
                self.rfid_remove_btn.setVisible(True)
            else:
                info += "\n✗ Aucun badge RFID configuré"
                # Cacher le bouton pour retirer le badge
                self.rfid_remove_btn.setVisible(False)
            
            self.rfid_employee_info.setText(info)
            self.rfid_employee_info.setStyleSheet("color: black;")
            self.rfid_scan_btn.setEnabled(self.rfid_reader and self.rfid_reader.is_connected())
        else:
            self.rfid_selected_employee = None
            self.rfid_employee_info.setText("Aucun employé sélectionné")
            self.rfid_employee_info.setStyleSheet("color: gray; font-style: italic;")
            self.rfid_scan_btn.setEnabled(False)
            self.rfid_remove_btn.setVisible(False)
    
    def start_rfid_scanning(self):
        """Démarre l'attente du scan"""
        if not self.rfid_selected_employee:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord sélectionner un employé")
            return
        
        if not self.rfid_reader or not self.rfid_reader.is_connected():
            QMessageBox.critical(self, "Erreur", "Le lecteur RFID n'est pas connecté")
            return
        
        self.rfid_waiting_for_scan = True
        self.rfid_display.clear()
        self.rfid_scan_btn.setText("⏳ En attente du scan...")
        self.rfid_scan_btn.setStyleSheet("background-color: orange; color: white; font-weight: bold;")
        self.rfid_scan_btn.setEnabled(False)
        self.rfid_cancel_btn.setEnabled(True)
        self.rfid_save_btn.setEnabled(False)
        
        self.rfid_log(f"⏳ Scannez le badge pour {self.rfid_selected_employee['prenom']} {self.rfid_selected_employee['nom']}...")
        
        # Arrêter la lecture RFID principale et démarrer la nôtre
        if self.rfid_reader.running:
            self.rfid_reader.stop_reading()
            self.rfid_log("  → Lecture principale arrêtée")
        
        # Démarrer notre propre lecture
        self.rfid_reader.start_reading(self.on_rfid_badge_scanned)
        self.rfid_log("  → Mode configuration activé")
    
    def on_rfid_badge_scanned(self, rfid_code):
        """Appelé quand un badge est scanné"""
        try:
            if not self.rfid_waiting_for_scan:
                return
            
            self.rfid_waiting_for_scan = False
            rfid_code = rfid_code.strip()
            
            self.rfid_display.setText(rfid_code)
            self.rfid_scan_btn.setText("✓ Badge scanné!")
            self.rfid_scan_btn.setStyleSheet("background-color: green; color: white; font-weight: bold;")
            self.rfid_save_btn.setEnabled(True)
            
            self.rfid_log(f"✓ Badge scanné: {rfid_code}")
            
            # Arrêter notre lecture et redémarrer la lecture principale
            self.stop_rfid_config_mode()
            
            # Réactiver le bouton après 2 secondes
            QTimer.singleShot(2000, self.reset_rfid_scan_button)
            
        except Exception as e:
            logger.error(f"Erreur lors du scan du badge: {e}")
            self.rfid_log(f"❌ Erreur: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def reset_rfid_scan_button(self):
        """Réinitialise le bouton de scan"""
        self.rfid_scan_btn.setText("Scannez le badge maintenant")
        self.rfid_scan_btn.setStyleSheet("")
        self.rfid_scan_btn.setEnabled(True)
        self.rfid_cancel_btn.setEnabled(False)
    
    def cancel_rfid_scanning(self):
        """Annule le scan en cours"""
        if self.rfid_waiting_for_scan:
            self.rfid_waiting_for_scan = False
            self.rfid_log("❌ Scan annulé")
            self.stop_rfid_config_mode()
            self.reset_rfid_scan_button()
    
    def save_rfid_association(self):
        """Enregistre l'association badge/employé via l'API"""
        if not self.rfid_selected_employee:
            return
        
        rfid_code = self.rfid_display.text().strip()
        if not rfid_code:
            QMessageBox.warning(self, "Attention", "Aucun badge scanné")
            return
        
        api_url = self.api_url
        id_compte = str(self.id_compte)
        id_emp = self.rfid_selected_employee['id_emp']
        
        self.rfid_log(f"💾 Enregistrement de l'association...")
        self.rfid_save_btn.setEnabled(False)
        
        try:
            url = f"{api_url}/api_save_rfid.php"
            data = {
                'id_emp': id_emp,
                'id_compte': id_compte,
                'rfid_code': rfid_code
            }
            
            response = requests.post(url, json=data, headers=self.get_api_headers(), timeout=10, verify=False)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('success'):
                message = result.get('message', 'Badge RFID enregistré avec succès')
                self.rfid_log(f"✓ {message}")
                
                # Générer automatiquement le fichier employees.json
                self.generate_employees_json_file()
                
                QMessageBox.information(self, "Succès", message + "\n\nLe fichier employees.json a été mis à jour.")
                
                # Réinitialiser
                self.rfid_display.clear()
                self.rfid_waiting_for_scan = False
                self.load_rfid_employees()  # Recharger pour mettre à jour les statuts
            else:
                error = result.get('error', 'Erreur inconnue')
                self.rfid_log(f"❌ Erreur: {error}")
                
                # Vérifier si c'est un doublon
                duplicate_emp = result.get('duplicate_employee')
                if duplicate_emp:
                    # Message détaillé pour un doublon
                    msg = (f"⚠️ BADGE DÉJÀ ATTRIBUÉ\n\n"
                           f"Ce code RFID est déjà utilisé par:\n"
                           f"• {duplicate_emp['prenom']} {duplicate_emp['nom']}\n"
                           f"• ID: {duplicate_emp['id_emp']}\n\n"
                           f"Code RFID: {rfid_code}\n\n"
                           f"Veuillez utiliser un autre badge ou retirer d'abord\n"
                           f"ce badge de l'autre employé.")
                    QMessageBox.warning(self, "Badge déjà attribué", msg)
                    self.rfid_log(f"⚠️ Badge utilisé par: {duplicate_emp['prenom']} {duplicate_emp['nom']}")
                else:
                    # Message d'erreur générique
                    QMessageBox.warning(self, "Erreur", f"Erreur lors de l'enregistrement:\n\n{error}")
        except Exception as e:
            self.rfid_log(f"❌ Erreur: {str(e)}")
            QMessageBox.critical(self, "Erreur", f"Impossible de se connecter à l'API:\n{str(e)}")
        finally:
            self.rfid_save_btn.setEnabled(True)
    
    def rfid_log(self, message):
        """Ajoute un message au log RFID"""
        self.rfid_log_display.append(message)
        cursor = self.rfid_log_display.textCursor()
        cursor.movePosition(cursor.End)
        self.rfid_log_display.setTextCursor(cursor)
    
    def generate_employees_json_file(self):
        """Génère et télécharge le fichier employees.json depuis l'API"""
        try:
            api_url = self.api_url
            id_compte = str(self.id_compte)
            
            self.rfid_log("📄 Génération du fichier employees.json...")
            
            # Télécharger le fichier depuis l'API
            url = f"{api_url}/api_download_employees_json.php?id_compte={id_compte}"
            response = requests.get(url, headers=self.get_api_headers(), timeout=10, verify=False)
            response.raise_for_status()
            
            # Sauvegarder dans config/employees.json
            import os
            from pathlib import Path
            
            # Trouver le chemin du fichier de configuration
            config_dir = Path(__file__).parent.parent.parent / 'config'
            employees_file = config_dir / 'employees.json'
            
            # Écrire le contenu
            with open(employees_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Vérifier le nombre d'employés
            import json
            data = json.loads(response.text)
            employee_count = len(data.get('employees', []))
            
            self.rfid_log(f"✓ Fichier employees.json généré avec {employee_count} employé(s)")
            self.rfid_log(f"  Emplacement: {employees_file}")
            logger.info(f"Fichier employees.json mis à jour: {employees_file}")
            
            # Demander à la fenêtre principale de recharger le fichier
            reload_success = False
            if self.parent():
                parent_window = self.parent()
                if hasattr(parent_window, 'reload_employees'):
                    try:
                        parent_window.reload_employees()
                        self.rfid_log("✓ Application mise à jour (rechargement automatique)")
                        reload_success = True
                    except Exception as e:
                        logger.error(f"Erreur lors du rechargement dans l'application: {e}")
                        self.rfid_log(f"⚠️ Rechargement automatique échoué: {str(e)}")
            
            if not reload_success:
                self.rfid_log("ℹ️ Fermez et relancez l'application pour prendre en compte les changements")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du fichier employees.json: {e}")
            self.rfid_log(f"⚠️ Erreur génération fichier: {str(e)}")
            # Ne pas bloquer l'opération principale si la génération échoue
            return False
    
    def manual_generate_employees_json(self):
        """Génère manuellement le fichier employees.json"""
        self.rfid_regen_btn.setEnabled(False)
        success = self.generate_employees_json_file()
        self.rfid_regen_btn.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "Succès", "Le fichier employees.json a été généré avec succès !")
        else:
            QMessageBox.warning(self, "Erreur", "Erreur lors de la génération du fichier.\nConsultez les messages pour plus de détails.")
    
    def remove_rfid_badge(self):
        """Retire le badge RFID d'un employé"""
        if not self.rfid_selected_employee:
            return
        
        # Vérifier qu'il y a bien un badge
        if not self.rfid_selected_employee.get('has_rfid') or not self.rfid_selected_employee.get('carte') or self.rfid_selected_employee['carte'] == '0':
            QMessageBox.warning(self, "Attention", "Cet employé n'a pas de badge RFID configuré")
            return
        
        employee_name = f"{self.rfid_selected_employee['prenom']} {self.rfid_selected_employee['nom']}"
        rfid_code = self.rfid_selected_employee['carte']
        
        # Demander confirmation
        reply = QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir retirer le badge RFID de :\n\n"
            f"• Employé: {employee_name}\n"
            f"• Badge actuel: {rfid_code}\n\n"
            f"Cette action peut être annulée en réattribuant un badge.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            self.rfid_log("❌ Suppression annulée par l'utilisateur")
            return
        
        api_url = self.api_url
        id_compte = str(self.id_compte)
        id_emp = self.rfid_selected_employee['id_emp']
        
        self.rfid_log(f"🗑️ Retrait du badge RFID pour {employee_name}...")
        self.rfid_remove_btn.setEnabled(False)
        
        try:
            url = f"{api_url}/api_remove_rfid.php"
            data = {
                'id_emp': id_emp,
                'id_compte': id_compte
            }
            
            response = requests.post(url, json=data, headers=self.get_api_headers(), timeout=10, verify=False)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('success'):
                message = result.get('message', 'Badge RFID retiré avec succès')
                old_code = result.get('old_rfid_code', rfid_code)
                self.rfid_log(f"✓ {message}")
                self.rfid_log(f"  Ancien code retiré: {old_code}")
                
                # Générer automatiquement le fichier employees.json
                self.generate_employees_json_file()
                
                QMessageBox.information(self, "Succès", message + "\n\nLe fichier employees.json a été mis à jour.")
                
                # Réinitialiser et recharger
                self.rfid_display.clear()
                self.rfid_waiting_for_scan = False
                self.load_rfid_employees()  # Recharger pour mettre à jour les statuts
            else:
                error = result.get('error', 'Erreur inconnue')
                self.rfid_log(f"❌ Erreur: {error}")
                QMessageBox.warning(self, "Erreur", f"Erreur lors du retrait:\n\n{error}")
                
        except Exception as e:
            self.rfid_log(f"❌ Erreur: {str(e)}")
            QMessageBox.critical(self, "Erreur", f"Impossible de se connecter à l'API:\n\n{str(e)}")
        finally:
            self.rfid_remove_btn.setEnabled(True)
    
    def stop_rfid_config_mode(self):
        """Arrête le mode configuration et restaure le mode normal"""
        try:
            if self.rfid_reader and self.rfid_reader.running:
                self.rfid_reader.stop_reading()
                self.rfid_log("  → Mode configuration désactivé")
            
            # Restaurer la lecture normale si le callback est disponible
            if self.restore_rfid_callback:
                QTimer.singleShot(500, self.restore_rfid_callback)  # Petit délai pour s'assurer que l'arrêt est complet
                self.rfid_log("  → Lecture principale restaurée")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt du mode config: {e}")
            self.rfid_log(f"  ⚠️ Attention: {str(e)}")
    
    def closeEvent(self, event):
        """Appelé à la fermeture du panneau d'administration"""
        try:
            # S'assurer que le lecteur est arrêté
            if self.rfid_reader and self.rfid_reader.running:
                self.rfid_reader.stop_reading()
                logger.info("Lecteur RFID arrêté lors de la fermeture du panneau admin")
            
            # Restaurer le mode normal
            if self.restore_rfid_callback:
                QTimer.singleShot(500, self.restore_rfid_callback)
                logger.info("Restauration de la lecture RFID normale programmée")
                
        except Exception as e:
            logger.error(f"Erreur lors de la fermeture du panneau admin: {e}")
        
        event.accept()



