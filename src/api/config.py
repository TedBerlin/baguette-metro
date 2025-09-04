#!/usr/bin/env python3
"""
Configuration des clés API pour Baguette & Métro
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le répertoire racine
import pathlib
root_dir = pathlib.Path(__file__).parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

# Configuration des clés API (lecture directe depuis .env)
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")

# Configuration des modèles
MISTRAL_MODEL = "mistral-small-latest"  # Modèle correct pour Mistral AI
OPENROUTER_MODEL = "mistralai/mistral-7b-instruct"
OPENAI_MODEL = "gpt-4o-mini"  # Modèle OpenAI optimal pour coût/performance

# Configuration des timeouts
API_TIMEOUT = 15  # secondes
MAX_TOKENS = 200
TEMPERATURE = 0.7
TOP_P = 0.9

# URLs des APIs
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
GOOGLE_PLACES_API_URL = "https://maps.googleapis.com/maps/api/place"

# Configuration du fallback
ENABLE_MISTRAL_DIRECT = True   # Réactivé - on va résoudre le problème FR
ENABLE_OPENAI_FALLBACK = True  # OpenAI comme fallback supplémentaire
ENABLE_OPENROUTER_FALLBACK = True
ENABLE_LOCAL_FALLBACK = True

# Priorités des sources IA
IA_PRIORITIES = [
    "mistral_direct",      # Priorité 1 : Mistral direct (EN/JP)
    "openai_fallback",     # Priorité 2 : OpenAI fallback (FR/EN/JP)
    "openrouter",          # Priorité 3 : OpenRouter fallback
    "local_fallback"       # Priorité 4 : Fallback local (sécurité)
]
