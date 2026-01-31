"""
Interface de configuration RFID
Permet d'associer un badge RFID à un employé via l'API du site web
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QLineEdit, QTextEdit,
    QGroupBox, QMessageBox, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
import requests
import logging

logger = logging.getLogger(__name__)


class RFIDConfigPanel(QWidget):
    """Panneau de configuration RFID"""
    
    # Signals
    rfid_configured = pyqtSignal(dict)  # Émis quand un badge est configuré
    
    def __init__(self, rfid_reader, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.rfid_reader = rfid_reader
        self.employees = []
        self.selected_employee = None
        self.waiting_for_scan = False
        
        # Configuration de l'API
        self.api_url = "https://prestest.ddev.site"  # À modifier selon votre configuration
        
        self.init_ui()
        
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        # Titre de la fenêtre
        self.setWindowTitle("Configuration des badges RFID")
        
        layout = QVBoxLayout()
        
        # Titre
        title = QLabel("Configuration des badges RFID")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Section 1: Configuration de l'API
        api_group = QGroupBox("Connexion au serveur")
        api_layout = QVBoxLayout()
        
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL de l'API:"))
        self.url_input = QLineEdit(self.api_url)
        self.url_input.setPlaceholderText("https://prestest.ddev.site")
        url_layout.addWidget(self.url_input)
        api_layout.addLayout(url_layout)
        
        compte_layout = QHBoxLayout()
        compte_layout.addWidget(QLabel("ID du compte:"))
        self.compte_input = QLineEdit("2")
        self.compte_input.setPlaceholderText("ID du compte (ex: 2)")
        compte_layout.addWidget(self.compte_input)
        
        self.load_employees_btn = QPushButton("Charger les employés")
        self.load_employees_btn.clicked.connect(self.load_employees)
        compte_layout.addWidget(self.load_employees_btn)
        api_layout.addLayout(compte_layout)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # Section 2: Sélection de l'employé
        employee_group = QGroupBox("Sélection de l'employé")
        employee_layout = QVBoxLayout()
        
        self.employee_combo = QComboBox()
        self.employee_combo.setEnabled(False)
        self.employee_combo.currentIndexChanged.connect(self.on_employee_selected)
        employee_layout.addWidget(QLabel("Employé:"))
        employee_layout.addWidget(self.employee_combo)
        
        # Info sur l'employé sélectionné
        self.employee_info = QLabel("Aucun employé sélectionné")
        self.employee_info.setStyleSheet("color: gray; font-style: italic;")
        employee_layout.addWidget(self.employee_info)
        
        employee_group.setLayout(employee_layout)
        layout.addWidget(employee_group)
        
        # Section 3: Scan du badge (design compact 2 colonnes)
        scan_group = QGroupBox("Configuration du badge RFID")
        scan_layout = QVBoxLayout()
        scan_layout.setSpacing(10)
        
        # Status du lecteur (en haut, pleine largeur)
        self.reader_status = QLabel("Lecteur RFID: Non connecté")
        self.reader_status.setStyleSheet("color: red; font-weight: bold;")
        self.reader_status.setAlignment(Qt.AlignCenter)
        scan_layout.addWidget(self.reader_status)
        
        # Layout en 2 colonnes pour boutons et affichage RFID
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        
        # Colonne 1: Bouton scanner (compact)
        self.scan_btn = QPushButton("🔍 Scanner le badge")
        self.scan_btn.setEnabled(False)
        self.scan_btn.setMinimumHeight(50)
        self.scan_btn.setMaximumWidth(250)
        self.scan_btn.clicked.connect(self.start_scanning)
        grid_layout.addWidget(self.scan_btn, 0, 0)
        
        # Colonne 2: Bouton enregistrer (compact)
        self.save_btn = QPushButton("💾 Enregistrer")
        self.save_btn.setEnabled(False)
        self.save_btn.setMinimumHeight(50)
        self.save_btn.setMaximumWidth(250)
        self.save_btn.clicked.connect(self.save_rfid_association)
        grid_layout.addWidget(self.save_btn, 0, 1)
        
        scan_layout.addLayout(grid_layout)
        
        # Code RFID scanné (sous les boutons, pleine largeur)
        rfid_container = QHBoxLayout()
        rfid_container.setSpacing(10)
        rfid_label = QLabel("Code RFID:")
        rfid_label.setMinimumWidth(80)
        self.rfid_display = QLineEdit()
        self.rfid_display.setReadOnly(True)
        self.rfid_display.setPlaceholderText("En attente...")
        self.rfid_display.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 13px;
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
        rfid_container.addWidget(rfid_label)
        rfid_container.addWidget(self.rfid_display)
        scan_layout.addLayout(rfid_container)
        
        scan_group.setLayout(scan_layout)
        layout.addWidget(scan_group)
        
        # Section 4: Log/Messages
        log_group = QGroupBox("Messages")
        log_layout = QVBoxLayout()
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMaximumHeight(150)
        log_layout.addWidget(self.log_display)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Bouton fermer
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Définir une taille fixe pour la fenêtre
        self.setMinimumSize(700, 800)
        self.resize(700, 800)
        
        # Vérifier l'état du lecteur RFID
        self.check_reader_status()
        
    def showEvent(self, event):
        """Appelé quand la fenêtre est affichée"""
        super().showEvent(event)
        # Centrer la fenêtre sur l'écran
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
        # Forcer l'activation et le focus
        self.raise_()
        self.activateWindow()
        
    def check_reader_status(self):
        """Vérifie l'état du lecteur RFID"""
        if self.rfid_reader and self.rfid_reader.is_connected():
            self.reader_status.setText("Lecteur RFID: Connecté ✓")
            self.reader_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.reader_status.setText("Lecteur RFID: Non connecté")
            self.reader_status.setStyleSheet("color: red; font-weight: bold;")
            
    def load_employees(self):
        """Charge la liste des employés depuis l'API"""
        api_url = self.url_input.text().strip()
        id_compte = self.compte_input.text().strip()
        
        if not api_url or not id_compte:
            self.log("❌ Veuillez entrer l'URL de l'API et l'ID du compte")
            return
        
        self.log(f"📡 Chargement des employés du compte {id_compte}...")
        self.load_employees_btn.setEnabled(False)
        
        try:
            # Appel à l'API
            url = f"{api_url}/api_list_employees.php?id_compte={id_compte}"
            response = requests.get(url, timeout=10, verify=False)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success'):
                self.employees = data.get('employees', [])
                self.employee_combo.clear()
                self.employee_combo.addItem("-- Sélectionnez un employé --", None)
                
                for emp in self.employees:
                    rfid_status = "✓" if emp.get('has_rfid') else "✗"
                    label = f"{emp['nom']} {emp['prenom']} [{rfid_status}]"
                    self.employee_combo.addItem(label, emp)
                
                self.employee_combo.setEnabled(True)
                self.log(f"✓ {len(self.employees)} employés chargés")
                
            else:
                error = data.get('error', 'Erreur inconnue')
                self.log(f"❌ Erreur API: {error}")
                QMessageBox.warning(self, "Erreur", f"Erreur lors du chargement:\n{error}")
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Erreur de connexion: {str(e)}")
            QMessageBox.critical(self, "Erreur", f"Impossible de se connecter à l'API:\n{str(e)}")
        except Exception as e:
            self.log(f"❌ Erreur: {str(e)}")
            logger.error(f"Erreur lors du chargement des employés: {e}")
        finally:
            self.load_employees_btn.setEnabled(True)
            
    def on_employee_selected(self, index):
        """Appelé quand un employé est sélectionné"""
        employee = self.employee_combo.currentData()
        
        if employee:
            self.selected_employee = employee
            info = f"Sélectionné: {employee['nom']} {employee['prenom']}"
            if employee.get('has_rfid') and employee.get('rfid'):
                info += f"\n⚠️ Badge RFID déjà configuré: {employee.get('rfid')}"
                info += "\n(Sera remplacé si vous scannez un nouveau badge)"
            self.employee_info.setText(info)
            self.employee_info.setStyleSheet("color: black;")
            self.scan_btn.setEnabled(self.rfid_reader and self.rfid_reader.is_connected())
        else:
            self.selected_employee = None
            self.employee_info.setText("Aucun employé sélectionné")
            self.employee_info.setStyleSheet("color: gray; font-style: italic;")
            self.scan_btn.setEnabled(False)
            
    def start_scanning(self):
        """Démarre l'attente du scan"""
        if not self.selected_employee:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord sélectionner un employé")
            return
            
        if not self.rfid_reader or not self.rfid_reader.is_connected():
            QMessageBox.critical(self, "Erreur", "Le lecteur RFID n'est pas connecté")
            return
        
        self.waiting_for_scan = True
        self.rfid_display.clear()
        self.rfid_display.setPlaceholderText("Scannez maintenant...")
        self.scan_btn.setText("⏳ En attente...")
        self.scan_btn.setStyleSheet("background-color: orange; color: white; font-weight: bold;")
        self.scan_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        
        self.log(f"⏳ Scannez le badge pour {self.selected_employee['prenom']} {self.selected_employee['nom']}...")
        
        # Démarrer la lecture RFID
        if not self.rfid_reader.running:
            self.rfid_reader.start_reading(self.on_rfid_scanned)
        
    def on_rfid_scanned(self, rfid_code):
        """Appelé quand un badge est scanné"""
        if not self.waiting_for_scan:
            return
            
        self.waiting_for_scan = False
        
        # Nettoyer le code
        rfid_code = rfid_code.strip()
        
        self.rfid_display.setText(rfid_code)
        self.scan_btn.setText("✓ Badge scanné!")
        self.scan_btn.setStyleSheet("background-color: green; color: white; font-weight: bold;")
        self.save_btn.setEnabled(True)
        
        self.log(f"✓ Badge scanné: {rfid_code}")
        
        # Réactiver le bouton après 2 secondes
        QTimer.singleShot(2000, self.reset_scan_button)
        
    def reset_scan_button(self):
        """Réinitialise le bouton de scan"""
        self.scan_btn.setText("🔍 Scanner le badge")
        self.scan_btn.setStyleSheet("")
        self.scan_btn.setEnabled(True)
        
    def save_rfid_association(self):
        """Enregistre l'association badge/employé via l'API"""
        if not self.selected_employee:
            return
            
        rfid_code = self.rfid_display.text().strip()
        if not rfid_code:
            QMessageBox.warning(self, "Attention", "Aucun badge scanné")
            return
        
        api_url = self.url_input.text().strip()
        id_compte = self.compte_input.text().strip()
        id_emp = self.selected_employee['id_emp']
        
        self.log(f"💾 Enregistrement de l'association...")
        self.save_btn.setEnabled(False)
        
        try:
            # Appel à l'API
            url = f"{api_url}/api_save_rfid.php"
            data = {
                'id_emp': id_emp,
                'id_compte': id_compte,
                'rfid_code': rfid_code
            }
            
            response = requests.post(url, json=data, timeout=10, verify=False)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('success'):
                message = result.get('message', 'Badge RFID enregistré avec succès')
                self.log(f"✓ {message}")
                QMessageBox.information(self, "Succès", message)
                
                # Émettre le signal
                self.rfid_configured.emit({
                    'employee': self.selected_employee,
                    'rfid_code': rfid_code
                })
                
                # Réinitialiser
                self.rfid_display.clear()
                self.load_employees()  # Recharger pour mettre à jour les statuts
                
            else:
                error = result.get('error', 'Erreur inconnue')
                self.log(f"❌ Erreur: {error}")
                QMessageBox.warning(self, "Erreur", f"Erreur lors de l'enregistrement:\n{error}")
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Erreur de connexion: {str(e)}")
            QMessageBox.critical(self, "Erreur", f"Impossible de se connecter à l'API:\n{str(e)}")
        except Exception as e:
            self.log(f"❌ Erreur: {str(e)}")
            logger.error(f"Erreur lors de l'enregistrement: {e}")
        finally:
            self.save_btn.setEnabled(True)
            
    def log(self, message):
        """Ajoute un message au log"""
        self.log_display.append(message)
        # Auto-scroll
        cursor = self.log_display.textCursor()
        cursor.movePosition(cursor.End)
        self.log_display.setTextCursor(cursor)
        
    def closeEvent(self, event):
        """Appelé à la fermeture de la fenêtre"""
        # Arrêter la lecture RFID si elle est en cours
        if self.rfid_reader and self.rfid_reader.running:
            self.rfid_reader.stop_reading()
        event.accept()

