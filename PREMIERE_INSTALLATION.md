# 🎯 Guide de Première Installation

Ce guide vous accompagne étape par étape pour installer et configurer le système de pointage pour la toute première fois.

---

## ✅ Checklist Avant Installation

Avant de commencer, assurez-vous d'avoir :

- [ ] Un ordinateur Windows 10/11 ou macOS
- [ ] Une connexion Internet
- [ ] Le lecteur RFID (ou prévoir de tester en mode simulateur)
- [ ] Les informations de connexion FTP de votre serveur
- [ ] La liste de vos employés avec leurs badges RFID

---

## 📥 Étape 1 : Obtenir Python

### Windows

1. Allez sur [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Téléchargez **Python 3.11** ou plus récent
3. **IMPORTANT** : Pendant l'installation
   - ✅ **Cochez "Add Python to PATH"** (très important !)
   - ✅ Cliquez sur "Install Now"
4. Attendez la fin de l'installation

**Vérification :**
- Ouvrez l'Invite de commandes (Win + R, tapez `cmd`)
- Tapez : `python --version`
- Vous devriez voir : `Python 3.11.x`

### macOS

**Option 1 : Avec Homebrew (recommandé)**
```bash
brew install python3
```

**Option 2 : Installateur officiel**
1. Téléchargez depuis [python.org](https://www.python.org/downloads/)
2. Installez le fichier `.pkg`

**Vérification :**
```bash
python3 --version
```

---

## 📦 Étape 2 : Préparer le Logiciel

### Option A : Vous avez reçu un dossier ZIP

1. **Décompressez** le fichier `timbrage.zip` sur votre bureau
2. **Renommez** le dossier si nécessaire (ex: `PointageRFID`)
3. **Déplacez** le dossier vers un emplacement permanent :
   - Windows : `C:\PointageRFID\`
   - macOS : `/Applications/PointageRFID/` ou `~/Applications/PointageRFID/`

### Option B : Vous avez cloné depuis Git

```bash
git clone [url-du-repo] timbrage
cd timbrage
```

---

## 🔧 Étape 3 : Installation Automatique

### Windows

1. **Ouvrez** le dossier du projet
2. **Double-cliquez** sur `start.bat`
3. Le script va :
   - Vérifier que Python est installé
   - Installer automatiquement les dépendances
   - Vous demander de configurer le système
   - Lancer l'application

**Si une erreur apparaît :**
- Vérifiez que Python est bien dans le PATH
- Ouvrez une nouvelle fenêtre d'invite de commandes

### macOS / Linux

1. **Ouvrez le Terminal**
2. **Naviguez** vers le dossier :
   ```bash
   cd /chemin/vers/timbrage
   ```
3. **Rendez le script exécutable** :
   ```bash
   chmod +x start.sh
   ```
4. **Lancez le script** :
   ```bash
   ./start.sh
   ```

---

## ⚙️ Étape 4 : Configuration Initiale

Lors du premier lancement, le script `setup_env.py` va se lancer automatiquement.

### Questions posées :

#### 1. Configuration FTP

```
Hôte FTP (ex: ftp.example.com): 
```
→ Entrez l'adresse de votre serveur FTP (ex: `ftp.monentreprise.com`)

```
Port FTP (par défaut: 21): 
```
→ Appuyez sur Entrée pour garder 21, ou entrez un autre port

```
Nom d'utilisateur FTP: 
```
→ Votre nom d'utilisateur FTP

```
Mot de passe FTP: 
```
→ Votre mot de passe FTP (ne s'affiche pas pendant la saisie)

```
Chemin distant (par défaut: /pointage): 
```
→ Le dossier sur le serveur où envoyer les fichiers (ex: `/data/pointage`)

#### 2. Configuration Générale

```
Nom de l'entreprise: 
```
→ Le nom de votre entreprise (ex: `Acme Corporation`)

**C'est terminé !** Un fichier `.env` a été créé avec votre configuration.

---

## 👥 Étape 5 : Ajouter vos Employés

### Préparer les Données

Avant de modifier le fichier, préparez une liste avec :
- Le **nom** de chaque employé
- Son **matricule** (ID unique)
- Son **code RFID** (on verra comment l'obtenir)

### Modifier le Fichier

1. **Ouvrez** le fichier `config/employees.json` avec un éditeur de texte
   - Windows : Bloc-notes, Notepad++, VS Code
   - macOS : TextEdit, VS Code

2. **Modifiez** le contenu :

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
    },
    {
      "rfid": "1122334455",
      "name": "Paul Durand",
      "employee_id": "EMP003"
    }
  ]
}
```

3. **Sauvegardez** le fichier

### 🔍 Comment obtenir les codes RFID ?

Si vous ne connaissez pas les codes RFID des badges :

**Méthode 1 : Mode DEBUG**

1. Ouvrez le fichier `.env`
2. Changez `DEBUG_MODE=False` en `DEBUG_MODE=True`
3. Sauvegardez
4. Lancez l'application
5. Scannez un badge
6. Ouvrez `logs/pointage.log`
7. Le code RFID sera visible dans les logs

**Méthode 2 : Test avec codes temporaires**

1. Mettez des codes temporaires (ex: "TEMP001", "TEMP002")
2. Lancez l'application en mode DEBUG
3. Scannez les badges un par un
4. Notez les vrais codes dans les logs
5. Mettez à jour `employees.json` avec les vrais codes

---

## 🔌 Étape 6 : Connecter le Lecteur RFID

### Installation Physique

1. **Branchez** le lecteur RFID en USB
2. **Attendez** que Windows/macOS installe les pilotes
3. Le lecteur devrait être **détecté automatiquement**

### Vérification

#### Windows

1. Ouvrez le **Gestionnaire de périphériques**
   - Clic droit sur le menu Démarrer → Gestionnaire de périphériques
2. Dépliez **"Ports (COM et LPT)"**
3. Vous devriez voir votre lecteur (ex: "USB Serial Port (COM3)")
4. **Notez le numéro** (ex: COM3)

#### macOS

1. Ouvrez le **Terminal**
2. Tapez : `ls /dev/cu.*`
3. Vous devriez voir votre lecteur (ex: `/dev/cu.usbserial`)

### Configuration Manuelle (si nécessaire)

Si le lecteur n'est pas détecté automatiquement :

1. Ouvrez le fichier `.env`
2. Modifiez la ligne :
   ```env
   RFID_PORT=COM3  # Windows
   # ou
   RFID_PORT=/dev/cu.usbserial  # macOS
   ```
3. Sauvegardez

---

## ✅ Étape 7 : Premier Test

### Test sans lecteur RFID (Simulateur)

Si vous n'avez pas encore le lecteur RFID :

```bash
python test_rfid_simulator.py
```

Une fenêtre de contrôle apparaîtra avec des boutons pour simuler des scans.

### Test avec le lecteur RFID réel

1. **Lancez l'application** :
   - Windows : `start.bat`
   - macOS/Linux : `./start.sh`

2. **L'interface principale** s'affiche

3. **Scannez un badge** devant le lecteur

4. **Vérifiez** :
   - ✅ Le nom de l'employé s'affiche
   - ✅ Un message vert indique "ENTRÉE enregistrée"
   - ✅ Le pointage apparaît dans la liste en bas

5. **Scannez à nouveau** le même badge
   - ✅ Un message vert indique "SORTIE enregistrée"

### Vérifier les Données

1. Cliquez sur **"Administration"**
2. Allez dans l'onglet **"Pointages"**
3. Vérifiez que vos tests apparaissent dans la liste

---

## 🌐 Étape 8 : Tester l'Export FTP

### Test de Connexion

1. Dans le panneau d'administration
2. Allez dans l'onglet **"Export"**
3. Cliquez sur **"Tester la connexion FTP"**
4. Un message devrait indiquer : **"Connexion FTP réussie!"**

### Premier Export

1. Faites quelques pointages de test
2. Dans l'onglet "Export", cliquez sur **"Exporter et envoyer par FTP"**
3. Vérifiez que le fichier apparaît sur votre serveur FTP

**En cas d'échec :**
- Vérifiez vos paramètres FTP dans `.env`
- Testez avec un client FTP (FileZilla) pour valider vos accès
- Consultez `logs/pointage.log` pour plus de détails

---

## 🎯 Étape 9 : Configuration Finale

### Pour un Terminal de Production

Éditez le fichier `.env` :

```env
# Désactiver le mode DEBUG
DEBUG_MODE=False

# Activer le plein écran (optionnel)
FULLSCREEN=True

# Intervalle d'export auto (en secondes)
# 3600 = toutes les heures
AUTO_EXPORT_INTERVAL=3600
```

### Démarrage Automatique (Windows)

1. **Créez un raccourci** de `start.bat`
2. Appuyez sur **Win + R**
3. Tapez : `shell:startup` et appuyez sur Entrée
4. **Collez le raccourci** dans le dossier qui s'ouvre
5. L'application démarrera automatiquement au démarrage de Windows

### Démarrage Automatique (macOS)

1. Ouvrez **Préférences Système** → **Utilisateurs et groupes**
2. Allez dans **Ouverture**
3. Cliquez sur **+** et ajoutez le script `start.sh`

---

## 🛡️ Étape 10 : Sauvegardes

### Fichiers à Sauvegarder Régulièrement

Configurez une sauvegarde automatique de :

```
timbrage/
├── .env                      # Configuration (IMPORTANT)
├── config/employees.json     # Liste des employés
├── data/pointage.db          # Base de données
└── logs/pointage.log         # Logs (optionnel)
```

**Recommandation :**
- Sauvegardez sur un **disque réseau** ou **cloud**
- Fréquence : **quotidienne** pour `pointage.db`
- Conservez les sauvegardes pendant **au moins 3 mois**

---

## 📋 Checklist Finale

Avant de mettre en production, vérifiez :

- [ ] Python installé et fonctionnel
- [ ] Dépendances installées (via `pip install -r requirements.txt`)
- [ ] Fichier `.env` configuré avec les paramètres FTP
- [ ] Tous les employés ajoutés dans `config/employees.json`
- [ ] Lecteur RFID connecté et détecté
- [ ] Test de pointage réussi
- [ ] Test d'export FTP réussi
- [ ] Mode DEBUG désactivé (`DEBUG_MODE=False`)
- [ ] Démarrage automatique configuré (optionnel)
- [ ] Sauvegardes configurées
- [ ] Formation des utilisateurs effectuée

---

## 🆘 Besoin d'Aide ?

### Outils de Diagnostic

```bash
# Vérifier que tout est OK
python diagnostic.py
```

### Consulter les Logs

```bash
# Windows
type logs\pointage.log

# macOS/Linux
cat logs/pointage.log
```

### Documentation

- [QUICK_START.md](QUICK_START.md) - Démarrage rapide
- [MANUEL_UTILISATION.md](MANUEL_UTILISATION.md) - Manuel complet
- [INSTALLATION_WINDOWS.md](INSTALLATION_WINDOWS.md) - Guide Windows détaillé

---

## 🎉 Félicitations !

Votre système de pointage est maintenant opérationnel !

**Prochaines étapes :**
1. Formez vos employés à l'utilisation
2. Surveillez les logs pendant les premiers jours
3. Vérifiez régulièrement les exports FTP

**Bon pointage ! ⏰**



