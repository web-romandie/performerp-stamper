"""
Configuration API pour l'application de timbrage

IMPORTANT : 
1. Copiez ce fichier vers api_config.py
2. Configurez vos vraies valeurs
3. Ne jamais commiter api_config.py dans git !

cp config/api_config.example.py config/api_config.py
"""

# URL de base de l'API (sans slash final)
API_URL = "https://prestest.ddev.site"

# ID du compte (doit correspondre à votre compte dans la base de données)
ACCOUNT_ID = 2

# Clé API pour authentifier les requêtes
# Cette clé doit correspondre EXACTEMENT à celle définie dans 
# api_keys_config.php sur le serveur pour votre compte
# Ne jamais partager cette clé !
API_KEY = "PVN-2025-A7K9M3X8Q2W5"
