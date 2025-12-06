"""
Gestionnaire de lecteur RFID
"""
import serial
import serial.tools.list_ports
import threading
import time
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class RFIDReader:
    """Gère la lecture des cartes RFID"""
    
    def __init__(self, port: str = "", baudrate: int = 9600, timeout: float = 1.0):
        """
        Initialise le lecteur RFID
        
        Args:
            port: Port série (laissez vide pour auto-détection)
            baudrate: Vitesse de communication
            timeout: Timeout de lecture
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection: Optional[serial.Serial] = None
        self.running = False
        self.read_thread: Optional[threading.Thread] = None
        self.callback: Optional[Callable] = None
        
    def list_available_ports(self):
        """Liste les ports série disponibles"""
        ports = serial.tools.list_ports.comports()
        available_ports = []
        for port in ports:
            available_ports.append({
                'device': port.device,
                'description': port.description,
                'hwid': port.hwid
            })
        return available_ports
    
    def auto_detect_port(self) -> Optional[str]:
        """
        Tente de détecter automatiquement le port du lecteur RFID
        
        Returns:
            Port détecté ou None
        """
        ports = self.list_available_ports()
        
        # Chercher des mots-clés communs pour les lecteurs RFID
        keywords = ['USB', 'Serial', 'UART', 'CH340', 'CP2102', 'FTDI', 'ACM']
        
        for port_info in ports:
            description = port_info['description'].upper()
            hwid = port_info['hwid'].upper()
            
            for keyword in keywords:
                if keyword in description or keyword in hwid:
                    logger.info(f"Port RFID détecté: {port_info['device']} - {port_info['description']}")
                    return port_info['device']
        
        # Si aucun port trouvé avec mots-clés, retourner le premier disponible
        if ports:
            logger.warning(f"Aucun port RFID identifié, utilisation du premier port: {ports[0]['device']}")
            return ports[0]['device']
        
        logger.error("Aucun port série disponible")
        return None
    
    def connect(self) -> bool:
        """
        Connecte au lecteur RFID
        
        Returns:
            True si la connexion est réussie
        """
        try:
            if not self.port:
                self.port = self.auto_detect_port()
                if not self.port:
                    return False
            
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            
            logger.info(f"Connecté au lecteur RFID sur {self.port}")
            return True
            
        except serial.SerialException as e:
            logger.error(f"Erreur de connexion au lecteur RFID: {e}")
            return False
    
    def disconnect(self):
        """Déconnecte du lecteur RFID"""
        self.stop_reading()
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            logger.info("Déconnecté du lecteur RFID")
    
    def read_card(self) -> Optional[str]:
        """
        Lit une carte RFID (lecture bloquante)
        
        Returns:
            Code RFID ou None
        """
        if not self.serial_connection or not self.serial_connection.is_open:
            return None
        
        try:
            if self.serial_connection.in_waiting > 0:
                data = self.serial_connection.readline()
                rfid_code = data.decode('utf-8', errors='ignore').strip()
                
                # Filtrer les lectures vides ou invalides
                if rfid_code and len(rfid_code) > 0:
                    logger.debug(f"Carte RFID lue: {rfid_code}")
                    return rfid_code
                    
        except Exception as e:
            logger.error(f"Erreur de lecture RFID: {e}")
        
        return None
    
    def _reading_loop(self):
        """Boucle de lecture continue (thread)"""
        logger.info("Démarrage de la lecture RFID continue")
        
        last_read = None
        last_read_time = 0
        debounce_time = 2.0  # Éviter les lectures multiples en 2 secondes
        
        while self.running:
            try:
                rfid_code = self.read_card()
                current_time = time.time()
                
                # Vérifier si c'est une nouvelle lecture (debouncing)
                if rfid_code and (rfid_code != last_read or current_time - last_read_time > debounce_time):
                    last_read = rfid_code
                    last_read_time = current_time
                    
                    if self.callback:
                        self.callback(rfid_code)
                
                time.sleep(0.1)  # Petit délai pour ne pas surcharger le CPU
                
            except Exception as e:
                logger.error(f"Erreur dans la boucle de lecture: {e}")
                time.sleep(1)
        
        logger.info("Arrêt de la lecture RFID continue")
    
    def start_reading(self, callback: Callable[[str], None]):
        """
        Démarre la lecture continue en arrière-plan
        
        Args:
            callback: Fonction appelée lors de la lecture d'une carte
        """
        if self.running:
            logger.warning("La lecture est déjà en cours")
            return
        
        self.callback = callback
        self.running = True
        self.read_thread = threading.Thread(target=self._reading_loop, daemon=True)
        self.read_thread.start()
        logger.info("Lecture RFID continue démarrée")
    
    def stop_reading(self):
        """Arrête la lecture continue"""
        if self.running:
            self.running = False
            if self.read_thread:
                self.read_thread.join(timeout=2)
            logger.info("Lecture RFID continue arrêtée")
    
    def is_reading(self) -> bool:
        """Vérifie si la lecture est en cours"""
        return self.running
    
    def is_connected(self) -> bool:
        """Vérifie si le lecteur est connecté"""
        return self.serial_connection is not None and self.serial_connection.is_open



