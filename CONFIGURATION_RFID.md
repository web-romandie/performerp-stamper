# Configuration des badges RFID

## Vue d'ensemble

Cette fonctionnalité permet d'associer un badge RFID à un employé en utilisant l'application de timbrage et l'API du site web.

## Prérequis

1. **Application de timbrage** lancée avec le lecteur RFID connecté
2. **Site web** accessible (prestest.ddev.site)
3. **Connexion réseau** entre l'application et le site web

## Utilisation

### 1. Ouvrir la configuration RFID

Dans l'application de timbrage :
- Cliquez sur le bouton **"Configuration RFID"** (bouton vert)

### 2. Connexion au serveur

1. **URL de l'API** : Vérifiez ou modifiez l'URL du site web
   - Par défaut : `https://prestest.ddev.site`
   - En production : Modifier selon votre serveur

2. **ID du compte** : Entrez l'ID du compte (ex: `2`)

3. Cliquez sur **"Charger les employés"**

### 3. Sélection de l'employé

1. Dans la liste déroulante, sélectionnez l'employé à configurer
2. Les employés avec un badge déjà configuré sont marqués d'un ✓
3. Les employés sans badge sont marqués d'un ✗

### 4. Scan du badge

1. Cliquez sur **"Scannez le badge maintenant"**
2. Le bouton devient orange et affiche "⏳ En attente du scan..."
3. **Passez le badge RFID sur le lecteur**
4. Le code RFID apparaît dans le champ "Code RFID"
5. Le bouton devient vert avec "✓ Badge scanné!"

### 5. Enregistrement

1. Cliquez sur **"Enregistrer l'association"**
2. L'application envoie les données au serveur
3. Un message de confirmation s'affiche si tout s'est bien passé

### 6. Vérification

- Le statut de l'employé est mis à jour dans la liste (✗ → ✓)
- Vous pouvez vérifier sur le site web que le badge est bien enregistré

## Messages d'erreur possibles

### "Lecteur RFID: Non connecté"
- Vérifiez que le lecteur RFID est bien branché
- Redémarrez l'application

### "Impossible de se connecter à l'API"
- Vérifiez l'URL de l'API
- Vérifiez votre connexion réseau
- Vérifiez que le site web est accessible

### "Ce code RFID est déjà utilisé par..."
- Le badge est déjà associé à un autre employé
- Vérifiez quel employé utilise ce badge
- Si nécessaire, retirez d'abord l'ancien badge

### "ID de compte manquant ou invalide"
- Vérifiez que vous avez entré le bon ID de compte

## APIs créées

### 1. Liste des employés
- **Endpoint** : `/api_list_employees.php`
- **Méthode** : GET
- **Paramètres** : 
  - `id_compte` (requis) : ID du compte
- **Réponse** : Liste des employés actifs avec leur statut RFID

### 2. Enregistrement du badge
- **Endpoint** : `/api_save_rfid.php`
- **Méthode** : POST
- **Paramètres** :
  - `id_emp` (requis) : ID de l'employé
  - `id_compte` (requis) : ID du compte
  - `rfid_code` (requis) : Code du badge RFID
- **Réponse** : Confirmation d'enregistrement ou message d'erreur

## Notes techniques

- Les APIs sont accessibles sans authentification (à sécuriser en production)
- CORS est activé pour permettre les requêtes cross-origin
- Les codes RFID sont nettoyés automatiquement (espaces supprimés)
- Détection des doublons de badges dans le même compte
- Support des requêtes JSON et form-data

## Sécurité (TODO pour la production)

⚠️ En production, il faudra ajouter :
1. Authentification par token/API key
2. HTTPS obligatoire
3. Limitation du taux de requêtes (rate limiting)
4. Logs des modifications
5. Validation renforcée des données

## Dépannage

### Le badge ne se scanne pas dans l'application
1. Vérifiez le statut du lecteur (rouge = non connecté)
2. Testez le lecteur avec un simple scan de badge au démarrage
3. Consultez les logs de l'application

### L'enregistrement échoue
1. Vérifiez les messages dans la zone "Messages"
2. Vérifiez les logs du serveur web
3. Testez l'API directement avec curl ou Postman

### Le badge scanné n'est pas reconnu plus tard
1. Vérifiez que le code enregistré correspond au code scanné
2. Vérifiez la table `employe`, colonne `carte`
3. Le format du code peut varier selon le lecteur

## Support

Pour toute question ou problème :
1. Consultez les logs de l'application (`logs/pointage.log`)
2. Vérifiez les erreurs PHP sur le serveur web
3. Contactez l'administrateur système

