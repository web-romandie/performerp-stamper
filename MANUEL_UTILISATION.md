# Manuel d'Utilisation - Système de Pointage RFID

## Table des matières

1. [Installation](#installation)
2. [Configuration initiale](#configuration-initiale)
3. [Démarrage](#démarrage)
4. [Utilisation quotidienne](#utilisation-quotidienne)
5. [Panneau d'administration](#panneau-dadministration)
6. [Dépannage](#dépannage)

---

## Installation

### Prérequis

- **Windows 10/11** ou **macOS 10.14+**
- **Python 3.8 ou supérieur**
- **Lecteur RFID** connecté en USB/Serial
- Connexion Internet (pour l'envoi FTP)

### Étapes d'installation

1. **Téléchargez** ou **clonez** le projet dans un dossier de votre choix

2. **Installez Python** si ce n'est pas déjà fait :
   - Windows : Téléchargez depuis [python.org](https://www.python.org/downloads/)
   - macOS : `brew install python3` (si Homebrew est installé)

3. **Ouvrez un terminal** dans le dossier du projet

4. **Installez les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```
   
   Ou sur macOS/Linux :
   ```bash
   pip3 install -r requirements.txt
   ```

---

## Configuration initiale

### 1. Configuration automatique (recommandée)

Lancez le script de configuration :

**Windows :**
```bash
python setup_env.py
```

**macOS/Linux :**
```bash
python3 setup_env.py
```

Le script vous guidera pour configurer :
- Les paramètres FTP (hôte, utilisateur, mot de passe)
- Le nom de votre entreprise
- Les autres paramètres

### 2. Configuration manuelle

Si vous préférez configurer manuellement :

1. **Copiez** le fichier `.env.example` vers `.env`
2. **Éditez** le fichier `.env` avec vos paramètres :

```env
# Configuration FTP
FTP_HOST=ftp.votreserveur.com
FTP_PORT=21
FTP_USER=votre_utilisateur
FTP_PASSWORD=votre_mot_de_passe
FTP_REMOTE_PATH=/pointage

# Configuration générale
COMPANY_NAME=Votre Entreprise
AUTO_EXPORT_INTERVAL=3600
DEBUG_MODE=False

# Configuration RFID (laissez vide pour auto-détection)
RFID_PORT=
RFID_BAUDRATE=9600
RFID_TIMEOUT=1.0

# Interface
FULLSCREEN=False
```

### 3. Configurer les employés

Éditez le fichier `config/employees.json` :

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

**Important :**
- `rfid` : Le code de la puce RFID de l'employé
- `name` : Le nom complet de l'employé
- `employee_id` : Le matricule unique de l'employé

Pour connaître le code RFID d'une carte, vous pouvez :
1. Lancer l'application en mode DEBUG
2. Scanner la carte
3. Consulter les logs dans `logs/pointage.log`

---

## Démarrage

### Windows

**Double-cliquez** sur `start.bat` ou exécutez dans un terminal :
```bash
start.bat
```

### macOS/Linux

Exécutez dans un terminal :
```bash
./start.sh
```

Ou :
```bash
python3 main.py
```

---

## Utilisation quotidienne

### Interface principale

L'interface principale affiche :
- **L'heure et la date** actuelles
- **Une zone d'instruction** pour scanner le badge
- **Un message de feedback** après chaque scan
- **La liste des derniers pointages** de la journée

### Pointage d'un employé

1. L'employé **présente sa puce RFID** devant le lecteur
2. Le système **détecte automatiquement** s'il s'agit d'une entrée ou d'une sortie
3. Un **message de confirmation** s'affiche avec le nom de l'employé
4. Le pointage est **enregistré** dans la base de données

**Règles :**
- Si le dernier pointage était une SORTIE (ou aucun pointage) → **ENTRÉE**
- Si le dernier pointage était une ENTRÉE → **SORTIE**

### Messages possibles

- ✅ **"Bonjour [Nom] - ENTRÉE enregistrée"** (fond vert)
- ✅ **"Bonjour [Nom] - SORTIE enregistrée"** (fond vert)
- ❌ **"Badge non reconnu"** (fond rouge)

---

## Panneau d'administration

Pour accéder au panneau d'administration, cliquez sur le bouton **"Administration"** en bas de l'écran principal.

### Onglet "Pointages"

Consultez tous les pointages sur une période donnée :

1. **Sélectionnez** les dates de début et fin
2. Cliquez sur **"Rafraîchir"**
3. La liste affiche tous les pointages avec :
   - Date et heure
   - Matricule et nom de l'employé
   - Type (ENTRÉE/SORTIE)
   - Statut d'export

### Onglet "Rapports"

Générez des rapports d'activité :

- **Rapport du jour** : Tous les pointages de la journée par employé
- **Rapport de la semaine** : Heures travaillées par employé sur la semaine

Les rapports affichent :
- Le nombre total de pointages
- Le détail par employé
- Les heures calculées (pour le rapport hebdomadaire)

### Onglet "Export"

Gérez l'export et l'envoi des données :

#### Fonctions disponibles :

1. **Exporter en CSV uniquement**
   - Crée un fichier CSV dans le dossier `exports/`
   - Marque les pointages comme exportés
   - Format : `pointages_YYYYMMDD_HHMMSS.csv`

2. **Exporter et envoyer par FTP**
   - Exporte en CSV
   - Envoie le fichier sur le serveur FTP configuré
   - Marque les pointages comme exportés

3. **Tester la connexion FTP**
   - Vérifie que les paramètres FTP sont corrects
   - Affiche un message de succès ou d'erreur

#### Format du fichier CSV

Le fichier CSV est au format suivant :
```
ID;Matricule;Nom;RFID;Date;Heure;Type
1;EMP001;Jean Dupont;1234567890;26/11/2025;08:30:00;ENTREE
2;EMP001;Jean Dupont;1234567890;26/11/2025;17:00:00;SORTIE
```

- **Séparateur** : `;` (point-virgule)
- **Encodage** : UTF-8 avec BOM
- **Format de date** : JJ/MM/AAAA
- **Format d'heure** : HH:MM:SS

---

## Dépannage

### Le lecteur RFID n'est pas détecté

**Solutions :**
1. Vérifiez que le lecteur est **bien connecté** en USB
2. Vérifiez dans le **Gestionnaire de périphériques** (Windows) ou **À propos de ce Mac > Rapport système** (macOS)
3. **Redémarrez** l'application
4. Consultez les logs dans `logs/pointage.log` pour voir les ports détectés
5. Configurez manuellement le port dans `.env` :
   ```env
   RFID_PORT=COM3  # Windows
   # ou
   RFID_PORT=/dev/ttyUSB0  # Linux
   # ou
   RFID_PORT=/dev/cu.usbserial  # macOS
   ```

### Un badge n'est pas reconnu

**Solutions :**
1. Vérifiez que l'employé est bien dans `config/employees.json`
2. Vérifiez que le code RFID est correct
3. Activez le mode DEBUG dans `.env` :
   ```env
   DEBUG_MODE=True
   ```
4. Scannez le badge et consultez `logs/pointage.log` pour voir le code lu

### L'envoi FTP échoue

**Vérifications :**
1. **Testez la connexion** depuis le panneau d'administration
2. Vérifiez vos **paramètres FTP** dans `.env`
3. Vérifiez que vous avez **accès Internet**
4. Vérifiez les **droits d'écriture** sur le serveur FTP
5. Testez avec un client FTP (FileZilla) pour valider les identifiants

### L'application ne démarre pas

**Solutions :**
1. Vérifiez que **Python 3.8+** est installé :
   ```bash
   python --version
   ```
2. Vérifiez que les **dépendances** sont installées :
   ```bash
   pip install -r requirements.txt
   ```
3. Consultez les **logs d'erreur** dans `logs/pointage.log`
4. Sur macOS, installez les dépendances système si nécessaire :
   ```bash
   brew install python-tk
   ```

### La base de données est corrompue

**Solution :**
1. **Sauvegardez** le fichier `data/pointage.db`
2. **Supprimez** le fichier
3. **Redémarrez** l'application (une nouvelle base sera créée)
4. Si nécessaire, **récupérez les données** de la sauvegarde avec un outil SQLite

---

## Logs et diagnostics

### Fichiers de logs

Tous les logs sont dans le dossier `logs/` :
- `pointage.log` : Log principal de l'application

### Activer le mode DEBUG

Dans `.env` :
```env
DEBUG_MODE=True
```

Le mode DEBUG affiche plus d'informations dans les logs, notamment :
- Les codes RFID lus
- Les requêtes SQL
- Les détails des connexions FTP
- Les erreurs détaillées

---

## Support technique

Pour toute assistance :
1. Consultez d'abord ce manuel
2. Vérifiez les logs dans `logs/pointage.log`
3. Contactez votre administrateur système

---

## Notes importantes

- ⚠️ **Sauvegardez régulièrement** la base de données `data/pointage.db`
- ⚠️ **Testez la connexion FTP** régulièrement
- ⚠️ **Vérifiez les exports** pour s'assurer qu'ils fonctionnent
- ⚠️ **Ne partagez jamais** le fichier `.env` (il contient des mots de passe)
- ✅ **Conservez une copie** de `config/employees.json`



