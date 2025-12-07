"""
Simulateur RFID pour tester l'application sans lecteur physique

Utilisation: python test_rfid_simulator.py

Ce script simule un lecteur RFID en lisant les codes depuis le clavier.
Utile pour le développement et les tests.
"""
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from src.rfid import RFIDReader


class RFIDSimulator(RFIDReader):
    """Simulateur de lecteur RFID pour tests"""
    
    def __init__(self):
        """Initialise le simulateur"""
        # Ne pas appeler __init__ du parent pour éviter la connexion série
        self.running = False
        self.callback = None
        print("=" * 60)
        print("SIMULATEUR RFID - Mode Test")
        print("=" * 60)
        print()
        print("Le simulateur remplace le lecteur RFID physique.")
        print("Entrez les codes RFID manuellement pour tester.")
        print()
    
    def connect(self):
        """Simule la connexion"""
        print("✓ Simulateur RFID connecté")
        print()
        return True
    
    def disconnect(self):
        """Simule la déconnexion"""
        print("\n✓ Simulateur RFID déconnecté")
    
    def is_connected(self):
        """Simule l'état de connexion"""
        return True
    
    def start_reading(self, callback):
        """Démarre la simulation de lecture"""
        self.callback = callback
        self.running = True
        print("Mode manuel activé. Vous pouvez scanner des badges.")
        print("Codes RFID de test disponibles :")
        print("  - DEMO123456 (Jean Dupont - EMP001)")
        print("  - DEMO789012 (Marie Martin - EMP002)")
        print()
    
    def stop_reading(self):
        """Arrête la simulation"""
        self.running = False
    
    def simulate_scan(self, rfid_code):
        """Simule le scan d'une carte"""
        if self.callback and self.running:
            print(f"\n→ Simulation scan: {rfid_code}")
            self.callback(rfid_code)


def create_test_app():
    """Crée une application de test avec le simulateur"""
    import logging
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QLabel
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
    
    from config import settings
    from src.database import DatabaseManager
    from src.gui import MainWindow
    
    # Configuration du logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Chargement de l'application de test...")
    print()
    
    # Initialiser la base de données
    db_manager = DatabaseManager(str(settings.DATABASE_PATH))
    
    # Créer le simulateur RFID
    rfid_simulator = RFIDSimulator()
    
    # Créer l'application Qt
    app = QApplication(sys.argv)
    
    # Créer la fenêtre principale
    main_window = MainWindow(db_manager, rfid_simulator, settings.EMPLOYEES_FILE)
    
    # Créer une fenêtre de contrôle pour le simulateur
    class SimulatorControl(QMainWindow):
        """Fenêtre de contrôle du simulateur"""
        
        def __init__(self, simulator):
            super().__init__()
            self.simulator = simulator
            self.init_ui()
        
        def init_ui(self):
            self.setWindowTitle("Contrôle Simulateur RFID")
            self.setGeometry(100, 100, 400, 200)
            
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            layout = QVBoxLayout()
            
            # Titre
            title = QLabel("Simulateur de Lecteur RFID")
            title.setFont(QFont("Arial", 16, QFont.Bold))
            title.setAlignment(Qt.AlignCenter)
            layout.addWidget(title)
            
            # Instructions
            instructions = QLabel("Entrez un code RFID et cliquez sur Scanner")
            instructions.setAlignment(Qt.AlignCenter)
            layout.addWidget(instructions)
            
            # Champ de saisie
            self.rfid_input = QLineEdit()
            self.rfid_input.setPlaceholderText("Code RFID (ex: DEMO123456)")
            self.rfid_input.setFont(QFont("Arial", 12))
            self.rfid_input.returnPressed.connect(self.scan_card)
            layout.addWidget(self.rfid_input)
            
            # Boutons rapides
            quick_layout = QVBoxLayout()
            
            btn1 = QPushButton("Scanner: Jean Dupont (DEMO123456)")
            btn1.clicked.connect(lambda: self.quick_scan("DEMO123456"))
            quick_layout.addWidget(btn1)
            
            btn2 = QPushButton("Scanner: Marie Martin (DEMO789012)")
            btn2.clicked.connect(lambda: self.quick_scan("DEMO789012"))
            quick_layout.addWidget(btn2)
            
            layout.addLayout(quick_layout)
            
            # Bouton scanner
            scan_button = QPushButton("Scanner le code saisi")
            scan_button.setFont(QFont("Arial", 12))
            scan_button.clicked.connect(self.scan_card)
            layout.addWidget(scan_button)
            
            central_widget.setLayout(layout)
        
        def scan_card(self):
            """Simule le scan d'une carte"""
            rfid_code = self.rfid_input.text().strip()
            if rfid_code:
                self.simulator.simulate_scan(rfid_code)
                self.rfid_input.clear()
                self.rfid_input.setFocus()
        
        def quick_scan(self, rfid_code):
            """Scan rapide avec un code prédéfini"""
            self.simulator.simulate_scan(rfid_code)
    
    # Créer et afficher la fenêtre de contrôle
    control_window = SimulatorControl(rfid_simulator)
    control_window.show()
    
    # Afficher la fenêtre principale
    main_window.show()
    
    print("\n✓ Application de test lancée")
    print("✓ Utilisez la fenêtre 'Contrôle Simulateur RFID' pour scanner des badges")
    print()
    
    return app.exec_()


if __name__ == "__main__":
    try:
        sys.exit(create_test_app())
    except Exception as e:
        print(f"\n✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)




