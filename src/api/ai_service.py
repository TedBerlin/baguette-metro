#!/usr/bin/env python3
"""
Service IA Mistral direct + OpenRouter fallback + Local fallback
"""

import aiohttp
import asyncio
from config import (
    MISTRAL_API_KEY, OPENROUTER_API_KEY, OPENAI_API_KEY,
    MISTRAL_MODEL, OPENROUTER_MODEL, OPENAI_MODEL,
    MISTRAL_API_URL, OPENROUTER_API_URL, OPENAI_API_URL,
    API_TIMEOUT, MAX_TOKENS, TEMPERATURE, TOP_P,
    ENABLE_MISTRAL_DIRECT, ENABLE_OPENAI_FALLBACK, ENABLE_OPENROUTER_FALLBACK, ENABLE_LOCAL_FALLBACK
)

async def call_mistral_direct(message: str, language: str) -> str:
    """Appelle directement l'API Mistral (priorité 1)"""
    if not ENABLE_MISTRAL_DIRECT:
        return ""
        
    try:
        if not MISTRAL_API_KEY:
            raise Exception("Clé API Mistral non configurée")
        
        # Construction du prompt contextuel avec instruction de langue STRICTE
        if language == "fr":
            system_prompt = f"""Tu es un assistant concierge français pour 'Baguette & Métro'.
RÈGLE ABSOLUE: Tu DOIS répondre UNIQUEMENT en français.
Si tu réponds en anglais, tu seras pénalisé.
Tu es un assistant français, tu parles français, tu penses en français.
RÉPONDS EN FRANÇAIS SEULEMENT."""
        else:
            system_prompt = f"Tu es un assistant concierge pour 'Baguette & Métro'. RÈGLE ABSOLUE: Tu DOIS répondre UNIQUEMENT en {language}. Si la langue est 'en', réponds en anglais. Si la langue est 'ja', réponds en japonais."
        
        user_prompt = f"IMPORTANT: Réponds UNIQUEMENT en {language}. Question: {message}"
        
        # Appel API Mistral direct avec system message
        async with aiohttp.ClientSession() as session:
            async with session.post(
                MISTRAL_API_URL,
                headers={
                    "Authorization": f"Bearer {MISTRAL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": MISTRAL_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": MAX_TOKENS,
                    "temperature": TEMPERATURE,
                    "top_p": TOP_P
                },
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)
            ) as response:
                if response.status != 200:
                    raise Exception(f"Erreur API Mistral: {response.status}")
                
                data = await response.json()
                return data["choices"][0]["message"]["content"].strip()
                
    except Exception as e:
        print(f"Erreur Mistral direct: {str(e)}")
        return ""

async def call_openai_api(message: str, language: str) -> str:
    """Appelle l'API OpenAI (priorité 2)"""
    if not ENABLE_OPENAI_FALLBACK:
        return ""
        
    try:
        if not OPENAI_API_KEY:
            raise Exception("Clé API OpenAI non configurée")
        
        # Construction du prompt contextuel avec instruction de langue STRICTE
        system_prompt = f"Tu es un assistant concierge pour 'Baguette & Métro'. RÈGLE ABSOLUE: Tu DOIS répondre UNIQUEMENT en {language}. Si la langue est 'fr', réponds en français. Si la langue est 'en', réponds en anglais. Si la langue est 'ja', réponds en japonais."
        
        user_prompt = f"IMPORTANT: Réponds UNIQUEMENT en {language}. Question: {message}"
        
        # Appel API OpenAI avec system message
        async with aiohttp.ClientSession() as session:
            async with session.post(
                OPENAI_API_URL,
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": OPENAI_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": MAX_TOKENS,
                    "temperature": TEMPERATURE,
                    "top_p": TOP_P
                },
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)
            ) as response:
                if response.status != 200:
                    raise Exception(f"Erreur API OpenAI: {response.status}")
                
                data = await response.json()
                return data["choices"][0]["message"]["content"].strip()
                
    except Exception as e:
        print(f"Erreur OpenAI: {str(e)}")
        return ""

