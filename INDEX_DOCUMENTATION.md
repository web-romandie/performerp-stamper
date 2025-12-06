# 📚 Index de la Documentation

Bienvenue dans le système de pointage RFID ! Voici un guide pour naviguer dans la documentation.

> ⚠️ **Problème d'installation ?** → **[DEPANNAGE_INSTALLATION.md](DEPANNAGE_INSTALLATION.md)**

---

## 🚀 Pour Commencer

### Vous installez pour la première fois ?

→ **[PREMIERE_INSTALLATION.md](PREMIERE_INSTALLATION.md)**  
Guide complet étape par étape pour votre première installation.

### Installation rapide (utilisateur expérimenté) ?

→ **[QUICK_START.md](QUICK_START.md)**  
Démarrage rapide en 3 étapes.

### Installation sur Windows ?

→ **[INSTALLATION_WINDOWS.md](INSTALLATION_WINDOWS.md)**  
Guide détaillé spécifique Windows avec configuration du terminal tactile.

### Installation sur Raspberry Pi ? 🥧

→ **[RASPBERRY_QUICKSTART.md](RASPBERRY_QUICKSTART.md)** - 4 étapes rapides  
→ **[INSTALLATION_RASPBERRY.md](INSTALLATION_RASPBERRY.md)** - Guide complet

---

## 📖 Documentation Principale

### Vue d'ensemble du projet

→ **[README.md](README.md)**  
Présentation complète du système, fonctionnalités, structure du projet.

### Manuel d'utilisation

→ **[MANUEL_UTILISATION.md](MANUEL_UTILISATION.md)**  
Guide utilisateur complet avec toutes les fonctionnalités détaillées.

### Historique des versions

→ **[CHANGELOG.md](CHANGELOG.md)**  
Liste de toutes les modifications et versions du logiciel.

---

## 🔧 Guides Techniques

### Configuration

| Fichier                 | Description                                |
| ----------------------- | ------------------------------------------ |
| `.env`                  | Configuration principale (FTP, RFID, etc.) |
| `config/employees.json` | Liste des employés avec codes RFID         |
| `config/settings.py`    | Configuration avancée (ne pas modifier)    |

### Scripts Utiles

| Script                     | Usage                           | Description                         |
| -------------------------- | ------------------------------- | ----------------------------------- |
| `main.py`                  | `python main.py`                | Lance l'application                 |
| `setup_env.py`             | `python setup_env.py`           | Configuration initiale guidée       |
| `diagnostic.py`            | `python diagnostic.py`          | Vérifie l'installation              |
| `test_rfid_simulator.py`   | `python test_rfid_simulator.py` | Test sans lecteur RFID              |
| `install_dependencies.bat` | Double-clic                     | Installation auto (Windows) ⭐      |
| `build_windows.py`         | `python build_windows.py`       | Compile en .exe                     |
| `start.bat`                | Double-clic                     | Démarrage automatique (Windows)     |
| `start.sh`                 | `./start.sh`                    | Démarrage automatique (macOS/Linux) |

---

## 🎯 Par Tâche

### Installation & Configuration

1. **[Première installation complète](PREMIERE_INSTALLATION.md)** ✨ RECOMMANDÉ

   - Installation de Python
   - Installation du logiciel
   - Configuration initiale
   - Ajout des employés
   - Tests

2. **[Installation rapide](QUICK_START.md)**

   - Pour utilisateurs expérimentés
   - 3 étapes simples

3. **[Installation Windows spécifique](INSTALLATION_WINDOWS.md)**
   - Configuration terminal tactile QCT
   - Optimisation Windows
   - Démarrage automatique

4. **[Installation Raspberry Pi 🥧](INSTALLATION_RASPBERRY.md)** ⭐ NOUVEAU
   - Guide complet étape par étape
   - Configuration du système
   - Écran tactile et démarrage auto
   - Monitoring et maintenance
   - **[Version rapide (4 étapes)](RASPBERRY_QUICKSTART.md)**

### Utilisation Quotidienne

