#!/usr/bin/env python3
"""
Génère assets/prevenir.png à partir de assets/prevenir.svg.

À exécuter sur un PC (pas sur le Raspberry) pour créer le PNG utilisé
par l'application sur Raspberry Pi (le rendu SVG peut faire planter l'app sur RPi).

Usage (depuis la racine du projet) :
  python assets/svg_to_png.py
"""
import sys
from pathlib import Path

# Ajouter la racine du projet au path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from PyQt5.QtSvg import QSvgRenderer
    from PyQt5.QtGui import QImage, QPainter
except ImportError as e:
    print("Erreur: PyQt5 avec QtSvg requis. Installez: pip install PyQt5 PyQtSvg")
    sys.exit(1)

SVG_PATH = ROOT / "assets" / "prevenir.svg"
PNG_PATH = ROOT / "assets" / "prevenir.png"
# Hauteur d'affichage dans l'app = 42px ; on génère en 2x pour écrans haute densité
OUTPUT_HEIGHT = 84


def main():
    if not SVG_PATH.exists():
        print(f"Fichier introuvable: {SVG_PATH}")
        sys.exit(1)

    renderer = QSvgRenderer(str(SVG_PATH))
    if not renderer.isValid():
        print("Erreur: SVG invalide ou non reconnu.")
        sys.exit(1)

    default_size = renderer.defaultSize()
    if default_size.height() <= 0:
        print("Erreur: dimensions SVG invalides.")
        sys.exit(1)

    ratio = default_size.width() / default_size.height()
    width = int(OUTPUT_HEIGHT * ratio)
    image = QImage(width, OUTPUT_HEIGHT, QImage.Format_ARGB32)
    image.fill(0)

    painter = QPainter(image)
    renderer.render(painter)
    painter.end()

    if not image.save(str(PNG_PATH), "PNG"):
        print(f"Erreur: impossible d'écrire {PNG_PATH}")
        sys.exit(1)

    print(f"OK: {PNG_PATH} créé ({width}x{OUTPUT_HEIGHT} px)")
    print("Copiez ce fichier sur le Raspberry pour afficher le logo sans plantage.")


if __name__ == "__main__":
    main()