async def call_openrouter_api(message: str, language: str) -> str:
    """Appelle l'API OpenRouter (priorité 3)"""
    if not ENABLE_OPENROUTER_FALLBACK:
        return ""
        
    try:
        if not OPENROUTER_API_KEY:
            raise Exception("Clé API OpenRouter non configurée")
        
        # Construction du prompt contextuel
        prompt = build_openrouter_prompt(message, language)
        
        # Appel API avec timeout
        async with aiohttp.ClientSession() as session:
            async with session.post(
                OPENROUTER_API_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": MAX_TOKENS,
                    "temperature": TEMPERATURE,
                    "top_p": TOP_P
                },
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)
            ) as response:
                if response.status != 200:
                    raise Exception(f"Erreur API OpenRouter: {response.status}")
                
                data = await response.json()
                return data["choices"][0]["message"]["content"].strip()
                
    except Exception as e:
        print(f"Erreur OpenRouter: {str(e)}")
        return ""

async def call_ai_with_fallback(message: str, language: str) -> tuple[str, str]:
    """Appelle l'IA avec fallback intelligent : Mistral → OpenRouter → Local"""
    try:
        # STRATÉGIE HYBRIDE INTELLIGENTE PAR LANGUE
        if language == "fr":
            # FRANÇAIS : OpenAI direct (résout le problème de langue)
            print(f"🔵 FRANÇAIS DÉTECTÉ - Utilisation d'OpenAI direct")
            print(f"🔍 DEBUG: ENABLE_OPENAI_FALLBACK = {ENABLE_OPENAI_FALLBACK}")
            print(f"🔍 DEBUG: OPENAI_API_KEY = {'CONFIGURÉ' if OPENAI_API_KEY else 'NON CONFIGURÉ'}")
            
            if ENABLE_OPENAI_FALLBACK:
                print(f"🚀 TENTATIVE OPENAI...")
                openai_response = await call_openai_api(message, language)
                print(f"🔍 DEBUG: Réponse OpenAI = '{openai_response}'")
                if openai_response and openai_response.strip():
                    print(f"✅ OPENAI RÉUSSI !")
                    return openai_response, "openai_direct"
                else:
                    print(f"❌ OPENAI ÉCHOUÉ - Fallback local")
            # Fallback local si OpenAI échoue
            if ENABLE_LOCAL_FALLBACK:
                local_response = get_intelligent_fallback(message, language)
                return local_response, "local_fallback_fr"
        elif language == "ja":
            # JAPONAIS : Mistral direct (fonctionne parfaitement)
            print(f"🟡 JAPONAIS DÉTECTÉ - Utilisation de Mistral direct")
            if ENABLE_MISTRAL_DIRECT:
                mistral_response = await call_mistral_direct(message, language)
                if mistral_response and mistral_response.strip():
                    return mistral_response, "mistral_direct"
        elif language == "en":
            # ANGLAIS : Mistral direct (fonctionne parfaitement)
            print(f"🔴 ANGLAIS DÉTECTÉ - Utilisation de Mistral direct")
            if ENABLE_MISTRAL_DIRECT:
                mistral_response = await call_mistral_direct(message, language)
                if mistral_response and mistral_response.strip():
                    return mistral_response, "mistral_direct"
        
        # 2. TENTATIVE OPENAI (fallback général pour toutes les langues)
        if ENABLE_OPENAI_FALLBACK:
            openai_response = await call_openai_api(message, language)
            if openai_response and openai_response.strip():
                return openai_response, "openai_fallback"
        
        # 3. TENTATIVE OPENROUTER (fallback général)
        if ENABLE_OPENROUTER_FALLBACK:
            openrouter_response = await call_openrouter_api(message, language)
            if openrouter_response and openrouter_response.strip():
                return openrouter_response, "openrouter"
        
        # 4. FALLBACK LOCAL (sécurité)
        if ENABLE_LOCAL_FALLBACK:
            local_response = get_intelligent_fallback(message, language)
            return local_response, "local_fallback"
        
        # Si aucun fallback n'est activé
        return "Service temporairement indisponible", "error"
        
    except Exception as e:
        print(f"Erreur dans l'appel IA: {str(e)}")
        if ENABLE_LOCAL_FALLBACK:
            local_response = get_intelligent_fallback(message, language)
            return local_response, "local_fallback"
        return "Erreur système", "error"

