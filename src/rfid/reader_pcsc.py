"""
Gestionnaire de lecteur RFID PC/SC (pour ACR1252 et lecteurs smart card)
"""
import threading
import time
import logging
from typing import Callable, Optional

try:
    from smartcard.System import readers
    from smartcard.util import toHexString
    from smartcard.Exceptions import NoCardException, CardConnectionException
    PYSCARD_AVAILABLE = True
except ImportError:
    PYSCARD_AVAILABLE = False

logger = logging.getLogger(__name__)


class RFIDReaderPCSC:
    """Gère la lecture des cartes RFID via PC/SC (smart card)"""
    
    def __init__(self, reader_index: int = 0):
        """
        Initialise le lecteur PC/SC
        
        Args:
            reader_index: Index du lecteur à utiliser (0 = premier lecteur)
        """
        if not PYSCARD_AVAILABLE:
            raise ImportError(
                "pyscard n'est pas installé. Installez-le avec: "
                "sudo apt install python3-pyscard"
            )
        
        self.reader_index = reader_index
        self.reader = None
        self.connection = None
        self.running = False
        self.read_thread: Optional[threading.Thread] = None
        self.callback: Optional[Callable] = None
        self.last_uid = None
        self.last_read_time = 0
        
    def list_available_readers(self):
        """Liste les lecteurs PC/SC disponibles"""
        try:
            r = readers()
            available_readers = []
            for i, reader in enumerate(r):
                available_readers.append({
                    'index': i,
                    'name': str(reader),
                    'description': str(reader)
                })
            return available_readers
        except Exception as e:
            logger.error(f"Erreur lors de la liste des lecteurs: {e}")
            return []
    
    def connect(self) -> bool:
        """
        Connecte au lecteur PC/SC
        
        Returns:
            True si la connexion est réussie
        """
        try:
            r = readers()
            
            if not r:
                logger.error("Aucun lecteur PC/SC trouvé")
                return False
            
            if self.reader_index >= len(r):
                logger.error(f"Lecteur index {self.reader_index} non trouvé. Lecteurs disponibles: {len(r)}")
                return False
            
            self.reader = r[self.reader_index]
            logger.info(f"Connecté au lecteur PC/SC: {self.reader}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur de connexion au lecteur PC/SC: {e}")
            return False
    
    def disconnect(self):
        """Déconnecte du lecteur PC/SC"""
        self.stop_reading()
        if self.connection:
            try:
                self.connection.disconnect()
            except:
                pass
        logger.info("Déconnecté du lecteur PC/SC")
    
    def read_card_uid(self) -> Optional[str]:
        """
        Lit l'UID d'une carte RFID
        
        Returns:
            UID de la carte ou None
        """
        if not self.reader:
            return None
        
        try:
            # Créer une connexion à la carte
            connection = self.reader.createConnection()
            connection.connect()
            
            # Commande APDU pour lire l'UID (Get Data)
            # Cette commande fonctionne pour la plupart des cartes RFID/NFC
            GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            
            data, sw1, sw2 = connection.transmit(GET_UID)
            
            # Vérifier le statut (90 00 = succès)
            if sw1 == 0x90 and sw2 == 0x00:
                # Convertir en chaîne hexadécimale
                uid = toHexString(data).replace(' ', '')
                logger.debug(f"UID lu: {uid}")
                connection.disconnect()
                return uid
            else:
                logger.warning(f"Erreur lecture UID: SW={sw1:02X} {sw2:02X}")
                connection.disconnect()
                return None
                
        except NoCardException:
            # Pas de carte présente (normal)
            return None
        except CardConnectionException as e:
            logger.debug(f"Erreur connexion carte: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur lecture UID: {e}")
            return None
    
    def _reading_loop(self):
        """Boucle de lecture continue (thread)"""
        logger.info("Démarrage de la lecture PC/SC continue")
        
        debounce_time = 2.0  # Éviter les lectures multiples en 2 secondes
        
        while self.running:
            try:
                uid = self.read_card_uid()
                current_time = time.time()
                
                # Vérifier si c'est une nouvelle lecture (debouncing)
                if uid and (uid != self.last_uid or current_time - self.last_read_time > debounce_time):
                    self.last_uid = uid
                    self.last_read_time = current_time
                    
                    if self.callback:
                        self.callback(uid)
                
                time.sleep(0.3)  # Vérifier toutes les 300ms
                
            except Exception as e:
                logger.error(f"Erreur dans la boucle de lecture: {e}")
                time.sleep(1)
        
        logger.info("Arrêt de la lecture PC/SC continue")
    
    def start_reading(self, callback: Callable[[str], None]):
        """
        Démarre la lecture continue en arrière-plan
        
        Args:
            callback: Fonction appelée lors de la lecture d'une carte
        """
        if self.running:
            logger.warning("La lecture est déjà en cours")
            return
        
        if not self.reader:
            logger.error("Lecteur non connecté. Appelez connect() d'abord.")
            return
        
        self.callback = callback
        self.running = True
        self.read_thread = threading.Thread(target=self._reading_loop, daemon=True)
        self.read_thread.start()
        logger.info("Lecture PC/SC continue démarrée")
    
    def stop_reading(self):
        """Arrête la lecture continue"""
        if self.running:
            self.running = False
            if self.read_thread:
                self.read_thread.join(timeout=2)
            logger.info("Lecture PC/SC continue arrêtée")
    
    def is_reading(self) -> bool:
        """Vérifie si la lecture est en cours"""
        return self.running
    
    def is_connected(self) -> bool:
        """Vérifie si le lecteur est connecté"""
        return self.reader is not None


# Fonction utilitaire pour détecter le type de lecteur
def detect_reader_type():
    """Détecte quel type de lecteur utiliser (Serial ou PC/SC)"""
    # Vérifier si pyscard est disponible et s'il y a des lecteurs
    if PYSCARD_AVAILABLE:
        try:
            r = readers()
            if r:
                return 'pcsc'
        except:
            pass
    
    # Vérifier s'il y a des ports série
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        if ports:
            return 'serial'
    except:
        pass
    
    return None