- **[Manuel d'utilisation → Utilisation quotidienne](MANUEL_UTILISATION.md#utilisation-quotidienne)**

  - Pointage des employés
  - Lecture des messages
  - Interface principale

- **[Manuel d'utilisation → Panneau d'administration](MANUEL_UTILISATION.md#panneau-dadministration)**
  - Consultation des pointages
  - Génération de rapports
  - Export CSV et FTP

### Dépannage

- **[Dépannage Installation](DEPANNAGE_INSTALLATION.md)** ⚠️ NOUVEAU

  - "pip n'est pas reconnu"
  - "python n'est pas reconnu"
  - Erreurs d'installation
  - Problèmes de permissions
  - Guide complet de diagnostic

- **[Manuel d'utilisation → Dépannage](MANUEL_UTILISATION.md#dépannage)**

  - Lecteur RFID non détecté
  - Badge non reconnu
  - Problèmes FTP
  - Autres problèmes courants

- **[Quick Start → Dépannage rapide](QUICK_START.md#dépannage-rapide)**
  - Solutions rapides aux problèmes fréquents

### Administration

- **[Configuration des employés](QUICK_START.md#configuration-des-employés)**

  - Format du fichier JSON
  - Obtenir les codes RFID

- **[Configuration FTP](MANUEL_UTILISATION.md#export-des-données)**
  - Paramètres FTP
  - Test de connexion
  - Format des exports

---

## 👥 Par Profil Utilisateur

### 🏢 Administrateur Système

**Installation :**

1. [PREMIERE_INSTALLATION.md](PREMIERE_INSTALLATION.md) - Installation complète
2. [INSTALLATION_WINDOWS.md](INSTALLATION_WINDOWS.md) - Spécifique Windows

**Configuration :**

- Configuration FTP : [MANUEL_UTILISATION.md](MANUEL_UTILISATION.md#configuration)
- Gestion des employés : `config/employees.json`
- Paramètres avancés : `.env`

**Maintenance :**

- Logs : `logs/pointage.log`
- Base de données : `data/pointage.db`
- Diagnostic : `python diagnostic.py`

### 👨‍💼 Responsable RH

**Utilisation :**

- [MANUEL_UTILISATION.md](MANUEL_UTILISATION.md) - Manuel complet
- Panneau d'administration → Onglet "Rapports"
- Panneau d'administration → Onglet "Export"

**Rapports :**

- Rapport journalier
- Rapport hebdomadaire
- Export CSV

### 👷 Employé

**Utilisation simple :**

- Présenter le badge devant le lecteur
- Vérifier le message de confirmation
- C'est tout ! 😊

---

## 📊 Par Fonctionnalité

### Pointage RFID

- [README.md → Fonctionnalités](README.md#-fonctionnalités)
- [MANUEL_UTILISATION.md → Pointage d'un employé](MANUEL_UTILISATION.md#pointage-dun-employé)

### Base de Données

- Format : SQLite (`data/pointage.db`)
- Structure : Voir `src/database/db_manager.py`
- Sauvegarde : [PREMIERE_INSTALLATION.md → Sauvegardes](PREMIERE_INSTALLATION.md#-étape-10--sauvegardes)

### Export CSV

- [README.md → Format d'Export CSV](README.md#-format-dexport-csv)
- [MANUEL_UTILISATION.md → Export des données](MANUEL_UTILISATION.md#export-des-données)

### Envoi FTP

- Configuration : `.env`
- Test : Panneau admin → Onglet "Export" → "Tester la connexion FTP"
- Dépannage : [MANUEL_UTILISATION.md → Dépannage](MANUEL_UTILISATION.md#lenvoi-ftp-échoue)

### Rapports

- [MANUEL_UTILISATION.md → Onglet Rapports](MANUEL_UTILISATION.md#onglet-rapports)
- Rapport journalier
- Rapport hebdomadaire
- Calcul des heures

---

## 🛠️ Développement

### Structure du Code

```
src/
├── gui/           # Interface graphique (PyQt5)
├── rfid/          # Gestion lecteur RFID
├── database/      # Base de données SQLite
└── export/        # Export CSV et FTP
```

### Tests

- **Test sans RFID :** `python test_rfid_simulator.py`
- **Diagnostic :** `python diagnostic.py`
- **Mode DEBUG :** Activer dans `.env`

### Build

- **Exécutable Windows :** `python build_windows.py`

---

## 🆘 Aide Rapide

### Commandes Essentielles

```bash
# Lancer l'application
python main.py

# Configuration initiale
python setup_env.py

# Vérifier l'installation
python diagnostic.py

# Test sans lecteur RFID
python test_rfid_simulator.py

# Consulter les logs
cat logs/pointage.log  # macOS/Linux
type logs\pointage.log  # Windows
```

### Fichiers Importants

| Fichier                 | Description               | À sauvegarder |
| ----------------------- | ------------------------- | ------------- |
| `.env`                  | Configuration (FTP, etc.) | ✅ OUI        |
| `config/employees.json` | Liste employés            | ✅ OUI        |
| `data/pointage.db`      | Base de données           | ✅ OUI        |
| `logs/pointage.log`     | Logs                      | Optionnel     |

### Résolution de Problèmes

1. **Consultez les logs :** `logs/pointage.log`
2. **Activez le DEBUG :** Éditez `.env` → `DEBUG_MODE=True`
3. **Lancez le diagnostic :** `python diagnostic.py`
4. **Consultez la doc :** [MANUEL_UTILISATION.md → Dépannage](MANUEL_UTILISATION.md#dépannage)

---

## 📞 Support

### Auto-assistance

1. Consultez cette documentation
2. Vérifiez les logs
3. Lancez le diagnostic
4. Consultez le CHANGELOG pour les problèmes connus

### Contact

Pour un support technique, contactez votre administrateur système avec :

- La version du logiciel (voir CHANGELOG.md)
- Le contenu de `logs/pointage.log`
- La description du problème

---

## 📝 Licence

**Propriétaire - Tous droits réservés**

Consultez le fichier [LICENSE](LICENSE) pour plus d'informations.

---

## 🎯 Liens Rapides

| Je veux...                      | Consulter...                                                       |
| ------------------------------- | ------------------------------------------------------------------ |
| Installer pour la première fois | [PREMIERE_INSTALLATION.md](PREMIERE_INSTALLATION.md)               |
| Démarrer rapidement             | [QUICK_START.md](QUICK_START.md)                                   |
| Comprendre le système           | [README.md](README.md)                                             |
| Utiliser l'application          | [MANUEL_UTILISATION.md](MANUEL_UTILISATION.md)                     |
| Installer sur Windows           | [INSTALLATION_WINDOWS.md](INSTALLATION_WINDOWS.md)                 |
| Résoudre un problème            | [MANUEL_UTILISATION.md#dépannage](MANUEL_UTILISATION.md#dépannage) |
| Voir l'historique               | [CHANGELOG.md](CHANGELOG.md)                                       |
| Tester sans RFID                | `python test_rfid_simulator.py`                                    |
| Vérifier l'installation         | `python diagnostic.py`                                             |

---

**Bonne utilisation ! 📚**
