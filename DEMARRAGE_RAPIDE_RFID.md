# 🚀 Démarrage rapide - Configuration RFID

## Installation

### 1. Installer la dépendance requests

```bash
cd /Users/webromandie/timbrage
source venv/bin/activate
pip install requests==2.31.0
```

OU utilisez le script d'installation :

```bash
chmod +x install_rfid_config.sh
./install_rfid_config.sh
```

### 2. Lancer l'application

```bash
./start.sh
```

## Utilisation en 5 étapes

### ✅ Étape 1 : Ouvrir la configuration
- Cliquez sur le bouton **"Configuration RFID"** (bouton vert) dans l'application

### ✅ Étape 2 : Se connecter au serveur
- URL de l'API : `https://prestest.ddev.site` (déjà pré-rempli)
- ID du compte : `2` (ou votre ID de compte)
- Cliquez sur **"Charger les employés"**

### ✅ Étape 3 : Sélectionner l'employé
- Choisissez l'employé dans la liste déroulante
- ✓ = badge déjà configuré | ✗ = pas de badge

### ✅ Étape 4 : Scanner le badge
- Cliquez sur **"Scannez le badge maintenant"**
- Passez le badge RFID sur le lecteur
- Le code s'affiche automatiquement

### ✅ Étape 5 : Enregistrer
- Cliquez sur **"Enregistrer l'association"**
- Un message de confirmation s'affiche

## Vérification

Sur le site web `prestest.ddev.site` :
1. Allez dans **Employés**
2. Cliquez sur l'employé configuré
3. Le code RFID devrait être visible dans le champ "carte"

## En cas de problème

### Le lecteur RFID n'est pas connecté
```bash
# Vérifier les ports série disponibles
python diagnostic_lecteur.py
```

### Erreur de connexion à l'API
- Vérifiez que le site est accessible : `curl https://prestest.ddev.site`
- Vérifiez l'URL dans l'interface de configuration

### Le badge ne se scanne pas
- Testez le lecteur dans l'application principale (écran d'accueil)
- Vérifiez que le lecteur est bien connecté (voyant vert)

## Documentation complète

Voir **CONFIGURATION_RFID.md** pour plus de détails.

## APIs créées sur le site web

✅ `/api_list_employees.php` - Liste des employés  
✅ `/api_save_rfid.php` - Enregistrement du badge

## Fichiers modifiés

### Application de timbrage
- ✅ `src/gui/rfid_config_panel.py` (nouveau)
- ✅ `src/gui/main_window.py` (bouton ajouté)
- ✅ `requirements.txt` (requests ajouté)
- ✅ `install_rfid_config.sh` (nouveau)
- ✅ `CONFIGURATION_RFID.md` (nouveau)
- ✅ `DEMARRAGE_RAPIDE_RFID.md` (ce fichier)

### Site web
- ✅ `api_list_employees.php` (nouveau)
- ✅ `api_save_rfid.php` (nouveau)

## C'est prêt ! 🎉

Lancez l'application et configurez vos badges RFID facilement ! 🏷️

