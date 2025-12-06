#!/usr/bin/env python3
"""
Script de test pour le panneau de configuration RFID
"""
import sys
from PyQt5.QtWidgets import QApplication
from src.gui.rfid_config_panel import RFIDConfigPanel

def main():
    app = QApplication(sys.argv)
    
    # Créer une fenêtre de test sans lecteur RFID
    print("Création du panneau de configuration RFID...")
    window = RFIDConfigPanel(rfid_reader=None)
    
    print("Affichage de la fenêtre...")
    window.show()
    
    print("Fenêtre affichée ! Appuyez sur Fermer pour quitter.")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

