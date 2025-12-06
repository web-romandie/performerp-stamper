"""
Module d'export des pointages en CSV
"""
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class CSVExporter:
    """Gère l'export des pointages en fichier CSV"""
    
    def __init__(self, export_dir: Path):
        """
        Initialise l'exporteur CSV
        
        Args:
            export_dir: Répertoire d'export
        """
        self.export_dir = export_dir
        self.export_dir.mkdir(exist_ok=True)
    
    def export_pointages(self, pointages: List[Dict], filename: str = None) -> str:
        """
        Exporte une liste de pointages en CSV
        
        Args:
            pointages: Liste des pointages à exporter
            filename: Nom du fichier (généré automatiquement si None)
        
        Returns:
            Chemin du fichier créé
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pointages_{timestamp}.csv"
        
        filepath = self.export_dir / filename
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['ID', 'Matricule', 'Nom', 'RFID', 'Date', 'Heure', 'Type']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
                
                writer.writeheader()
                
                for pointage in pointages:
                    # Parser la date et l'heure
                    try:
                        dt = datetime.fromisoformat(pointage['timestamp'])
                        date_str = dt.strftime("%d/%m/%Y")
                        heure_str = dt.strftime("%H:%M:%S")
                    except:
                        date_str = pointage['timestamp']
                        heure_str = ""
                    
                    writer.writerow({
                        'ID': pointage['id'],
                        'Matricule': pointage['employee_id'],
                        'Nom': pointage['employee_name'],
                        'RFID': pointage['rfid'],
                        'Date': date_str,
                        'Heure': heure_str,
                        'Type': pointage['type']
                    })
            
            logger.info(f"Export CSV réussi: {filepath} ({len(pointages)} pointages)")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export CSV: {e}")
            raise
    
    def export_hours_summary(self, hours_data: Dict, filename: str = None) -> str:
        """
        Exporte un résumé des heures en CSV
        
        Args:
            hours_data: Données des heures par employé
            filename: Nom du fichier (généré automatiquement si None)
        
        Returns:
            Chemin du fichier créé
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"resume_heures_{timestamp}.csv"
        
        filepath = self.export_dir / filename
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['Matricule', 'Total_Heures', 'Nombre_Pointages']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
                
                writer.writeheader()
                writer.writerow({
                    'Matricule': hours_data['employee_id'],
                    'Total_Heures': hours_data['total_hours'],
                    'Nombre_Pointages': hours_data['num_pointages']
                })
            
            logger.info(f"Export résumé heures réussi: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export résumé: {e}")
            raise



