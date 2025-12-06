# 🔧 Dépannage Installation - Problèmes Courants

Ce guide résout les problèmes d'installation les plus fréquents.

---

## ❌ Erreur : "pip n'est pas reconnu"

### Symptôme
```
'pip' n'est pas reconnu en tant que commande interne
ou externe, un programme exécutable ou un fichier de commandes.
```

### Cause
Python est installé mais `pip` n'est pas dans le PATH système.

### ✅ Solutions

#### Solution 1 : Utiliser python -m pip (RECOMMANDÉ)

Au lieu de :
```bash
pip install -r requirements.txt
```

Utilisez :
```bash
python -m pip install -r requirements.txt
```

Ou sur certains systèmes :
```bash
py -m pip install -r requirements.txt
```

#### Solution 2 : Utiliser le script automatique

Double-cliquez sur :
```
install_dependencies.bat
```

Ce script détecte automatiquement votre configuration et installe tout.

#### Solution 3 : Ajouter pip au PATH

1. Trouvez où Python est installé :
   ```bash
   where python
   ```
   Résultat typique : `C:\Users\VotreNom\AppData\Local\Programs\Python\Python311\python.exe`

2. Le dossier de pip est : `C:\Users\VotreNom\AppData\Local\Programs\Python\Python311\Scripts\`

3. Ajoutez ce chemin au PATH :
   - Clic droit sur "Ce PC" → Propriétés
   - Paramètres système avancés
   - Variables d'environnement
   - Dans "Variables système", sélectionnez "Path" → Modifier
   - Nouveau → Collez le chemin vers Scripts
   - OK sur tout

4. **Redémarrez** votre invite de commandes

5. Testez :
   ```bash
   pip --version
   ```

#### Solution 4 : Réinstaller Python avec PATH

1. Désinstallez Python (Panneau de configuration → Programmes)
2. Téléchargez Python depuis [python.org](https://www.python.org/downloads/)
3. **IMPORTANT** : Cochez "Add Python to PATH" pendant l'installation
4. Installez
5. Testez :
   ```bash
   python --version
   pip --version
   ```

---

## ❌ Erreur : "python n'est pas reconnu"

### Symptôme
```
'python' n'est pas reconnu en tant que commande interne
ou externe, un programme exécutable ou un fichier de commandes.
```

### Cause
Python n'est pas installé ou pas dans le PATH.

### ✅ Solutions

#### Solution 1 : Vérifier si Python est installé

Essayez ces commandes une par une :
```bash
python --version
py --version
python3 --version
```

Si l'une fonctionne, utilisez cette commande pour tout.

#### Solution 2 : Installer Python

1. Allez sur [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Téléchargez Python 3.11 ou plus récent
3. **COCHEZ "Add Python to PATH"** (très important !)
4. Cliquez "Install Now"
5. Attendez la fin
6. Redémarrez votre ordinateur
7. Testez :
   ```bash
   python --version
   ```

---

## ❌ Erreur : "Microsoft Visual C++ required"

### Symptôme
```
error: Microsoft Visual C++ 14.0 or greater is required
```

### Cause
Certaines bibliothèques Python nécessitent un compilateur C++.

### ✅ Solution

#### Option 1 : Installer Visual C++ Redistributable

1. Téléchargez depuis [Microsoft](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. Installez le fichier
3. Redémarrez
4. Relancez l'installation des dépendances

#### Option 2 : Installer Build Tools

1. Téléchargez [Build Tools for Visual Studio](https://visualstudio.microsoft.com/downloads/)
2. Sélectionnez "Build Tools for Visual Studio"
3. Dans l'installeur, cochez "C++ build tools"
4. Installez
5. Redémarrez
6. Relancez l'installation

---

## ❌ Erreur : "Permission denied" / "Access denied"

### Symptôme
```
PermissionError: [WinError 5] Access denied
```

### Cause
Droits administrateur nécessaires.

### ✅ Solutions

#### Solution 1 : Installation utilisateur

Utilisez l'option `--user` :
```bash
python -m pip install --user -r requirements.txt
```

#### Solution 2 : Exécuter en administrateur

1. Clic droit sur `install_dependencies.bat`
2. "Exécuter en tant qu'administrateur"

Ou dans l'invite de commandes :
1. Cherchez "cmd" dans le menu Démarrer
2. Clic droit → "Exécuter en tant qu'administrateur"
3. Naviguez vers le dossier :
   ```bash
   cd C:\chemin\vers\timbrage
   ```
4. Lancez l'installation :
   ```bash
   python -m pip install -r requirements.txt
   ```

---

## ❌ Erreur : "No module named 'PyQt5'"

### Symptôme
```
ModuleNotFoundError: No module named 'PyQt5'
```

### Cause
PyQt5 n'est pas installé ou installé pour une mauvaise version de Python.

### ✅ Solutions

#### Solution 1 : Installer manuellement

```bash
python -m pip install PyQt5
python -m pip install pyserial
python -m pip install python-dotenv
```

#### Solution 2 : Vérifier la version de Python

Vous avez peut-être plusieurs versions de Python installées.

```bash
# Vérifier quelle version lance l'app
python --version

