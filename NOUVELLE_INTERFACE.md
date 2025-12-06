# Nouvelle Interface Moderne de Pointage

## Vue d'ensemble

L'interface a été complètement redessinée avec un design moderne et épuré, inspiré de l'application Tipee.

## Caractéristiques

### 🎨 Design Horizontal
- **Layout moderne** : Interface en deux colonnes (horloge + données employé)
- **Couleurs actuelles** : Palette professionnelle et claire
- **Animations** : Transitions fluides

### 📡 Détection Automatique
1. **Badge détecté** → Affiche immédiatement le nom de l'employé
2. **Enregistrement automatique** du pointage dans la base
3. **Chargement des données** après 3 secondes (pour éviter la surcharge)
4. **Badge retiré** → Masque les informations et revient à l'écran d'accueil

### 📊 Informations Affichées

Quand un badge est présent :

#### **Carte "Reste à faire"**
- Heures planifiées moins heures réalisées aujourd'hui
- Couleur : Bleu

#### **Carte "Temps réalisé"**
- Heures travaillées aujourd'hui (basé sur les pointages)
- Couleur : Vert

#### **Carte "Solde de travail"**
- Solde d'heures cumulé à hier
- Couleur : Violet (rouge si négatif)
- Format : +12h30 ou -2h15

#### **Carte "Solde de vacances"**
- Jours de vacances restants
- Couleur : Orange
- Format : 4.50 jours

### 🔄 Rafraîchissement Automatique
- Les données sont rafraîchies **toutes les 30 secondes** tant que le badge est présent
- Permet de voir le temps travaillé évoluer en temps réel

## API Utilisée

### Endpoint
```
GET /api_get_employee_dashboard.php
```

### Paramètres
- `id_emp` : ID de l'employé (int)
- `id_compte` : ID du compte (int, par défaut 2)
- `date` : Date au format Y-m-d (optionnel, défaut = aujourd'hui)

### Réponse (exemple)
```json
{
  "success": true,
  "data": {
    "employee": {
      "id_emp": 3050,
      "nom": "Martinelli",
      "prenom": "Antoine",
      "nom_complet": "Antoine Martinelli"
    },
    "date": "2025-12-06",
    "planning": {
      "heures_planifiees": 7.5,
      "heures_planifiees_formatted": "07:30:00"
    },
    "temps_travaille": {
      "heures_realisees": 4.25,
      "heures_realisees_formatted": "04:15:00",
      "heures_restantes": 3.25,
      "heures_restantes_formatted": "03:15:00",
      "est_present": true
    },
    "soldes": {
      "heures": {
        "valeur": 12.5,
        "formatted": "+12:30:00"
      },
      "vacances": {
        "jours": 4,
        "heures": 23.8
      }
    }
  }
}
```

## Configuration

### Fichier de configuration
L'API URL et l'ID compte sont configurables dans `src/gui/main_window.py` :

```python
# Configuration API
self.api_url = "https://prestest.ddev.site"
self.id_compte = 2  # TODO: Configurable
```

### Personnalisation des couleurs
Les couleurs sont définies dans la méthode `apply_styles()` :
- Header : `#2c3e50` (bleu foncé)
- Accent : `#3498db` (bleu)
- Succès : `#2ecc71` (vert)
- Avertissement : `#e67e22` (orange)
- Erreur : `#e74c3c` (rouge)

## Fichiers Modifiés

### Nouveaux fichiers
- `/Users/webromandie/prevenir/prestest/api_get_employee_dashboard.php` - API dashboard
- `/Users/webromandie/timbrage/src/gui/main_window_modern.py` - Nouvelle interface

### Fichiers sauvegardés
- `/Users/webromandie/timbrage/src/gui/main_window_old_backup.py` - Ancienne interface

### Fichiers remplacés
- `/Users/webromandie/timbrage/src/gui/main_window.py` - Maintenant utilise la nouvelle interface

## Lancement

```bash
cd /Users/webromandie/timbrage
./start_auto.sh
```

## Retour à l'ancienne interface

Si besoin de revenir à l'ancienne version :

```bash
cd /Users/webromandie/timbrage
cp src/gui/main_window_old_backup.py src/gui/main_window.py
```

## TODO / Améliorations futures

- [ ] Ajouter une configuration pour l'ID compte (actuellement en dur à 2)
- [ ] Implémenter la vraie détection de retrait de carte (actuellement simulé)
- [ ] Ajouter des graphiques pour visualiser le temps travaillé
- [ ] Afficher l'historique des pointages du jour
- [ ] Support du mode sombre
- [ ] Traduction multilingue (FR/DE/EN)

