# Dossier Assets

Ce dossier contient les ressources graphiques de l'application.

## Logo de l'en-tête

**Fichiers supportés :**
- `prevenir.svg` (prioritaire, recommandé)
- `prevenir.png` (fallback)

**Spécifications SVG :**
- Format : SVG (Scalable Vector Graphics)
- Dimensions : Sera affiché à 150px × 42px (largeur max × hauteur)
- Avantage : Qualité parfaite à toutes les tailles, fichier léger

**Spécifications PNG :**
- Format : PNG avec transparence (recommandé)
- Hauteur : Sera automatiquement redimensionné à 42px de hauteur
- Largeur : Proportionnelle (pas de limite)

**Emplacement :** `/assets/prevenir.svg` ou `/assets/prevenir.png`

**Note :** Si aucun logo n'est trouvé, l'application affichera "Pointage" en texte comme fallback.

## Ordre de priorité

1. **`prevenir.svg`** — rendu une fois en pixmap (qualité vectorielle, stable sur Raspberry Pi)
2. `prevenir.png` (si le SVG est absent ou si le rendu échoue)
3. Texte "Pointage" (si aucun logo)

## Qualité et Raspberry Pi

Le logo SVG est rendu **une seule fois** au démarrage en image (sans utiliser le widget SVG en direct), ce qui conserve la qualité vectorielle tout en évitant les plantages sur Raspberry Pi. Si le rendu SVG échoue (par ex. module Qt SVG défaillant), l’application utilise automatiquement `prevenir.png` s’il est présent.

## Comment ajouter le logo

1. Placez `prevenir.svg` dans ce dossier (optionnel : `prevenir.png` en secours si le rendu SVG échoue).
2. Relancez l'application — le logo apparaîtra dans l'en-tête avec une qualité vectorielle.
