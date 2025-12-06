# 🚀 Raspberry Pi - Démarrage Rapide

Guide ultra-rapide pour installer le système de pointage sur Raspberry Pi.

---

## 📋 Ce dont vous avez besoin

- ✅ Un Raspberry Pi connecté à votre réseau
- ✅ Accès SSH activé sur le Raspberry Pi
- ✅ 10-15 minutes

---

## 🎯 Installation en 4 Étapes

### Étape 1 : Trouver votre Raspberry Pi

**Sur macOS/Linux :**
```bash
cd /chemin/vers/timbrage
chmod +x trouver_raspberry.sh
./trouver_raspberry.sh
```

**Sur Windows ou via votre box Internet :**
- Connectez-vous à votre box (ex: http://192.168.1.1)
- Liste des appareils → cherchez "raspberrypi"
- Notez l'adresse IP (ex: 192.168.1.45)

---

### Étape 2 : Se connecter au Raspberry Pi

```bash
ssh pi@192.168.1.45
```
(Remplacez par l'IP de votre Raspberry Pi)

**Mot de passe par défaut :** `raspberry`

---

### Étape 3 : Transférer et installer

**Option A : Depuis votre Mac/Linux**

```bash
# Sur votre ordinateur (ouvrez un nouveau terminal)
cd /chemin/vers/timbrage
scp -r . pi@192.168.1.45:~/timbrage

# Puis sur le Raspberry Pi (dans le terminal SSH)
cd ~/timbrage
chmod +x install_raspberry.sh
./install_raspberry.sh
```

**Option B : Depuis Windows**

1. Utilisez [WinSCP](https://winscp.net/) pour transférer le dossier `timbrage`
2. Puis dans PuTTY/SSH :
   ```bash
   cd ~/timbrage
   chmod +x install_raspberry.sh
   ./install_raspberry.sh
   ```

---

### Étape 4 : Configuration

```bash
# Configuration initiale
python3 setup_env.py

# Configurer les employés
nano config/employees.json

# Tester
python3 diagnostic.py
```

---

## ✅ C'est Prêt !

### Lancer l'application

```bash
cd ~/timbrage
python3 main.py
```

### Démarrage automatique au boot

```bash
# Créer le service
sudo nano /etc/systemd/system/pointage.service
```

Copiez le contenu depuis [INSTALLATION_RASPBERRY.md](INSTALLATION_RASPBERRY.md#81-créer-un-service-systemd)

Puis :
```bash
sudo systemctl enable pointage.service
sudo systemctl start pointage.service
```

---

## 🆘 Problèmes ?

### Le Raspberry Pi ne répond pas en SSH
- Vérifiez qu'il est allumé (LED rouge = alimentation, LED verte = activité)
- Vérifiez le câble réseau ou le WiFi
- Essayez : `ping 192.168.1.45` (remplacez par votre IP)

### Permission denied sur le port série
```bash
sudo usermod -a -G dialout pi
# Puis déconnectez et reconnectez-vous
exit
ssh pi@192.168.1.45
```

### L'interface ne démarre pas
```bash
# Tester avec le simulateur
python3 test_rfid_simulator.py

# Ou utiliser X virtual framebuffer
xvfb-run python3 main.py
```

---

## 📖 Documentation Complète

Pour plus de détails, consultez :
- **[INSTALLATION_RASPBERRY.md](INSTALLATION_RASPBERRY.md)** - Guide complet
- **[MANUEL_UTILISATION.md](MANUEL_UTILISATION.md)** - Manuel utilisateur

---

## 💡 Conseils

### Optimisation

```bash
# Désactiver le Bluetooth (si non utilisé)
echo "dtoverlay=disable-bt" | sudo tee -a /boot/config.txt

# Réduire la consommation
sudo raspi-config
# Performance Options → GPU Memory → 16
```

### Monitoring

```bash
# Voir les logs
sudo journalctl -u pointage.service -f

# Température
vcgencmd measure_temp

# Performances
htop
```

### Sauvegarde

```bash
# Sauvegarder la carte SD complète (depuis votre ordinateur)
sudo dd if=/dev/sdX of=~/raspberry_backup.img bs=4M status=progress

# Ou juste la base de données
scp pi@192.168.1.45:~/timbrage/data/pointage.db ~/backup/
```

---

**Votre Raspberry Pi est maintenant un terminal de pointage ! 🥧✨**