def build_mistral_prompt(message: str, language: str) -> str:
    """Construit un prompt intelligent pour Mistral direct"""
    base_context = {
        "fr": "Tu es un assistant concierge expert pour 'Baguette & Métro', une application qui optimise les trajets RATP avec arrêts boulangerie. Sois concis, utile et évite de répéter ce que dit l'utilisateur. IMPORTANT: Réponds UNIQUEMENT en français.",
        "en": "You are a concierge assistant for 'Baguette & Métro', an app that optimizes RATP routes with bakery stops. Be concise, helpful and avoid repeating the user's words. IMPORTANT: Respond ONLY in English.",
        "ja": "あなたは「バゲット・メトロ」のコンシェルジュアシスタントです。RATPの路線をパン屋寄り道で最適化するアプリです。簡潔で役立つ応答をし、ユーザーの言葉を繰り返さないでください。重要：日本語でのみ回答してください。"
    }
    
    context = base_context.get(language, base_context["fr"])
    
    return f"""{context}

Message de l'utilisateur: "{message}"
Instructions importantes:
- NE RÉPÈTE PAS le message de l'utilisateur
- Sois concis et utile
- RÉPONDS UNIQUEMENT DANS LA LANGUE: {language}
- Context: assistant concierge Baguette & Métro

RÉPONSE EN {language.upper()}:"""

def build_openrouter_prompt(message: str, language: str) -> str:
    """Construit un prompt intelligent pour OpenRouter"""
    base_context = {
        "fr": "Tu es un assistant concierge expert pour 'Baguette & Métro', une application qui optimise les trajets RATP avec arrêts boulangerie. Sois concis, utile et évite de répéter ce que dit l'utilisateur. IMPORTANT: Réponds UNIQUEMENT en français.",
        "en": "You are a concierge assistant for 'Baguette & Métro', an app that optimizes RATP routes with bakery stops. Be concise, helpful and avoid repeating the user's words. IMPORTANT: Respond ONLY in English.",
        "ja": "あなたは「バゲット・メトロ」のコンシェルジュアシスタントです。RATPの路線をパン屋寄り道で最適化するアプリです。簡潔で役立つ応答をし、ユーザーの言葉を繰り返さないでください。重要：日本語でのみ回答してください。"
    }
    
    context = base_context.get(language, base_context["fr"])
    
    return f"""{context}

Message de l'utilisateur: "{message}"
Instructions importantes:
- NE RÉPÈTE PAS le message de l'utilisateur
- Sois concis et utile
- RÉPONDS UNIQUEMENT DANS LA LANGUE: {language}
- Context: assistant concierge Baguette & Métro

RÉPONSE EN {language.upper()}:"""

def get_fallback_response(context: str, language: str) -> str:
    """Fallback simple pour messages vides"""
    fallbacks = {
        "fr": "Comment puis-je vous aider aujourd'hui ?",
        "en": "How can I help you today?",
        "ja": "今日はどのようなご用件ですか？"
    }
    return fallbacks.get(language, fallbacks["fr"])

def get_intelligent_fallback(message: str, language: str) -> str:
    """Fallback intelligent basé sur le contexte du message"""
    message_lower = message.lower()
    
    # Détection du contexte et réponse intelligente
    if any(word in message_lower for word in ['comment', 'how', 'どう', 'fonctionne', 'work']):
        return get_context_response("how_it_works", language)
    elif any(word in message_lower for word in ['boulangerie', 'bakery', 'パン屋', 'pain', 'croissant']):
        return get_context_response("bakery", language)
    elif any(word in message_lower for word in ['métro', 'metro', 'メトロ', 'transport', 'bus', 'ratp']):
        return get_context_response("metro", language)
    elif any(word in message_lower for word in ['paris', 'visiter', 'tourisme', 'voyage', 'visit', 'tourism', 'first time']):
        return get_context_response("paris_tourism", language)
    elif any(word in message_lower for word in ['bonjour', 'salut', 'hello', 'hi', 'こんにちは']):
        return get_context_response("greeting", language)
    else:
        return get_context_response("default", language)

