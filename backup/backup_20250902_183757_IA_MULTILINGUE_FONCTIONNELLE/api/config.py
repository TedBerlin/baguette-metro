#!/usr/bin/env python3
"""
Configuration des clés API pour Baguette & Métro
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration des clés API
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "pHNgLRN6EgngKlXeq2Ml8MQj96Q6as6Z")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")

# Configuration des modèles
MISTRAL_MODEL = "mistral-small-latest"  # Modèle correct pour Mistral AI
OPENROUTER_MODEL = "mistralai/mistral-7b-instruct"

# Configuration des timeouts
API_TIMEOUT = 15  # secondes
MAX_TOKENS = 200
TEMPERATURE = 0.7
TOP_P = 0.9

# URLs des APIs
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Configuration du fallback
ENABLE_MISTRAL_DIRECT = True   # Réactivé - on va résoudre le problème FR
ENABLE_OPENROUTER_FALLBACK = True
ENABLE_LOCAL_FALLBACK = True

# Priorités des sources IA
IA_PRIORITIES = [
    "mistral_direct",      # Priorité 1 : Mistral direct
    "openrouter",          # Priorité 2 : OpenRouter fallback
    "local_fallback"       # Priorité 3 : Fallback local
]
