# Changelog - Système de Pointage RFID

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

## [1.0.0] - 2025-11-26

### Ajouté
- ✨ Interface graphique de pointage optimisée pour écran tactile
- ✨ Système de lecture RFID avec auto-détection du port
- ✨ Enregistrement local des pointages dans base SQLite
- ✨ Détection automatique ENTRÉE/SORTIE selon dernier pointage
- ✨ Export des pointages en format CSV
- ✨ Envoi automatique par FTP des fichiers CSV
- ✨ Panneau d'administration avec 3 onglets :
  - Consultation des pointages par période
  - Génération de rapports (journalier/hebdomadaire)
  - Export manuel et test FTP
- ✨ Calcul automatique des heures travaillées
- ✨ Système de logs complet
- ✨ Configuration via fichier .env
- ✨ Gestion des employés via fichier JSON
- ✨ Scripts de démarrage pour Windows et macOS/Linux
- ✨ Script de configuration initiale (setup_env.py)
- ✨ Script de compilation en exécutable Windows (build_windows.py)

### Documentation
- 📝 README.md avec vue d'ensemble du projet
- 📝 MANUEL_UTILISATION.md complet
- 📝 INSTALLATION_WINDOWS.md détaillé pour terminal tactile
- 📝 CHANGELOG.md pour suivre les versions

### Technique
- 🔧 Python 3.8+ compatible
- 🔧 PyQt5 pour l'interface graphique
- 🔧 pyserial pour la communication RFID
- 🔧 SQLite pour la base de données
- 🔧 Support multi-plateforme (Windows, macOS, Linux)
- 🔧 Architecture modulaire (database, rfid, export, gui)

### Sécurité
- 🔒 Fichier .env pour les credentials (ignoré par git)
- 🔒 Mots de passe FTP non stockés en clair dans le code
- 🔒 Base de données locale sécurisée

## Prochaines versions (roadmap)

### [1.1.0] - Prévu
- 🚀 Ajout d'un mode hors-ligne avec synchronisation
- 🚀 Support de plusieurs lecteurs RFID
- 🚀 Interface d'administration web
- 🚀 Notifications par email en cas d'anomalie
- 🚀 Export en format Excel (XLSX)
- 🚀 Gestion des absences et congés
- 🚀 Authentification administrateur

### [1.2.0] - Prévu
- 🚀 Support de lecteurs biométriques
- 🚀 Tableau de bord temps réel
- 🚀 API REST pour intégration
- 🚀 Application mobile de consultation
- 🚀 Multi-sites avec synchronisation centralisée

---

## Format du changelog

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/lang/fr/).

### Types de changements
- **Ajouté** pour les nouvelles fonctionnalités
- **Modifié** pour les changements dans les fonctionnalités existantes
- **Déprécié** pour les fonctionnalités qui seront retirées prochainement
- **Retiré** pour les fonctionnalités supprimées
- **Corrigé** pour les corrections de bugs
- **Sécurité** pour les changements liés à la sécurité




