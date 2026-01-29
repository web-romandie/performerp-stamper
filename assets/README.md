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

1. `prevenir.svg` (si disponible)
2. `prevenir.png` (si SVG absent)
3. Texte "Pointage" (si aucun logo)

## Comment ajouter le logo

1. Placez votre fichier `prevenir.svg` ou `prevenir.png` dans ce dossier
2. Installez la dépendance SVG si nécessaire : `pip install PyQtSvg`
3. Relancez l'application
4. Le logo apparaîtra automatiquement dans l'en-tête