def get_context_response(context: str, language: str) -> str:
    """Retourne la réponse contextuelle dans la langue appropriée"""
    responses = {
        "fr": {
            "how_it_works": "🥖 Baguette & Métro fonctionne ainsi : 1) Entrez votre départ et destination, 2) Cliquez sur 'Calculer l'itinéraire', 3) L'IA trouve le meilleur trajet avec des boulangeries sur le chemin ! 🚇",
            "bakery": "🥖 Les boulangeries parisiennes sont excellentes ! Notre app trouve automatiquement les meilleures sur votre trajet. Essayez de calculer un itinéraire pour voir ! 🗺️",
            "metro": "🚇 Le métro parisien est très pratique ! Notre app utilise l'API PRIM RATP pour des données en temps réel. Calculons ensemble votre trajet optimal ! 🚀",
            "paris_tourism": "🏛️ Paris est magnifique ! Notre app vous aide à planifier vos déplacements et découvrir les meilleures boulangeries. Voulez-vous calculer un itinéraire ? 🥖",
            "greeting": "Bonjour ! 👋 Je suis votre assistant Baguette & Métro. Je peux vous aider avec les transports parisiens et les boulangeries. Que souhaitez-vous savoir ? 🚇🥖",
            "default": "🤖 Je peux vous aider avec les transports parisiens, les boulangeries et la planification d'itinéraires. Posez-moi une question spécifique ! 🚇🥖"
        },
        "en": {
            "how_it_works": "🥖 Baguette & Métro works like this: 1) Enter your departure and destination, 2) Click 'Calculate Route', 3) AI finds the best route with bakeries along the way! 🚇",
            "bakery": "🥖 Parisian bakeries are excellent! Our app automatically finds the best ones on your route. Try calculating a route to see! 🗺️",
            "metro": "🚇 The Paris metro is very convenient! Our app uses the PRIM RATP API for real-time data. Let's calculate your optimal route together! 🚀",
            "paris_tourism": "🏛️ Paris is beautiful! Our app helps you plan your trips and discover the best bakeries. Would you like to calculate a route? 🥖",
            "greeting": "Hello! 👋 I'm your Baguette & Métro assistant. I can help you with Parisian transport and bakeries. What would you like to know? 🚇🥖",
            "default": "🤖 I can help you with Parisian transport, bakeries and route planning. Ask me a specific question! 🚇🥖"
        },
        "ja": {
            "how_it_works": "🥖 バゲット・メトロはこのように動作します：1) 出発地と目的地を入力、2) 「ルート計算」をクリック、3) AIがパン屋さん寄り道の最適ルートを見つけます！🚇",
            "bakery": "🥖 パリのパン屋さんは素晴らしいです！私たちのアプリが自動的にルート上の最高のパン屋さんを見つけます。ルートを計算してみてください！🗺️",
            "metro": "🚇 パリのメトロはとても便利です！私たちのアプリはPRIM RATP APIを使用してリアルタイムデータを取得します。一緒に最適なルートを計算しましょう！🚀",
            "paris_tourism": "🏛️ パリは美しい街です！私たちのアプリが旅行計画と最高のパン屋さん発見をお手伝いします。ルートを計算しますか？🥖",
            "greeting": "こんにちは！👋 バゲット・メトロのアシスタントです。パリの交通機関とパン屋さんについてお手伝いできます。何を知りたいですか？🚇🥖",
            "default": "🤖 パリの交通機関、パン屋さん、ルート計画についてお手伝いできます。具体的な質問をしてください！🚇🥖"
        }
    }
    
    return responses.get(language, responses["fr"]).get(context, responses["fr"]["default"])

def detect_language_from_message(message: str) -> str:
    """Détecte automatiquement la langue de la question"""
    message_lower = message.lower()
    
    # Détection anglaise
    english_words = ['what', 'how', 'where', 'when', 'why', 'first', 'time', 'paris', 'visit', 'tour', 'help', 'hello', 'hi']
    if any(word in message_lower for word in english_words):
        return "en"
    
    # Détection japonaise
    japanese_chars = ['は', 'が', 'を', 'に', 'へ', 'で', 'の', 'か', 'よ', 'ね', 'わ', 'い', 'う', 'え', 'お', 'あ']
    if any(char in message for char in japanese_chars):
        return "ja"
    
    # Par défaut : français
    return "fr"
