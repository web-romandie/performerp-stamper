# 🚀 Guide de Démarrage Rapide

## Installation en 3 étapes

### 1️⃣ Installer Python

**Windows :**

- Téléchargez Python 3.11+ depuis [python.org](https://www.python.org/downloads/)
- ⚠️ Cochez "Add Python to PATH" pendant l'installation

**macOS :**

```bash
brew install python3
```

### 2️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

Ou sur macOS/Linux :

```bash
pip3 install -r requirements.txt
```

### 3️⃣ Configuration initiale

```bash
python setup_env.py
```

Suivez les instructions pour configurer :

- Vos paramètres FTP
- Le nom de votre entreprise
- Les autres options

---

## Premier lancement

### Test sans lecteur RFID (simulateur)

```bash
python test_rfid_simulator.py
```

Le simulateur vous permet de tester l'application sans lecteur physique.

### Lancement normal

**Windows :**

```bash
start.bat
```

**macOS/Linux :**

```bash
./start.sh
```

Ou directement :

```bash
python main.py
```

---

## Configuration des employés

Éditez `config/employees.json` :

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

**💡 Astuce :** Pour obtenir le code RFID d'une carte :

1. Activez le DEBUG dans `.env` : `DEBUG_MODE=True`
2. Lancez l'application
3. Scannez la carte
4. Le code apparaît dans `logs/pointage.log`

---

## Utilisation basique

### Interface principale

- **Présentez votre badge** devant le lecteur RFID
- Le système détecte automatiquement ENTRÉE ou SORTIE
- Un message de confirmation s'affiche

### Panneau d'administration

- Cliquez sur **"Administration"**
- Consultez les pointages
- Générez des rapports
- Exportez en CSV
- Testez la connexion FTP

---

## Structure des fichiers

```
timbrage/
├── main.py              # Point d'entrée
├── start.bat            # Démarrage Windows
├── start.sh             # Démarrage macOS/Linux
├── setup_env.py         # Configuration initiale
├── .env                 # Configuration (créé par setup)
├── config/
│   └── employees.json   # Liste des employés
├── src/
│   ├── gui/            # Interface graphique
│   ├── rfid/           # Gestion RFID
│   ├── database/       # Base de données
│   └── export/         # Export CSV et FTP
├── data/
│   └── pointage.db     # Base de données SQLite
├── logs/
│   └── pointage.log    # Logs de l'application
└── exports/            # Fichiers CSV exportés
```

---

## Dépannage rapide

### Le lecteur RFID n'est pas détecté

1. Vérifiez qu'il est bien branché
2. Redémarrez l'application
3. Consultez `logs/pointage.log`
4. Configurez manuellement le port dans `.env` :
   ```
   RFID_PORT=COM3  # Windows
   RFID_PORT=/dev/ttyUSB0  # Linux
   ```

### L'export FTP échoue

1. Cliquez sur "Administration" → "Export"
2. Testez la connexion FTP
3. Vérifiez vos paramètres dans `.env`

### Un badge n'est pas reconnu

1. Vérifiez qu'il est dans `config/employees.json`
2. Activez le mode DEBUG dans `.env`
3. Scannez le badge et consultez les logs

---

## Documentation complète

- 📖 **README.md** : Vue d'ensemble du projet
- 📘 **MANUEL_UTILISATION.md** : Guide utilisateur complet
- 🪟 **INSTALLATION_WINDOWS.md** : Guide spécifique Windows
- 📝 **CHANGELOG.md** : Historique des versions

---

## Support

Pour toute question :

1. Consultez la documentation
2. Vérifiez les logs : `logs/pointage.log`
3. Activez le mode DEBUG : `DEBUG_MODE=True` dans `.env`

---

## Commandes utiles

```bash
# Lancer l'application
python main.py

# Lancer le simulateur (test sans lecteur RFID)
python test_rfid_simulator.py

# Configuration initiale
python setup_env.py

# Compiler en .exe Windows (nécessite PyInstaller)
python build_windows.py
```

---

**🎉 Vous êtes prêt ! Bonne utilisation !**


