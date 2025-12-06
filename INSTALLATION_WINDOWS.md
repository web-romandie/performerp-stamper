# Guide d'Installation Windows - Système de Pointage RFID

Ce guide vous accompagne pas à pas pour installer le système de pointage sur un terminal Windows 10/11 avec écran tactile.

---

## Configuration matérielle recommandée

Pour le terminal **QCT Windows 10 4/64GB avec lecteur RFID** :
- ✅ Windows 10 ou 11
- ✅ 4 GB RAM minimum
- ✅ Écran tactile 10"
- ✅ Lecteur RFID intégré ou USB
- ✅ Connexion Internet (pour l'envoi FTP)

---

## Étape 1 : Installation de Python

### 1.1 Télécharger Python

1. Allez sur [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Téléchargez **Python 3.11** ou supérieur (fichier Windows installer)
3. **Important** : Pendant l'installation :
   - ✅ Cochez **"Add Python to PATH"**
   - ✅ Choisissez **"Install Now"**

### 1.2 Vérifier l'installation

1. Ouvrez **l'Invite de commandes** (touche Windows + R, tapez `cmd`, Entrée)
2. Tapez :
   ```bash
   python --version
   ```
3. Vous devriez voir : `Python 3.11.x`

---

## Étape 2 : Installation du logiciel de pointage

### 2.1 Télécharger le logiciel

1. Téléchargez le dossier complet `timbrage` sur une clé USB ou depuis votre réseau
2. Copiez-le dans un emplacement permanent, par exemple :
   ```
   C:\PointageRFID\
   ```

### 2.2 Installer les dépendances

1. Ouvrez **l'Invite de commandes**
2. Naviguez vers le dossier :
   ```bash
   cd C:\PointageRFID
   ```
3. Installez les bibliothèques requises :
   ```bash
   pip install -r requirements.txt
   ```
4. Patientez pendant le téléchargement et l'installation (quelques minutes)

---

## Étape 3 : Configuration du lecteur RFID

### 3.1 Connecter le lecteur

1. **Branchez** le lecteur RFID en USB (s'il n'est pas intégré)
2. Windows devrait automatiquement installer les pilotes

### 3.2 Identifier le port COM

1. Ouvrez le **Gestionnaire de périphériques** :
   - Clic droit sur le menu Démarrer
   - Sélectionnez "Gestionnaire de périphériques"

2. Dépliez la section **"Ports (COM et LPT)"**
3. Identifiez votre lecteur RFID (ex: "USB Serial Port (COM3)")
4. **Notez le numéro du port** (ex: COM3)

### 3.3 Test du lecteur (optionnel)

Vous pouvez tester le lecteur avec un terminal série :
1. Téléchargez **PuTTY** depuis [putty.org](https://www.putty.org/)
2. Ouvrez PuTTY
3. Sélectionnez "Serial"
4. Entrez le port COM (ex: COM3)
5. Vitesse : 9600
6. Cliquez "Open"
7. Scannez une carte → le code devrait s'afficher

---

## Étape 4 : Configuration du logiciel

### 4.1 Configuration automatique

1. Double-cliquez sur `setup_env.py` (ou lancez via l'invite de commandes)
2. Suivez les instructions à l'écran :

   ```
   Hôte FTP : ftp.votreserveur.com
   Port FTP : 21
   Utilisateur FTP : votre_login
   Mot de passe FTP : ********
   Chemin distant : /pointage
   Nom de l'entreprise : Votre Entreprise
   ```

3. Un fichier `.env` sera créé avec votre configuration

### 4.2 Configuration du port RFID (si nécessaire)

Si l'auto-détection ne fonctionne pas :

1. Ouvrez le fichier `.env` avec le Bloc-notes
2. Modifiez la ligne :
   ```
   RFID_PORT=COM3
   ```
   (Remplacez COM3 par votre port)

### 4.3 Ajouter les employés

1. Ouvrez le fichier `config\employees.json` avec le Bloc-notes
2. Ajoutez vos employés au format :
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

**Astuce** : Pour obtenir le code RFID d'une carte :
1. Activez le mode DEBUG dans `.env` : `DEBUG_MODE=True`
2. Lancez l'application
3. Scannez la carte
4. Le code apparaîtra dans `logs\pointage.log`

---

## Étape 5 : Premier lancement

### 5.1 Lancement manuel

1. Double-cliquez sur `start.bat`
2. Une fenêtre de commande s'ouvre
3. L'application démarre après quelques secondes

### 5.2 Vérifications

✅ Le lecteur RFID est détecté (vérifiez les logs)  
✅ L'interface s'affiche correctement  
✅ Le scan d'un badge fonctionne  
✅ Les pointages sont enregistrés  

---

## Étape 6 : Configuration pour démarrage automatique (optionnel)

### 6.1 Créer un raccourci

1. Clic droit sur `start.bat`
2. Sélectionnez "Créer un raccourci"
3. Déplacez le raccourci vers :
   ```
   C:\Users\[VotreUtilisateur]\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
   ```
   (ou cherchez "shell:startup" dans l'explorateur)

### 6.2 Démarrage en plein écran

1. Ouvrez `.env` avec le Bloc-notes
2. Modifiez :
   ```
   FULLSCREEN=True
   ```

---

## Étape 7 : Configuration réseau et FTP

### 7.1 Tester la connexion FTP

1. Lancez l'application
2. Cliquez sur "Administration"
3. Allez dans l'onglet "Export"
4. Cliquez sur "Tester la connexion FTP"
5. Un message de succès devrait apparaître

### 7.2 En cas d'échec FTP

**Vérifiez :**
- ✅ La connexion Internet fonctionne
- ✅ Les identifiants FTP sont corrects
- ✅ Le pare-feu Windows n'empêche pas la connexion
- ✅ Testez avec FileZilla pour valider les accès

**Configurer le pare-feu (si nécessaire) :**
1. Panneau de configuration → Système et sécurité → Pare-feu Windows
2. "Autoriser une application via le pare-feu"
3. Cliquez "Modifier les paramètres"
4. Ajoutez Python (python.exe)

---

## Étape 8 : Optimisation pour terminal tactile

### 8.1 Paramètres Windows recommandés

**Désactiver la mise en veille :**
1. Paramètres → Système → Alimentation et mise en veille
2. Écran : "Jamais"
3. Mise en veille : "Jamais"

**Désactiver les mises à jour automatiques pendant les heures de travail :**
1. Paramètres → Windows Update → Options avancées
2. Configurez les heures d'activité

**Désactiver l'écran de verrouillage :**
1. Ouvrir l'Éditeur de stratégie de groupe locale (gpedit.msc)
2. Configuration ordinateur → Modèles d'administration → Panneau de configuration → Personnalisation
3. "Ne pas afficher l'écran de verrouillage" → Activé

### 8.2 Calibrage de l'écran tactile

1. Paramètres → Périphériques → Stylet et Windows Ink
2. Cliquez sur "Calibrer l'écran tactile"
3. Suivez les instructions

---

## Étape 9 : Maintenance

### 9.1 Sauvegardes automatiques

Configurez une tâche planifiée pour sauvegarder :
- `data\pointage.db`
- `config\employees.json`
- `.env`

Vers un emplacement réseau ou un disque externe.

### 9.2 Surveillance des logs

Vérifiez régulièrement `logs\pointage.log` pour détecter d'éventuels problèmes.

### 9.3 Export FTP

L'export FTP est automatique toutes les heures (configurable dans `.env`).  
Vous pouvez aussi exporter manuellement depuis le panneau d'administration.

---

## Dépannage spécifique Windows

### Erreur "Python n'est pas reconnu"

**Solution :**
1. Réinstallez Python en cochant "Add to PATH"
2. Ou ajoutez manuellement Python au PATH :
   - Panneau de configuration → Système → Paramètres système avancés
   - Variables d'environnement
   - PATH → Modifier
   - Ajouter : `C:\Users\[Utilisateur]\AppData\Local\Programs\Python\Python311`

### Erreur "Permission denied" sur COM

**Solution :**
1. Fermez tous les programmes qui utilisent le port série
2. Redémarrez l'ordinateur
3. Vérifiez les droits administrateur

### L'interface ne s'affiche pas correctement

**Solution :**
1. Mettez à jour les pilotes graphiques
2. Réglez la résolution d'écran à 1024x600 minimum
3. Réglez la mise à l'échelle à 100%

---

## Support et ressources

- **Manuel utilisateur** : `MANUEL_UTILISATION.md`
- **README général** : `README.md`
- **Logs** : `logs\pointage.log`
- **Configuration** : `.env` et `config\employees.json`

---

## Checklist finale

Avant de mettre en production :

- [ ] Python installé et dans le PATH
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Lecteur RFID connecté et détecté
- [ ] Fichier `.env` configuré
- [ ] Employés ajoutés dans `employees.json`
- [ ] Test de pointage réussi
- [ ] Connexion FTP testée et fonctionnelle
- [ ] Export CSV testé
- [ ] Démarrage automatique configuré (optionnel)
- [ ] Sauvegardes configurées
- [ ] Formation des utilisateurs effectuée

---

**Félicitations ! Votre système de pointage est prêt à l'emploi.**



