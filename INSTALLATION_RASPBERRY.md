# 🥧 Installation sur Raspberry Pi

Guide complet pour installer le système de pointage RFID sur un Raspberry Pi.

---

## 🎯 Pourquoi Raspberry Pi ?

✅ **Parfait pour cette application :**
- 💰 Économique (40-80€)
- 🔌 Faible consommation électrique
- 🏃 Toujours allumé et disponible
- 🔒 Fiable et stable
- 🔧 Ports USB pour lecteur RFID
- 📡 WiFi/Ethernet intégré
- 🖥️ Peut piloter un écran tactile

---

## 📋 Matériel Requis

### Nécessaire
- **Raspberry Pi** (modèle 3B+, 4 ou 5 recommandé)
- **Carte SD** (16 GB minimum, classe 10)
- **Alimentation** officielle (5V 3A pour RPi 4/5)
- **Lecteur RFID** USB
- **Connexion réseau** (Ethernet ou WiFi)

### Optionnel
- **Écran tactile** (7" ou 10")
- **Boîtier** pour protéger le Raspberry Pi
- **Clavier/souris** (pour la configuration initiale)

---

## 🔍 Étape 1 : Trouver votre Raspberry Pi sur le Réseau

### Méthode A : Script Automatique (macOS/Linux)

```bash
chmod +x trouver_raspberry.sh
./trouver_raspberry.sh
```

### Méthode B : Via votre Box Internet

1. Connectez-vous à l'interface de votre box (ex: http://192.168.1.1)
2. Consultez la liste des appareils connectés
3. Cherchez "raspberrypi" dans le nom d'hôte
4. Notez l'adresse IP (ex: 192.168.1.45)

### Méthode C : Sur Windows avec Angry IP Scanner

