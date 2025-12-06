"""
Module d'upload FTP
"""
from ftplib import FTP, FTP_TLS
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FTPUploader:
    """Gère l'envoi de fichiers par FTP"""
    
    def __init__(self, host: str, port: int, user: str, password: str, remote_path: str = "/", use_tls: bool = False):
        """
        Initialise l'uploader FTP
        
        Args:
            host: Hôte FTP
            port: Port FTP
            user: Nom d'utilisateur
            password: Mot de passe
            remote_path: Chemin distant
            use_tls: Utiliser FTP avec TLS
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.remote_path = remote_path
        self.use_tls = use_tls
        self.ftp = None
    
    def connect(self) -> bool:
        """
        Connecte au serveur FTP
        
        Returns:
            True si la connexion est réussie
        """
        try:
            if self.use_tls:
                self.ftp = FTP_TLS()
            else:
                self.ftp = FTP()
            
            # Connexion
            self.ftp.connect(self.host, self.port)
            self.ftp.login(self.user, self.password)
            
            if self.use_tls:
                self.ftp.prot_p()  # Passer en mode sécurisé
            
            # Changer vers le répertoire distant
            try:
                self.ftp.cwd(self.remote_path)
            except:
                # Créer le répertoire s'il n'existe pas
                self._create_remote_directory(self.remote_path)
                self.ftp.cwd(self.remote_path)
            
            logger.info(f"Connecté au serveur FTP: {self.host}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur de connexion FTP: {e}")
            return False
    
    def disconnect(self):
        """Déconnecte du serveur FTP"""
        if self.ftp:
            try:
                self.ftp.quit()
            except:
                self.ftp.close()
            logger.info("Déconnecté du serveur FTP")
    
    def _create_remote_directory(self, path: str):
        """Crée un répertoire distant récursivement"""
        parts = path.strip('/').split('/')
        current = ''
        
        for part in parts:
            current += '/' + part
            try:
                self.ftp.mkd(current)
                logger.debug(f"Répertoire créé: {current}")
            except:
                # Le répertoire existe déjà
                pass
    
    def upload_file(self, local_file: str, remote_filename: str = None) -> bool:
        """
        Upload un fichier sur le serveur FTP
        
        Args:
            local_file: Chemin du fichier local
            remote_filename: Nom du fichier distant (nom local si None)
        
        Returns:
            True si l'upload est réussi
        """
        local_path = Path(local_file)
        
        if not local_path.exists():
            logger.error(f"Fichier local introuvable: {local_file}")
            return False
        
        if not remote_filename:
            remote_filename = local_path.name
        
        try:
            if not self.ftp:
                if not self.connect():
                    return False
            
            with open(local_path, 'rb') as file:
                self.ftp.storbinary(f'STOR {remote_filename}', file)
            
            logger.info(f"Fichier uploadé: {remote_filename}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'upload FTP: {e}")
            return False
    
    def upload_files(self, local_files: list) -> dict:
        """
        Upload plusieurs fichiers
        
        Args:
            local_files: Liste de chemins de fichiers locaux
        
        Returns:
            Dictionnaire avec les résultats {filename: success}
        """
        results = {}
        
        try:
            if not self.connect():
                return {f: False for f in local_files}
            
            for local_file in local_files:
                results[local_file] = self.upload_file(local_file)
            
            self.disconnect()
            
        except Exception as e:
            logger.error(f"Erreur lors de l'upload multiple: {e}")
            results = {f: False for f in local_files}
        
        return results
    
    def test_connection(self) -> bool:
        """
        Teste la connexion FTP
        
        Returns:
            True si la connexion fonctionne
        """
        result = self.connect()
        if result:
            self.disconnect()
        return result



