"""
Gestionnaire de base de données pour le système de pointage
"""
import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gère toutes les opérations de base de données"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Crée une connexion à la base de données"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialise les tables de la base de données"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table des pointages
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pointages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                employee_name TEXT NOT NULL,
                rfid TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                type TEXT NOT NULL,
                exported INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Index pour améliorer les performances
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_employee_id ON pointages(employee_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON pointages(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_exported ON pointages(exported)
        """)
        
        conn.commit()
        conn.close()
        logger.info("Base de données initialisée")
    
    def add_pointage(self, employee_id: str, employee_name: str, rfid: str, pointage_type: str) -> int:
        """
        Ajoute un pointage
        
        Args:
            employee_id: ID de l'employé
            employee_name: Nom de l'employé
            rfid: Code RFID
            pointage_type: Type de pointage ('ENTREE' ou 'SORTIE')
        
        Returns:
            ID du pointage créé
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        timestamp = datetime.now()
        
        cursor.execute("""
            INSERT INTO pointages (employee_id, employee_name, rfid, timestamp, type)
            VALUES (?, ?, ?, ?, ?)
        """, (employee_id, employee_name, rfid, timestamp, pointage_type))
        
        pointage_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Pointage ajouté: {employee_name} - {pointage_type} - {timestamp}")
        return pointage_id
    
    def get_last_pointage(self, employee_id: str) -> Optional[Dict]:
        """
        Récupère le dernier pointage d'un employé
        
        Args:
            employee_id: ID de l'employé
        
        Returns:
            Dictionnaire avec les infos du pointage ou None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, employee_id, employee_name, rfid, timestamp, type
            FROM pointages
            WHERE employee_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (employee_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'employee_id': row[1],
                'employee_name': row[2],
                'rfid': row[3],
                'timestamp': row[4],
                'type': row[5]
            }
        return None
    
    def get_pointages_by_date(self, start_date: date, end_date: date) -> List[Dict]:
        """
        Récupère tous les pointages entre deux dates
        
        Args:
            start_date: Date de début
            end_date: Date de fin
        
        Returns:
            Liste de dictionnaires avec les pointages
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, employee_id, employee_name, rfid, timestamp, type, exported
            FROM pointages
            WHERE DATE(timestamp) BETWEEN ? AND ?
            ORDER BY timestamp
        """, (start_date, end_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        pointages = []
        for row in rows:
            pointages.append({
                'id': row[0],
                'employee_id': row[1],
                'employee_name': row[2],
                'rfid': row[3],
                'timestamp': row[4],
                'type': row[5],
                'exported': row[6]
            })
        
        return pointages
    
    def get_non_exported_pointages(self) -> List[Dict]:
        """
        Récupère tous les pointages non exportés
        
        Returns:
            Liste de dictionnaires avec les pointages
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, employee_id, employee_name, rfid, timestamp, type
            FROM pointages
            WHERE exported = 0
            ORDER BY timestamp
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        pointages = []
        for row in rows:
            pointages.append({
                'id': row[0],
                'employee_id': row[1],
                'employee_name': row[2],
                'rfid': row[3],
                'timestamp': row[4],
                'type': row[5]
            })
        
        return pointages
    
    def mark_as_exported(self, pointage_ids: List[int]):
        """
        Marque des pointages comme exportés
        
        Args:
            pointage_ids: Liste des IDs de pointages à marquer
        """
        if not pointage_ids:
            return
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        placeholders = ','.join(['?'] * len(pointage_ids))
        cursor.execute(f"""
            UPDATE pointages
            SET exported = 1
            WHERE id IN ({placeholders})
        """, pointage_ids)
        
        conn.commit()
        conn.close()
        
        logger.info(f"{len(pointage_ids)} pointages marqués comme exportés")
    
    def get_employee_hours(self, employee_id: str, start_date: date, end_date: date) -> Dict:
        """
        Calcule les heures travaillées pour un employé
        
        Args:
            employee_id: ID de l'employé
            start_date: Date de début
            end_date: Date de fin
        
        Returns:
            Dictionnaire avec les statistiques
        """
        pointages = self.get_pointages_by_date(start_date, end_date)
        pointages = [p for p in pointages if p['employee_id'] == employee_id]
        
        total_hours = 0
        days = {}
        
        for i in range(0, len(pointages) - 1, 2):
            if pointages[i]['type'] == 'ENTREE' and i + 1 < len(pointages):
                if pointages[i + 1]['type'] == 'SORTIE':
                    entry_time = datetime.fromisoformat(pointages[i]['timestamp'])
                    exit_time = datetime.fromisoformat(pointages[i + 1]['timestamp'])
                    duration = (exit_time - entry_time).total_seconds() / 3600
                    total_hours += duration
                    
                    day_key = entry_time.date()
                    if day_key not in days:
                        days[day_key] = 0
                    days[day_key] += duration
        
        return {
            'employee_id': employee_id,
            'total_hours': round(total_hours, 2),
            'days': days,
            'num_pointages': len(pointages)
        }