1. Téléchargez [Angry IP Scanner](https://angryip.org/)
2. Installez et lancez
3. Scannez votre réseau (ex: 192.168.1.1 à 192.168.1.254)
4. Cherchez un appareil avec hostname "raspberrypi"

### Méthode D : Directement sur le Raspberry Pi

Si vous avez accès physique au Raspberry Pi :

1. Connectez un écran et un clavier
2. Ouvrez un terminal
3. Tapez :
   ```bash
   hostname -I
   ```
4. Notez l'adresse IP affichée

---

## 🔐 Étape 2 : Activer SSH (si nécessaire)

### Si SSH n'est pas activé

**Option 1 : Via l'interface graphique (si écran connecté)**
1. Menu → Preferences → Raspberry Pi Configuration
2. Onglet "Interfaces"
3. SSH : **Enable**
4. OK

**Option 2 : En créant un fichier sur la carte SD**
1. Retirez la carte SD du Raspberry Pi
2. Insérez-la dans votre ordinateur
3. Créez un fichier vide nommé `ssh` (sans extension) dans la partition "boot"
4. Réinsérez la carte SD dans le Raspberry Pi
5. Redémarrez

---

## 💻 Étape 3 : Se Connecter au Raspberry Pi

### Depuis votre ordinateur (macOS/Linux)

```bash
ssh pi@192.168.1.45
```
(Remplacez 192.168.1.45 par l'IP de votre Raspberry Pi)

**Mot de passe par défaut :** `raspberry`

### Depuis Windows

**Option 1 : PowerShell/CMD**
```bash
ssh pi@192.168.1.45
```

**Option 2 : PuTTY**
1. Téléchargez [PuTTY](https://www.putty.org/)
2. Lancez PuTTY
3. Host Name : IP de votre Raspberry Pi
4. Port : 22
5. Connection type : SSH
6. Click "Open"

---

## 🔧 Étape 4 : Préparer le Système

Une fois connecté en SSH :

### 4.1 Mettre à jour le système

```bash
sudo apt update
sudo apt upgrade -y
```
⏱️ Cela peut prendre 10-15 minutes

### 4.2 Installer Python et les outils

```bash
# Python est déjà installé, mais installer pip et venv
sudo apt install -y python3-pip python3-venv python3-dev

# Installer les dépendances système pour PyQt5
sudo apt install -y python3-pyqt5 python3-pyqt5.qtserialport

# Installer les outils système
sudo apt install -y git
```

### 4.3 Configurer le mot de passe (recommandé)

```bash
passwd
```
Suivez les instructions pour changer le mot de passe par défaut.

---

## 📦 Étape 5 : Installer l'Application

### 5.1 Télécharger le projet

**Option A : Via Git (si le projet est sur GitHub)**
```bash
cd ~
git clone [URL_DU_REPO] timbrage
cd timbrage
```

**Option B : Transférer depuis votre ordinateur**
```bash
# Sur votre ordinateur (macOS/Linux)
scp -r /chemin/vers/timbrage pi@192.168.1.45:~/

# Puis sur le Raspberry Pi
cd ~/timbrage
```

**Option C : Via SCP depuis Windows**
Utilisez [WinSCP](https://winscp.net/) pour transférer le dossier

### 5.2 Installer les dépendances

```bash
cd ~/timbrage

# Installer les dépendances Python
pip3 install -r requirements.txt
```

Si vous obtenez une erreur avec PyQt5, utilisez la version système :
```bash
# Retirer PyQt5 du requirements.txt temporairement
grep -v "PyQt5" requirements.txt > requirements_rpi.txt
pip3 install -r requirements_rpi.txt

# PyQt5 est déjà installé via apt
```

---

## ⚙️ Étape 6 : Configuration

### 6.1 Configuration initiale

```bash
python3 setup_env.py
```

Suivez les instructions pour configurer :
- Paramètres FTP
- Nom de l'entreprise
- Etc.

### 6.2 Configurer les employés

```bash
nano config/employees.json
```

Ajoutez vos employés :
```json
{
  "employees": [
    {
      "rfid": "1234567890",
      "name": "Jean Dupont",
      "employee_id": "EMP001"
    }
  ]
}
```

Sauvegardez : Ctrl+O, Enter, Ctrl+X

### 6.3 Vérifier le lecteur RFID

```bash
# Lister les ports série
ls -la /dev/tty*

# Ou avec plus de détails
dmesg | grep tty
```

Notez le port du lecteur RFID (ex: `/dev/ttyUSB0` ou `/dev/ttyACM0`)

Si nécessaire, configurez-le dans `.env` :
```bash
nano .env
```

Ajoutez ou modifiez :
```
RFID_PORT=/dev/ttyUSB0
```

### 6.4 Donner les droits d'accès au port série

```bash
# Ajouter l'utilisateur au groupe dialout
sudo usermod -a -G dialout pi

# Se déconnecter et reconnecter pour appliquer
exit
# Puis reconnectez-vous en SSH
```

---

## 🧪 Étape 7 : Tests

### 7.1 Vérifier l'installation

```bash
cd ~/timbrage
python3 diagnostic.py
```

### 7.2 Test sans écran (serveur X11 virtuel)

```bash
# Installer Xvfb (X virtual framebuffer)
sudo apt install -y xvfb

# Tester l'application
xvfb-run python3 test_rfid_simulator.py
```

### 7.3 Test avec écran

Si un écran est connecté au Raspberry Pi :

```bash
# Dans l'environnement graphique (pas en SSH)
cd ~/timbrage
python3 main.py
```

---

## 🚀 Étape 8 : Lancement Automatique au Démarrage

### 8.1 Créer un service systemd

```bash
sudo nano /etc/systemd/system/pointage.service
```

Ajoutez :
```ini
[Unit]
Description=Système de Pointage RFID
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/timbrage
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/pi/.Xauthority"
ExecStart=/usr/bin/python3 /home/pi/timbrage/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=graphical.target
```

Sauvegardez : Ctrl+O, Enter, Ctrl+X

### 8.2 Activer le service

```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer le service au démarrage
sudo systemctl enable pointage.service

# Démarrer le service
sudo systemctl start pointage.service

# Vérifier le statut
sudo systemctl status pointage.service
```

### 8.3 Commandes utiles

```bash
# Arrêter le service
sudo systemctl stop pointage.service

# Redémarrer le service
sudo systemctl restart pointage.service

# Voir les logs
sudo journalctl -u pointage.service -f

# Désactiver le démarrage automatique
sudo systemctl disable pointage.service
```

---

## 🖥️ Étape 9 : Configuration de l'Écran Tactile (optionnel)

### Si vous utilisez un écran tactile officiel Raspberry Pi :

#### 9.1 Rotation de l'écran

Éditez le fichier de config :
```bash
sudo nano /boot/config.txt
```

Ajoutez (pour rotation de 180°) :
```
lcd_rotate=2
```

Ou pour orientation portrait :
```
display_rotate=1
```

#### 9.2 Calibrage tactile

```bash
sudo apt install -y xinput-calibrator
DISPLAY=:0 xinput_calibrator
```

#### 9.3 Désactiver l'économiseur d'écran

```bash
sudo nano /etc/lightdm/lightdm.conf
```

Dans la section `[Seat:*]`, ajoutez :
```
xserver-command=X -s 0 -dpms
```

#### 9.4 Masquer le curseur

```bash
sudo apt install -y unclutter
```

Ajoutez au démarrage :
```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/unclutter.desktop
```

Contenu :
```
[Desktop Entry]
Type=Application
Name=Unclutter
Exec=unclutter -idle 0.1
```

---

## 🌐 Étape 10 : Accès à Distance

### 10.1 SSH (déjà configuré)

```bash
ssh pi@192.168.1.45
```

### 10.2 VNC (Bureau à distance)

```bash
# Activer VNC
sudo raspi-config
# Interface Options → VNC → Yes
```

Puis depuis votre ordinateur :
- Téléchargez [RealVNC Viewer](https://www.realvnc.com/download/viewer/)
- Connectez-vous à l'IP du Raspberry Pi

### 10.3 Accès Web aux Logs (optionnel)

Créez un serveur web simple pour consulter les logs :

```bash
# Créer un script
nano ~/web_logs.py
```

Contenu :
```python
#!/usr/bin/env python3
import http.server
import socketserver

PORT = 8080

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/home/pi/timbrage/logs", **kwargs)

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serveur web sur http://localhost:{PORT}")
    httpd.serve_forever()
```

Lancer :
```bash
python3 ~/web_logs.py &
```

Accéder depuis votre navigateur : `http://192.168.1.45:8080`

---

## 🔐 Sécurité et Maintenance

### Sauvegardes Automatiques

Créez un script de sauvegarde :

```bash
nano ~/backup_pointage.sh
```

Contenu :
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/pi/backups"
mkdir -p $BACKUP_DIR

# Sauvegarder la base de données
cp /home/pi/timbrage/data/pointage.db $BACKUP_DIR/pointage_$DATE.db

# Conserver seulement les 30 dernières sauvegardes
ls -t $BACKUP_DIR/pointage_*.db | tail -n +31 | xargs -r rm

echo "Sauvegarde créée : pointage_$DATE.db"
```

Rendre exécutable :
```bash
chmod +x ~/backup_pointage.sh
```

Programmer avec cron (tous les jours à 23h) :
```bash
crontab -e
```

Ajouter :
```
0 23 * * * /home/pi/backup_pointage.sh >> /home/pi/backup.log 2>&1
```

### Mises à Jour

```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Mettre à jour l'application
cd ~/timbrage
git pull  # Si utilisation de Git
pip3 install --upgrade -r requirements.txt
```

---

## 🐛 Dépannage Raspberry Pi

### Le lecteur RFID n'est pas détecté

```bash
# Vérifier les périphériques USB
lsusb

# Vérifier les ports série
ls -la /dev/tty* | grep USB

# Tester les permissions
groups  # Doit inclure 'dialout'

# Si pas dans le groupe :
sudo usermod -a -G dialout $USER
# Puis déconnexion/reconnexion
```

### L'interface graphique ne démarre pas

```bash
# Vérifier si X11 est en cours
echo $DISPLAY  # Devrait afficher :0

# Redémarrer le service graphique
sudo systemctl restart lightdm

# Ou redémarrer le Raspberry Pi
sudo reboot
```

### Problèmes de performance

```bash
# Vérifier la température
vcgencmd measure_temp

# Vérifier l'utilisation CPU
top

# Libérer de la mémoire
sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'
```

### Les logs ne s'écrivent pas

```bash
# Vérifier les permissions
ls -la ~/timbrage/logs/

# Créer le dossier si nécessaire
mkdir -p ~/timbrage/logs
chmod 777 ~/timbrage/logs
```

---

## 📊 Monitoring

### Vérifier l'état du service

```bash
# Statut
systemctl status pointage.service

# Logs en temps réel
journalctl -u pointage.service -f

# Logs de l'application
tail -f ~/timbrage/logs/pointage.log
```

### Statistiques système

```bash
# CPU et mémoire
htop

# Espace disque
df -h

# Température
watch -n 2 vcgencmd measure_temp
```

---

## 🎯 Configuration Réseau Avancée

### IP Statique (recommandé pour un système de production)

```bash
sudo nano /etc/dhcpcd.conf
```

Ajoutez à la fin :
```
interface eth0  # ou wlan0 pour WiFi
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

Redémarrer :
```bash
sudo reboot
```

---

## ✅ Checklist Finale

- [ ] Raspberry Pi trouvé sur le réseau
- [ ] SSH activé et fonctionnel
- [ ] Système à jour
- [ ] Python et dépendances installées
- [ ] Application installée et configurée
- [ ] Lecteur RFID détecté et configuré
- [ ] Fichier `.env` configuré
- [ ] Employés ajoutés
- [ ] Tests réussis
- [ ] Service systemd configuré
- [ ] Démarrage automatique activé
- [ ] Écran tactile configuré (si applicable)
- [ ] Sauvegardes automatiques configurées
- [ ] IP statique configurée (optionnel mais recommandé)

---

## 📚 Ressources

- [Documentation officielle Raspberry Pi](https://www.raspberrypi.org/documentation/)
- [Forum Raspberry Pi](https://www.raspberrypi.org/forums/)
- [Guide PyQt5 sur Raspberry Pi](https://www.riverbankcomputing.com/static/Docs/PyQt5/)

---

**Votre système de pointage est maintenant opérationnel sur Raspberry Pi ! 🥧⚡**