# Installer pour cette version spécifique
python -m pip install -r requirements.txt
```

#### Solution 3 : Utiliser un environnement virtuel

```bash
# Créer un environnement virtuel
python -m venv venv

# L'activer (Windows)
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'app
python main.py
```

---

## ❌ Erreur : Lecteur RFID non détecté

### Symptôme
L'application démarre mais le lecteur RFID n'est pas détecté.

### ✅ Solutions

Voir le guide complet : [MANUEL_UTILISATION.md - Dépannage](MANUEL_UTILISATION.md#le-lecteur-rfid-nest-pas-détecté)

**Rapide :**
1. Vérifiez que le lecteur est branché
2. Consultez `logs/pointage.log`
3. Testez avec le simulateur : `python test_rfid_simulator.py`
4. Configurez manuellement le port dans `.env`

---

## ❌ Erreur : "SSL Certificate verify failed"

### Symptôme
```
SSL: CERTIFICATE_VERIFY_FAILED
```

### Cause
Problème de certificats SSL (souvent derrière un proxy d'entreprise).

### ✅ Solutions

#### Solution 1 : Mettre à jour les certificats

```bash
python -m pip install --upgrade certifi
```

#### Solution 2 : Installation avec option trusted-host

```bash
python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

---

## 🆘 Procédure de Diagnostic Complète

Si vous avez toujours des problèmes, suivez cette procédure :

### Étape 1 : Vérifier Python

```bash
# Tester toutes les commandes possibles
python --version
py --version
python3 --version

# Noter celle qui fonctionne
```

### Étape 2 : Vérifier pip

```bash
# Avec la commande qui fonctionne ci-dessus
python -m pip --version

# Ou
py -m pip --version
```

### Étape 3 : Installer les dépendances une par une

```bash
python -m pip install PyQt5
python -m pip install pyserial
python -m pip install python-dotenv
```

Notez quelle bibliothèque pose problème.

### Étape 4 : Lancer le diagnostic

```bash
python diagnostic.py
```

### Étape 5 : Consulter les logs

Si l'application démarre, consultez :
```
logs/pointage.log
```

---

## 📞 Aide Supplémentaire

### Informations à fournir pour obtenir de l'aide

Si aucune solution ne fonctionne, préparez ces informations :

1. **Système d'exploitation :**
   ```bash
   ver  # Windows
   ```

2. **Version de Python :**
   ```bash
   python --version
   py --version
   python3 --version
   ```

3. **Message d'erreur complet**
   Copiez tout le message d'erreur

4. **Résultat du diagnostic :**
   ```bash
   python diagnostic.py
   ```

5. **Capture d'écran de l'erreur**

---

## ✅ Vérification Finale

Une fois les dépendances installées, vérifiez que tout fonctionne :

### Test 1 : Diagnostic
```bash
python diagnostic.py
```
Devrait afficher "✓ Tous les prérequis sont en place"

### Test 2 : Simulateur
```bash
python test_rfid_simulator.py
```
L'application devrait se lancer

### Test 3 : Application réelle
```bash
python main.py
```
L'application devrait démarrer

---

## 🚀 Scripts Utiles

Pour éviter les problèmes futurs, utilisez ces scripts :

| Script | Usage |
|--------|-------|
| `install_dependencies.bat` | Installation auto (Windows) |
| `start.bat` | Vérifie et installe avant de lancer |
| `diagnostic.py` | Vérifie l'installation complète |

---

## 💡 Conseils pour Éviter les Problèmes

1. ✅ **Toujours cocher "Add Python to PATH"** lors de l'installation de Python
2. ✅ **Redémarrer** l'invite de commandes après installation de Python
3. ✅ **Utiliser `python -m pip`** au lieu de `pip` directement
4. ✅ **Installer en tant qu'administrateur** si nécessaire
5. ✅ **Vérifier la connexion Internet** pendant l'installation

---

**Besoin d'aide ? Consultez aussi :**
- [PREMIERE_INSTALLATION.md](PREMIERE_INSTALLATION.md)
- [INSTALLATION_WINDOWS.md](INSTALLATION_WINDOWS.md)
- [MANUEL_UTILISATION.md - Dépannage](MANUEL_UTILISATION.md#dépannage)



