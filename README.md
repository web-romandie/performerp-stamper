# 🕐 Système de Pointage RFID

Logiciel de gestion de pointage des employés avec lecteur RFID, compatible **Windows** et **macOS**.

Conçu pour fonctionner sur terminal tactile **QCT Windows 10 4/64GB avec lecteur RFID intégré**.

---

## 🚀 Démarrage Rapide

### Installation en 3 étapes

1. **Installez Python 3.8+** depuis [python.org](https://www.python.org/downloads/)
2. **Installez les dépendances** : `pip install -r requirements.txt`
3. **Configurez l'application** : `python setup_env.py`

### Lancement

**Windows :** Double-cliquez sur `start.bat`  
**macOS/Linux :** Lancez `./start.sh`  
**Ou directement :** `python main.py`

### Test sans lecteur RFID

```bash
python test_rfid_simulator.py
```

📖 **Guide complet :** Consultez [QUICK_START.md](QUICK_START.md)

---

## ✨ Fonctionnalités

### Interface de Pointage

- ✅ **Pointage automatique** entrée/sortie par puce RFID
- ✅ **Interface tactile** optimisée pour écran 10 pouces
- ✅ **Feedback visuel** immédiat (vert/rouge)
- ✅ **Horloge en temps réel**
- ✅ **Historique** des derniers pointages

### Gestion des Données

- ✅ **Base de données locale** SQLite
- ✅ **Enregistrement automatique** de tous les pointages
- ✅ **Calcul des heures** travaillées par employé
- ✅ **Journalisation complète** (logs)

### Export et Synchronisation

- ✅ **Export automatique** en fichier CSV
- ✅ **Envoi par FTP** vers serveur distant
- ✅ **Planification** configurable (toutes les heures par défaut)
- ✅ **Export manuel** depuis l'administration

### Administration

- ✅ **Panneau d'administration** intégré
- ✅ **Consultation des pointages** par période
- ✅ **Rapports** journaliers et hebdomadaires
- ✅ **Test de connexion FTP**
- ✅ **Gestion des exports**

---

## 📋 Prérequis

### Matériel

- **Ordinateur** : Windows 10/11 ou macOS 10.14+
- **RAM** : 4 GB minimum
- **Lecteur RFID** : USB/Serial (auto-détection)
- **Écran tactile** : Recommandé (1024x600 minimum)
- **Connexion Internet** : Pour l'envoi FTP

### Logiciels

- **Python** 3.8 ou supérieur
- **Bibliothèques** : PyQt5, pyserial, python-dotenv (voir requirements.txt)

### Terminaux Compatibles

**Terminal tactile professionnel :**  
**[QCT Windows 10 4/64GB avec lecteur RFID](https://visualdata.primelco.ch/fr-product-10_1_-qct-win10-4_64gb-qct-rfid-black~pri-ctr_10qctbuwr0)**

**Alternative économique :**  
**Raspberry Pi** (3B+, 4 ou 5) + Écran tactile + Lecteur RFID USB  
→ Consultez [INSTALLATION_RASPBERRY.md](INSTALLATION_RASPBERRY.md)

---

## 📦 Installation

### Installation Automatique (Recommandée)

#### Windows

1. Téléchargez et décompressez le projet
2. Double-cliquez sur `start.bat`
3. Le script installera automatiquement les dépendances

#### macOS/Linux

```bash
chmod +x start.sh
./start.sh
```

### Installation Manuelle

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Configuration initiale
python setup_env.py

# 3. Vérifier l'installation
python diagnostic.py

# 4. Lancer l'application
python main.py
```

---

## ⚙️ Configuration

### Configuration Automatique

```bash
python setup_env.py
```

Le script vous guidera pour configurer :

- Paramètres FTP (hôte, utilisateur, mot de passe)
- Nom de l'entreprise
- Intervalle d'export automatique
- Port RFID (optionnel)

### Configuration Manuelle

Créez un fichier `.env` à la racine :

```env
# Configuration FTP
FTP_HOST=ftp.example.com
FTP_PORT=21
FTP_USER=username
FTP_PASSWORD=password
FTP_REMOTE_PATH=/pointage

# Configuration générale
COMPANY_NAME=Votre Entreprise
AUTO_EXPORT_INTERVAL=3600
DEBUG_MODE=False

# Configuration RFID (laissez vide pour auto-détection)
RFID_PORT=
RFID_BAUDRATE=9600

# Interface
FULLSCREEN=False
```

### Configuration des Employés

Éditez `config/employees.json` :

```json
{
  "employees": [
    {
      "rfid": "1234567890",
      "name": "Jean Dupont",
      "employee_id": "EMP001"
    },
    {
      "rfid": "0987654321",
      "name": "Marie Martin",
      "employee_id": "EMP002"
    }
  ]
}
```

**💡 Pour obtenir le code RFID d'un badge :**

1. Activez le mode DEBUG : `DEBUG_MODE=True` dans `.env`
2. Lancez l'application et scannez le badge
3. Consultez `logs/pointage.log` pour voir le code

---

## 🎯 Utilisation

### Interface Principale

1. **Lancement** : L'application démarre en mode pointage
2. **Pointage** : L'employé présente son badge RFID devant le lecteur
3. **Confirmation** : Un message affiche le nom et le type (ENTRÉE/SORTIE)
4. **Automatique** : Le système alterne automatiquement entre ENTRÉE et SORTIE

### Panneau d'Administration

Accès : Cliquez sur le bouton **"Administration"**

#### Onglet Pointages

- Consultez tous les pointages par période
- Filtrez par date
- Vérifiez le statut d'export

#### Onglet Rapports

- **Rapport journalier** : Détail de la journée
- **Rapport hebdomadaire** : Heures par employé

#### Onglet Export

- Exportez manuellement en CSV
- Envoyez par FTP
- Testez la connexion FTP

---

## 📊 Format d'Export CSV

Les fichiers CSV sont générés avec ce format :

```csv
ID;Matricule;Nom;RFID;Date;Heure;Type
1;EMP001;Jean Dupont;1234567890;26/11/2025;08:30:00;ENTREE
2;EMP001;Jean Dupont;1234567890;26/11/2025;17:00:00;SORTIE
```

- **Séparateur** : `;` (point-virgule)
- **Encodage** : UTF-8 avec BOM (compatible Excel)
- **Format de date** : JJ/MM/AAAA
- **Format d'heure** : HH:MM:SS

---

## 🗂️ Structure du Projet

```
timbrage/
├── main.py                    # Point d'entrée principal
├── setup_env.py              # Configuration initiale
├── diagnostic.py             # Vérification du système
├── test_rfid_simulator.py    # Test sans lecteur RFID
├── start.bat                 # Démarrage Windows
├── start.sh                  # Démarrage macOS/Linux
├── build_windows.py          # Compilation en .exe
├── requirements.txt          # Dépendances Python
├── .env                      # Configuration (à créer)
│
├── config/
│   ├── employees.json        # Liste des employés
│   └── settings.py           # Configuration de l'app
│
├── src/
│   ├── gui/
│   │   ├── main_window.py    # Interface principale
│   │   └── admin_panel.py    # Panneau d'administration
│   ├── rfid/
│   │   └── reader.py         # Gestion du lecteur RFID
│   ├── database/
│   │   └── db_manager.py     # Gestion de la base de données
│   └── export/
│       ├── csv_exporter.py   # Export CSV
│       └── ftp_uploader.py   # Upload FTP
│
├── data/
│   └── pointage.db           # Base de données SQLite
├── logs/
│   └── pointage.log          # Logs de l'application
└── exports/                  # Fichiers CSV exportés
```

---

## 🛠️ Outils et Scripts

| Script                   | Description                          |
| ------------------------ | ------------------------------------ |
| `main.py`                | Lance l'application principale       |
| `setup_env.py`           | Assistant de configuration initiale  |
| `diagnostic.py`          | Vérifie que tout est bien installé   |
| `test_rfid_simulator.py` | Teste l'app sans lecteur RFID        |
| `build_windows.py`       | Compile en exécutable Windows (.exe) |
| `start.bat`              | Démarrage automatique (Windows)      |
| `start.sh`               | Démarrage automatique (macOS/Linux)  |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [INSTALLATION_RASPBERRY.md](INSTALLATION_RASPBERRY.md) | Guide complet pour Raspberry Pi |
| [INSTALLATION_WINDOWS.md](INSTALLATION_WINDOWS.md) | Guide d'installation Windows |
| [CONNEXION_RASPBERRY.md](CONNEXION_RASPBERRY.md) | Connexion SSH au Raspberry Pi |
| [CHANGELOG.md](CHANGELOG.md) | Historique des versions |

---

## 🔧 Dépannage

### Le lecteur RFID n'est pas détecté

**Solutions :**

1. Vérifiez qu'il est bien branché en USB
2. Consultez `logs/pointage.log` pour voir les ports détectés
3. Configurez manuellement le port dans `.env` :
   ```env
   RFID_PORT=COM3  # Windows
   RFID_PORT=/dev/ttyUSB0  # Linux
   RFID_PORT=/dev/cu.usbserial  # macOS
   ```

### Un badge n'est pas reconnu

1. Vérifiez qu'il est dans `config/employees.json`
2. Activez le DEBUG : `DEBUG_MODE=True` dans `.env`
3. Scannez le badge et consultez les logs

### L'export FTP échoue

1. Testez depuis le panneau d'administration
2. Vérifiez vos paramètres dans `.env`
3. Testez avec FileZilla pour valider les accès

### Plus d'aide

```bash
# Vérifier l'installation
python diagnostic.py

# Activer le mode DEBUG
# Éditez .env et changez: DEBUG_MODE=True

# Consulter les logs
cat logs/pointage.log  # macOS/Linux
type logs\pointage.log  # Windows
```

---

## 🔄 Configurer une nouvelle entreprise

Pour réutiliser un Raspberry Pi (ou une copie de carte SD) pour une autre entreprise :

### 1. Arrêter la timbreuse

```bash
sudo systemctl stop timbrage
```

### 2. Supprimer les pointages existants

```bash
rm ~/timbrage/data/pointage.db
```

La base sera recréée automatiquement (vide) au prochain démarrage.

### 3. Vider les employés

```bash
echo '[]' > ~/timbrage/config/employees.json
```

### 4. Modifier la configuration API

```bash
nano ~/timbrage/config/api_config.py
```

Changez les valeurs pour la nouvelle entreprise :

```python
API_URL = "https://votre-serveur.ch/presence"
ACCOUNT_ID = 123      # ID du nouveau compte
API_KEY = "votre-clé-api"
```

### 5. Redémarrer la timbreuse

```bash
sudo systemctl start timbrage
```

### 6. Recharger les employés

Ouvrez l'admin → onglet **Configuration RFID** → bouton **"Regénérer employees.json"**

### Résumé rapide

| Étape | Commande |
|-------|----------|
| Arrêter | `sudo systemctl stop timbrage` |
| Vider les pointages | `rm ~/timbrage/data/pointage.db` |
| Vider les employés | `echo '[]' > ~/timbrage/config/employees.json` |
| Nouvelle config API | `nano ~/timbrage/config/api_config.py` |
| Redémarrer | `sudo systemctl start timbrage` |

---

## 💾 Sauvegarder / Cloner la carte SD

### Créer une copie (sur Mac)

```bash
# Identifier la carte SD
diskutil list

# Démonter la carte (remplacez disk6 par votre numéro)
diskutil unmountDisk /dev/disk6

# Copier la carte entière
sudo dd if=/dev/rdisk6 of=/Users/VOTRE_NOM/Desktop/raspberry_backup.img bs=4m status=progress

# Éjecter
diskutil eject /dev/disk6
```

### Restaurer sur une nouvelle carte

```bash
# Identifier la nouvelle carte
diskutil list

# Démonter
diskutil unmountDisk /dev/disk6

# Écrire l'image
sudo dd if=/Users/VOTRE_NOM/Desktop/raspberry_backup.img of=/dev/rdisk6 bs=4m status=progress

# Éjecter
diskutil eject /dev/disk6
```

### Compresser l'image (optionnel)

```bash
# Compresser (63 Go → ~5-15 Go)
gzip /Users/VOTRE_NOM/Desktop/raspberry_backup.img

# Restaurer depuis une image compressée
diskutil unmountDisk /dev/disk6
gunzip -c /Users/VOTRE_NOM/Desktop/raspberry_backup.img.gz | sudo dd of=/dev/rdisk6 bs=4m status=progress
```

> **Attention** : Vérifiez bien le numéro du disque (`diskutil list`) avant d'écrire. `dd` écrase tout sans confirmation !

---

## 🔧 Outils utilitaires

| Script | Description |
|--------|-------------|
| `mark_all_synced.py` | Marque tous les pointages comme déjà synchronisés |

```bash
# Utile après une migration pour éviter de renvoyer les anciens pointages
python3 mark_all_synced.py
```

---

## 🔐 Sécurité

- ⚠️ **Ne partagez jamais** le fichier `.env` (contient les mots de passe FTP)
- ⚠️ **Sauvegardez régulièrement** `data/pointage.db`
- ⚠️ **Conservez une copie** de `config/employees.json`
- ✅ Le fichier `.env` est ignoré par Git
- ✅ Les mots de passe ne sont jamais loggés
- ✅ Protection anti-doublon : un même employé ne peut pas pointer 2 fois en moins de 5 secondes

---

## 🚀 Compiler en Exécutable Windows

Pour distribuer l'application sans installer Python :

```bash
python build_windows.py
```

Un fichier `.exe` sera créé dans `dist/PointageRFID/`

---

## 📝 Licence

**Propriétaire - Tous droits réservés**

Ce logiciel est fourni pour usage interne uniquement.  
Consultez le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🤝 Support

Pour toute question ou problème :

1. Consultez la [documentation](MANUEL_UTILISATION.md)
2. Vérifiez les [logs](logs/pointage.log)
3. Lancez le [diagnostic](diagnostic.py)
4. Contactez votre administrateur système

---

## 🎉 Merci !

Ce système a été développé pour simplifier la gestion du temps de travail.

**Bon pointage ! ⏰**
