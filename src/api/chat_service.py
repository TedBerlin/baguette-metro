import os
import logging
from typing import Dict
import aiohttp
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger directement depuis .env
load_dotenv("../../.env")

class MultilingualChatService:
    def __init__(self):
        # Lecture directe depuis .env
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.contexts = self._initialize_contexts()
        
    def _initialize_contexts(self) -> Dict[str, Dict[str, str]]:
        """Initialise les contextes par langue et scénario"""
        return {
            "fr": {
                "default": "Tu es un assistant concierge expert pour 'Baguette & Métro', une application qui optimise les trajets RATP avec arrêts boulangerie. Sois concis, utile et évite de répéter ce que dit l'utilisateur.",
                "jour1": "Accueille l'utilisateur et présente brièvement l'application sans répéter ses mots.",
                "jour7": "Fais une démonstration concise de l'application sans paraphraser la demande."
            },
            "en": {
                "default": "You are a concierge assistant for 'Baguette & Métro', an app that optimizes RATP routes with bakery stops. Be concise, helpful and avoid repeating the user's words.",
                "jour1": "Welcome the user and briefly present the application without repeating their words.",
                "jour7": "Give a concise demonstration of the application without paraphrasing the request."
            },
            "ja": {
                "default": "あなたは「バゲット・メトロ」のコンシェルジュアシスタントです。RATPの路線をパン屋寄り道で最適化するアプリです。簡潔で役立つ応答をし、ユーザーの言葉を繰り返さないでください。",
                "jour1": "ユーザーを歓迎し、アプリを簡単に紹介してください。ユーザーの言葉を繰り返さないでください。",
                "jour7": "アプリのデモを簡潔に行ってください。リクエストを言い換えないでください。"
            }
        }

    async def get_chat_response(self, message: str, language: str = "fr", context: str = "default") -> str:
        """Génère une réponse IA intelligente sans répétition"""
        try:
            # 1. Vérification du message
            if not message or message.strip() == "":
                return self._get_fallback_response("empty", language)
            
            # 2. Construction du prompt contextuel
            prompt = self._build_intelligent_prompt(message, language, context)
            
            # 3. Appel API avec timeout
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "mistralai/mistral-7b-instruct",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 150,
                        "temperature": 0.7,
                        "top_p": 0.9
                    },
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status != 200:
                        raise Exception(f"API error: {response.status}")
                    
                    data = await response.json()
                    return data["choices"][0]["message"]["content"].strip()
                    
        except Exception as e:
            logging.error(f"Chat service error: {str(e)}")
            return self._get_fallback_response(message, language, context)

    def _build_intelligent_prompt(self, message: str, language: str, context: str) -> str:
        """Construit un prompt qui empêche la répétition"""
        base_context = self.contexts[language].get(context, self.contexts[language]["default"])
        
        return f"""{base_context}

Message de l'utilisateur: "{message}"

Instructions importantes:
- NE RÉPÈTE PAS le message de l'utilisateur
- Sois concis et utile
- Réponds dans la langue: {language}
- Context: {context}

Réponse:"""

    def _get_fallback_response(self, message: str, language: str, context: str = "default") -> str:
        """Fallback intelligent qui ne répète pas le message"""
        fallbacks = {
            "fr": {
                "empty": "Comment puis-je vous aider aujourd'hui ?",
                "default": "Je peux vous aider à optimiser vos trajets parisiens avec des arrêts boulangerie. Que souhaitez-vous savoir ?",
                "jour1": "Bienvenue dans Baguette & Métro ! Je vous aide à optimiser vos trajets RATP.",
                "jour7": "Je vous montre comment optimiser un trajet avec arrêt boulangerie !"
            },
            "en": {
                "empty": "How can I help you today?",
                "default": "I can help you optimize your Parisian routes with bakery stops. What would you like to know?",
                "jour1": "Welcome to Baguette & Métro! I help optimize RATP routes.",
                "jour7": "Let me show you how to optimize a route with a bakery stop!"
            },
            "ja": {
                "empty": "今日はどのようなご用件ですか？",
                "default": "パン屋さん寄り道でパリの移動を最適化するお手伝いができます。何を知りたいですか？",
                "jour1": "バゲット・メトロへようこそ！RATPの路線を最適化するお手伝いをします。",
                "jour7": "パン屋さん寄り道でルートを最適化する方法をご紹介します！"
            }
        }
        
        # Utiliser un fallback contextuel au lieu de répéter le message
        if message == "empty":
            return fallbacks[language]["empty"]
        
        return fallbacks[language].get(context, fallbacks[language]["default"])

    def get_service_status(self) -> Dict[str, str]:
        """Retourne le statut du service"""
        return {
            "status": "healthy" if self.api_key else "degraded",
            "api_key": "configured" if self.api_key else "missing"
        }

# Instance globale
chat_service = MultilingualChatService()

def get_chat_response(message: str, language: str = "fr", context: str = None) -> str:
    """Fonction d'interface pour obtenir une réponse de chat (synchrone pour compatibilité)"""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Si dans un contexte async, utiliser directement
            return asyncio.create_task(chat_service.get_chat_response(message, language, context or "default"))
        else:
            # Si dans un contexte synchrone, exécuter
            return loop.run_until_complete(chat_service.get_chat_response(message, language, context or "default"))
    except RuntimeError:
        # Nouveau event loop si nécessaire
        return asyncio.run(chat_service.get_chat_response(message, language, context or "default"))
