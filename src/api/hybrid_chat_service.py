#!/usr/bin/env python3
"""
Service de chat hybride - OpenRouter direct pour MVP
Bypass LangChain pour éviter les problèmes de segmentation fault
"""

import os
import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class HybridChatService:
    """Service de chat hybride utilisant OpenRouter directement"""
    
    def __init__(self, api_key: Optional[str] = None):
        # Essayer de récupérer depuis les secrets Streamlit d'abord
        if not api_key:
            try:
                import streamlit as st
                if hasattr(st, 'secrets') and hasattr(st.secrets, 'OPENROUTER_API_KEY'):
                    api_key = st.secrets.OPENROUTER_API_KEY
            except ImportError:
                pass
        
        # Fallback vers les variables d'environnement
        if not api_key:
            api_key = os.getenv('OPENROUTER_API_KEY')
        
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "openai/gpt-4o-mini"  # Modèle rapide et efficace
        self.temperature = 0.7
        self.max_tokens = 1000
        
        # Templates de prompts multilingues
        self.prompts = self._create_multilingual_prompts()
        
        # Historique des conversations par session
        self.session_memories = {}
        
        logger.info("HybridChatService initialized successfully")
    
    def _create_multilingual_prompts(self) -> Dict[str, str]:
        """Crée les prompts multilingues pour le MVP"""
        return {
            "fr": """Tu es un assistant spécialisé dans l'optimisation de trajets à Paris avec arrêts boulangerie.

Tu peux aider avec :
- Calcul d'ETA (Estimated Time of Arrival)
- Recherche de boulangeries sur le trajet
- Optimisation de routes
- Conseils sur les transports parisiens
- Informations sur les lignes RATP

Réponds toujours en français de manière claire et utile.
Si tu ne sais pas quelque chose, dis-le honnêtement.

Question de l'utilisateur : {question}

Réponse :""",
            
            "en": """You are an assistant specialized in optimizing routes in Paris with bakery stops.

You can help with:
- ETA (Estimated Time of Arrival) calculation
- Finding bakeries along the route
- Route optimization
- Advice on Parisian transportation
- Information about RATP lines

Always respond in English in a clear and helpful manner.
If you don't know something, say so honestly.

User question: {question}

Response:""",
            
            "ja": """あなたはパリでのベーカリー立ち寄りを含むルート最適化の専門アシスタントです。

以下のことができます：
- ETA（到着予定時刻）の計算
- ルート上のベーカリー検索
- ルート最適化
- パリの交通機関に関するアドバイス
- RATP路線の情報

常に日本語で明確で役立つ方法で回答してください。
何かわからないことがあれば、正直にそう言ってください。

ユーザーの質問：{question}

回答："""
        }
    
    def detect_language(self, text: str) -> str:
        """Détecte la langue du texte pour le MVP"""
        text_lower = text.lower()
        
        # Détection japonaise (caractères hiragana/katakana)
        if any(char in text for char in ['あ', 'い', 'う', 'え', 'お', 'か', 'き', 'く', 'け', 'こ', 'さ', 'し', 'す', 'せ', 'そ', 'た', 'ち', 'つ', 'て', 'と', 'な', 'に', 'ぬ', 'ね', 'の', 'は', 'ひ', 'ふ', 'へ', 'ほ', 'ま', 'み', 'む', 'め', 'も', 'や', 'ゆ', 'よ', 'ら', 'り', 'る', 'れ', 'ろ', 'わ', 'を', 'ん', 'エッフェル', 'ルーヴル', '美術館', '行き方', '駅', 'メトロ', 'ベーカリー']):
            return "ja"
        
        # Détection française (mots-clés français) - PRIORITÉ
        french_words = ['comment', 'comment ça marche', 'comment aller', 'quelles sont', 'meilleures', 'boulangeries', 'trajet', 'optimiser', 'aller', 'prendre', 'métro', 'station', 'ligne', 'temps', 'rapide', 'vite', 'pourquoi', 'quand', 'où', 'quoi', 'qui', 'tour eiffel', 'musée', 'mon', 'ma', 'mes']
        if any(word in text_lower for word in french_words):
            return "fr"
        
        # Détection anglaise (mots-clés anglais)
        english_words = ['how', 'what', 'where', 'when', 'why', 'which', 'who', 'the', 'is', 'are', 'you', 'can', 'will', 'have', 'to', 'get', 'go', 'eiffel', 'tower', 'museum', 'louvre', 'metro', 'station', 'bakery', 'best', 'route', 'optimize', 'optimise', 'time', 'fast', 'quick']
        if any(word in text_lower for word in english_words):
            return "en"
        
        # Français par défaut
        return "fr"
    
    async def chat_completion(self, message: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Effectue une requête de chat via OpenRouter"""
        try:
            # Détection automatique de langue si non spécifiée
            if not language:
                language = self.detect_language(message)
            
            # Création du prompt
            prompt_template = self.prompts.get(language, self.prompts["fr"])
            prompt = prompt_template.format(question=message)
            
            # Préparation de la requête
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://baguette-metro.com",
                "X-Title": "Baguette Metro MVP"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant specialized in Paris route optimization with bakery stops."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            # Appel à l'API OpenRouter
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        
                        return {
                            "response": content,
                            "language": language,
                            "model": self.model,
                            "metadata": {
                                "model": self.model,
                                "language": language,
                                "timestamp": datetime.now().isoformat(),
                                "service": "hybrid_openrouter"
                            }
                        }
                    else:
                        logger.error(f"OpenRouter API error: {response.status}")
                        return self._fallback_response(message, language)
                        
        except Exception as e:
            logger.error(f"Error in chat_completion: {e}")
            return self._fallback_response(message, language)
    
    def _fallback_response(self, message: str, language: str) -> Dict[str, Any]:
        """Réponse de fallback en cas d'erreur"""
        fallback_responses = {
            "fr": {
                "comment_ca_marche": "Voici comment fonctionne Baguette & Métro : 1) Entrez votre trajet, 2) L'IA trouve les meilleures boulangeries, 3) Optimise votre route avec arrêt boulangerie !",
                "meilleures_boulangeries": "Les meilleures boulangeries parisiennes : Du Pain et des Idées (10e), Poilâne (6e), Blé Sucré (12e), Mamiche (9e), Liberté (11e).",
                "optimiser_trajet": "Pour optimiser votre trajet : 1) Privilégiez les lignes 1, 4, 14 (plus rapides), 2) Évitez les correspondances aux heures de pointe, 3) Planifiez l'arrêt boulangerie près des stations."
            },
            "en": {
                "comment_ca_marche": "Here's how Baguette & Metro works: 1) Enter your route, 2) AI finds the best bakeries, 3) Optimizes your route with bakery stop!",
                "meilleures_boulangeries": "Best Parisian bakeries: Du Pain et des Idées (10th), Poilâne (6th), Blé Sucré (12th), Mamiche (9th), Liberté (11th).",
                "optimiser_trajet": "To optimize your route: 1) Prefer lines 1, 4, 14 (faster), 2) Avoid transfers during peak hours, 3) Plan bakery stop near stations."
            },
            "ja": {
                "comment_ca_marche": "Baguette & Metroの使い方：1) ルートを入力、2) AIが最高のベーカリーを見つける、3) ベーカリー立ち寄りでルートを最適化！",
                "meilleures_boulangeries": "最高のパリのベーカリー：Du Pain et des Idées (10区), Poilâne (6区), Blé Sucré (12区), Mamiche (9区), Liberté (11区)。",
                "optimiser_trajet": "ルート最適化：1) 1、4、14番線を優先（より速い）、2) ラッシュ時の乗り換えを避ける、3) 駅近くでベーカリー立ち寄りを計画。"
            }
        }
        
        # Détection du type de question pour réponse appropriée
        message_lower = message.lower()
        if any(word in message_lower for word in ["comment", "how", "使い方", "fonctionne", "works"]):
            response_type = "comment_ca_marche"
        elif any(word in message_lower for word in ["meilleures", "best", "最高", "boulangeries", "bakeries", "ベーカリー"]):
            response_type = "meilleures_boulangeries"
        elif any(word in message_lower for word in ["optimiser", "optimize", "最適", "trajet", "route", "ルート"]):
            response_type = "optimiser_trajet"
        else:
            response_type = "comment_ca_marche"
        
        fallback = fallback_responses.get(language, fallback_responses["fr"])
        content = fallback.get(response_type, fallback["comment_ca_marche"])
        
        return {
            "response": content,
            "language": language,
            "model": "fallback",
            "metadata": {
                "model": "fallback",
                "language": language,
                "timestamp": datetime.now().isoformat(),
                "service": "hybrid_fallback"
            }
        }
    
    async def quick_response(self, response_type: str, language: str = "fr") -> Dict[str, Any]:
        """Réponses rapides pour les boutons d'action"""
        quick_responses = {
            "comment_ca_marche": {
                "fr": "Voici comment fonctionne Baguette & Métro : 1) Entrez votre trajet, 2) L'IA trouve les meilleures boulangeries, 3) Optimise votre route avec arrêt boulangerie !",
                "en": "Here's how Baguette & Metro works: 1) Enter your route, 2) AI finds the best bakeries, 3) Optimizes your route with bakery stop!",
                "ja": "Baguette & Metroの使い方：1) ルートを入力、2) AIが最高のベーカリーを見つける、3) ベーカリー立ち寄りでルートを最適化！"
            },
            "meilleures_boulangeries": {
                "fr": "Les meilleures boulangeries parisiennes : Du Pain et des Idées (10e), Poilâne (6e), Blé Sucré (12e), Mamiche (9e), Liberté (11e).",
                "en": "Best Parisian bakeries: Du Pain et des Idées (10th), Poilâne (6th), Blé Sucré (12th), Mamiche (9th), Liberté (11th).",
                "ja": "最高のパリのベーカリー：Du Pain et des Idées (10区), Poilâne (6区), Blé Sucré (12区), Mamiche (9区), Liberté (11区)。"
            },
            "optimiser_trajet": {
                "fr": "Pour optimiser votre trajet : 1) Privilégiez les lignes 1, 4, 14 (plus rapides), 2) Évitez les correspondances aux heures de pointe, 3) Planifiez l'arrêt boulangerie près des stations.",
                "en": "To optimize your route: 1) Prefer lines 1, 4, 14 (faster), 2) Avoid transfers during peak hours, 3) Plan bakery stop near stations.",
                "ja": "ルート最適化：1) 1、4、14番線を優先（より速い）、2) ラッシュ時の乗り換えを避ける、3) 駅近くでベーカリー立ち寄りを計画。"
            }
        }
        
        content = quick_responses.get(response_type, {}).get(language, quick_responses["comment_ca_marche"]["fr"])
        
        return {
            "response": content,
            "language": language,
            "model": "quick_response",
            "metadata": {
                "model": "quick_response",
                "language": language,
                "timestamp": datetime.now().isoformat(),
                "service": "hybrid_quick"
            }
        }


# Instance globale pour le MVP
hybrid_chat_service = HybridChatService()
