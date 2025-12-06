"""
Script pour créer un exécutable Windows avec PyInstaller
Utilisation: python build_windows.py
"""
import os
import sys
from pathlib import Path

def check_pyinstaller():
    """Vérifie si PyInstaller est installé"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """Installe PyInstaller"""
    print("Installation de PyInstaller...")
    os.system("pip install pyinstaller")

def build_exe():
    """Crée l'exécutable"""
    print("=" * 60)
    print("Création de l'exécutable Windows")
    print("=" * 60)
    print()
    
    # Vérifier PyInstaller
    if not check_pyinstaller():
        print("PyInstaller n'est pas installé.")
        response = input("Voulez-vous l'installer maintenant? (o/N): ")
        if response.lower() == 'o':
            install_pyinstaller()
        else:
            print("Installation annulée.")
            return False
    
    # Paramètres PyInstaller
    app_name = "PointageRFID"
    main_file = "main.py"
    
    # Créer le fichier spec
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{main_file}'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('src', 'src'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'serial',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Pas de console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{app_name}',
)
"""
    
    # Écrire le fichier spec
    spec_file = f"{app_name}.spec"
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"Fichier spec créé: {spec_file}")
    print()
    print("Compilation en cours...")
    print("Cela peut prendre plusieurs minutes...")
    print()
    
    # Compiler avec PyInstaller
    result = os.system(f"pyinstaller {spec_file} --clean")
    
    if result == 0:
        print()
        print("=" * 60)
        print("✓ Compilation réussie!")
        print("=" * 60)
        print()
        print(f"L'exécutable se trouve dans: dist/{app_name}/")
        print()
        print("Pour distribuer l'application:")
        print(f"1. Copiez le dossier dist/{app_name}/ sur le terminal Windows")
        print("2. Ajoutez les fichiers .env et config/employees.json")
        print("3. Lancez PointageRFID.exe")
        print()
        return True
    else:
        print()
        print("✗ Erreur lors de la compilation")
        print("Consultez les messages d'erreur ci-dessus")
        return False

if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)



