#!/usr/bin/env python3
"""
Service Mistral AI avec gestion robuste du rate limit
Niveau ENTREPRISE - Sécurité et éthique AI
"""

import os
import time
import logging
import requests
from typing import Dict, List, Optional
import json

# Configuration du logging
logger = logging.getLogger(__name__)

class MistralAIService:
    """Service Mistral AI avec gestion robuste du rate limit"""
    
    def __init__(self):
        """Initialisation du service avec gestion intelligente du rate limit"""
        
        # Chargement automatique de la configuration
        try:
            from src.api.config import MISTRAL_API_KEY as config_key
            if config_key and config_key != "":
                self.api_key = config_key
                logger.info("✅ Configuration Mistral AI chargée depuis config")
            else:
                self.api_key = os.getenv('MISTRAL_API_KEY')
                if not self.api_key:
                    logger.warning("⚠️ Clé Mistral AI non configurée (config ou env)")
                else:
                    logger.info("✅ Configuration Mistral AI chargée depuis env")
        except ImportError:
            self.api_key = os.getenv('MISTRAL_API_KEY')
            if not self.api_key:
                logger.warning("⚠️ Clé Mistral AI non configurée (env uniquement)")
            else:
                logger.info("✅ Configuration Mistral AI chargée depuis env")
        
        self.base_url = "https://api.mistral.ai/v1"
        self.model = "mistral-large-latest"  # Modèle le plus avancé
        
        # GESTION ROBUSTE DU RATE LIMIT SELON VOS RECOMMANDATIONS
        self.max_requests_per_minute = 10  # Limite conservatrice
        self.min_delay_between_requests = 0.2  # 200ms minimum entre requêtes
        self.request_timestamps = []
        self.last_request_time = 0
        self.rate_limit_reset_time = None
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        self.backoff_multiplier = 2
        self.max_backoff_time = 60  # Maximum 60 secondes
        
        if self.api_key:
            logger.info("✅ Service Mistral AI initialisé avec clé API")
            logger.info(f"🔧 Rate limit configuré: {self.max_requests_per_minute} req/min")
            logger.info(f"⏱️ Délai minimum entre requêtes: {self.min_delay_between_requests}s")
            logger.info(f"🔄 Stratégie de retry avec backoff exponentiel activée")
        else:
            logger.warning("⚠️ Service Mistral AI en mode fallback uniquement")
    
    def _check_rate_limit(self) -> bool:
        """Vérification intelligente du rate limiting avec gestion des erreurs"""
        now = time.time()
        
        # Nettoyer les anciennes requêtes
        self.request_timestamps = [ts for ts in self.request_timestamps if now - ts < 60]
        
        # Vérifier le délai minimum entre requêtes (200ms)
        if self.last_request_time > 0:
            time_since_last = now - self.last_request_time
            if time_since_last < self.min_delay_between_requests:
                sleep_time = self.min_delay_between_requests - time_since_last
                logger.info(f"⏱️ Attente de {sleep_time:.2f}s pour respecter le délai minimum")
                time.sleep(sleep_time)
                now = time.time()  # Mettre à jour le temps après l'attente
        
        # Vérifier le nombre de requêtes par minute
        if len(self.request_timestamps) >= self.max_requests_per_minute:
            logger.warning(f"🚨 Rate limit dépassé: {len(self.request_timestamps)}/{self.max_requests_per_minute} req/min")
            
            # Calculer le temps d'attente nécessaire
            oldest_request = min(self.request_timestamps)
            wait_time = 60 - (now - oldest_request)
            
            if wait_time > 0:
                logger.info(f"⏳ Attente de {wait_time:.1f}s pour réinitialiser le rate limit")
                time.sleep(wait_time)
                now = time.time()
                
                # Nettoyer à nouveau après l'attente
                self.request_timestamps = [ts for ts in self.request_timestamps if now - ts < 60]
            
            return len(self.request_timestamps) < self.max_requests_per_minute
        
        # Enregistrer le timestamp et le temps de la dernière requête
        self.request_timestamps.append(now)
        self.last_request_time = now
        return True
    
    def _handle_rate_limit_error(self, error_response: Dict) -> None:
        """Gestion intelligente des erreurs de rate limit avec backoff exponentiel"""
        if 'error' in error_response and 'type' in error_response['error']:
            error_type = error_response['error']['type']
            
            if 'rate_limit' in error_type.lower() or '429' in str(error_response):
                self.consecutive_failures += 1
                logger.warning(f"🚨 Erreur rate limit détectée (échec #{self.consecutive_failures})")
                
                # Stratégie de backoff exponentiel selon vos recommandations
                if self.consecutive_failures <= self.max_consecutive_failures:
                    backoff_time = min(self.max_backoff_time, self.backoff_multiplier ** self.consecutive_failures)
                    logger.info(f"⏳ Backoff exponentiel: attente de {backoff_time}s")
                    time.sleep(backoff_time)
                    
                    # Réinitialiser le rate limit
                    self.request_timestamps = []
                    self.rate_limit_reset_time = time.time() + 60
                else:
                    logger.error("🚨 Trop d'échecs consécutifs, passage en mode fallback")
                    self.rate_limit_reset_time = time.time() + 300  # 5 minutes
            else:
                # Réinitialiser le compteur d'échecs pour les autres erreurs
                self.consecutive_failures = 0
    
    def _can_retry_request(self) -> bool:
        """Vérifie si on peut retenter une requête après une erreur"""
        if self.consecutive_failures >= self.max_consecutive_failures:
            if self.rate_limit_reset_time and time.time() < self.rate_limit_reset_time:
                return False
            else:
                # Réinitialiser après la période de blocage
                self.consecutive_failures = 0
                self.rate_limit_reset_time = None
                return True
        return True
    
    def _call_mistral_api_with_retry(self, payload: Dict, max_retries: int = 3) -> Optional[Dict]:
        """Appel Mistral AI avec retry et gestion robuste des erreurs"""
        
        for attempt in range(max_retries):
            try:
                # Vérification du rate limit
                if not self._check_rate_limit():
                    logger.warning(f"⚠️ Rate limit dépassé, tentative {attempt + 1}/{max_retries}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Backoff exponentiel
                        continue
                    else:
                        return None
                
                # Appel à l'API Mistral
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    ai_response = data['choices'][0]['message']['content']
                    
                    # Enregistrer le succès
                    self.request_timestamps.append(time.time())
                    self.last_request_time = time.time()
                    self.consecutive_failures = 0  # Réinitialiser les échecs
                    
                    logger.info(f"✅ Appel Mistral AI réussi (tentative {attempt + 1})")
                    return {
                        "response": ai_response,
                        "model": self.model,
                        "tokens_used": data['usage']['total_tokens'] if 'usage' in data else 0,
                        "attempt": attempt + 1
                    }
                    
                elif response.status_code == 429:  # Rate limit
                    logger.warning(f"🚨 Rate limit Mistral AI (tentative {attempt + 1}/{max_retries})")
                    self._handle_rate_limit_error({"error": {"type": "rate_limit"}})
                    
                    if attempt < max_retries - 1:
                        backoff_time = min(60, 2 ** attempt)
                        logger.info(f"⏳ Attente de {backoff_time}s avant retry")
                        time.sleep(backoff_time)
                        continue
                    else:
                        return None
                        
                else:
                    logger.warning(f"⚠️ Erreur Mistral AI {response.status_code} (tentative {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Attente courte pour les autres erreurs
                        continue
                    else:
                        return None
                        
            except requests.exceptions.Timeout:
                logger.warning(f"⏰ Timeout Mistral AI (tentative {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    return None
                    
            except Exception as e:
                logger.error(f"❌ Erreur inattendue Mistral AI: {e} (tentative {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    return None
        
        return None
    
    def _get_language_context(self, language: str) -> str:
        """Retourne le contexte linguistique pour Mistral"""
        contexts = {
            'fr': "Tu es un assistant IA expert en transport public et boulangeries artisanales à Paris. Réponds en français de manière professionnelle et bienveillante.",
            'en': "You are an AI assistant expert in public transport and artisanal bakeries in Paris. Respond in English in a professional and helpful manner.",
            'ja': "あなたはパリの公共交通機関と職人パン屋の専門家であるAIアシスタントです。日本語で専門的で親切に回答してください。"
        }
        return contexts.get(language, contexts['fr'])
    
    def _get_transport_context(self, ratp_data: Dict) -> str:
        """Génère le contexte des transports pour Mistral"""
        if not ratp_data or ratp_data.get('source') == 'erreur_api_fallback':
            return "Informations de transport non disponibles actuellement."
        
        context = "Informations RATP temps réel :\n"
        
        # Statut des lignes
        lines_status = ratp_data.get('lines_status', [])
        if lines_status:
            context += "- Statut des lignes :\n"
            for line in lines_status[:5]:  # Limiter à 5 lignes
                context += f"  • {line.get('line', 'N/A')} : {line.get('status', 'N/A')}\n"
        
        # Affluence des stations
        stations_crowding = ratp_data.get('stations_crowding', [])
        if stations_crowding:
            context += "- Affluence des stations :\n"
            for station in stations_crowding[:3]:  # Limiter à 3 stations
                context += f"  • {station.get('station', 'N/A')} : {station.get('crowding', 'N/A')}\n"
        
        return context
    
    def _get_bakery_context(self, bakeries: List[Dict]) -> str:
        """Génère le contexte des boulangeries pour Mistral"""
        if not bakeries:
            return "Aucune boulangerie trouvée sur cet itinéraire."
        
        context = "Boulangeries artisanales trouvées :\n"
        for bakery in bakeries[:3]:  # Limiter à 3 boulangeries
            context += f"• {bakery.get('name', 'N/A')} "
            context += f"(Note: {bakery.get('rating', 'N/A')}/5, "
            context += f"Distance: {bakery.get('distance', 'N/A')})\n"
        
        return context
    
    def generate_travel_advice(self, 
                              origin: str, 
                              destination: str, 
                              eta: str, 
                              distance: str,
                              bakeries: List[Dict],
                              ratp_data: Dict,
                              language: str = "fr") -> Optional[Dict]:
        """
        Génère des conseils de voyage personnalisés via Mistral AI
        
        Args:
            origin: Adresse de départ
            destination: Adresse d'arrivée
            eta: Temps estimé du trajet
            distance: Distance du trajet
            bakeries: Liste des boulangeries trouvées
            ratp_data: Données RATP temps réel
            language: Langue de réponse (fr, en, ja)
        
        Returns:
            Dict avec les conseils IA ou None si erreur
        """
        if not self.api_key:
            logger.warning("⚠️ Clé Mistral AI non configurée")
            return None
        
        if not self._check_rate_limit():
            logger.warning("⚠️ Rate limit dépassé, utilisation du fallback")
            return None
        
        try:
            logger.info(f"🤖 Génération conseils Mistral AI: {origin} → {destination} (lang: {language})")
            
            # Construction du prompt contextuel
            system_prompt = self._get_language_context(language)
            system_prompt += "\n\nTu dois fournir des conseils utiles et personnalisés pour ce trajet."
            
            # Contexte du trajet
            route_context = f"""
Trajet : {origin} → {destination}
Durée estimée : {eta}
Distance : {distance}

{self._get_transport_context(ratp_data)}

{self._get_bakery_context(bakeries)}
"""
            
            # Prompt utilisateur
            user_prompt = f"""
Basé sur ces informations, donne-moi des conseils pratiques pour ce trajet :

1. Conseils de transport (horaires, alternatives, conseils d'affluence)
2. Recommandations pour les boulangeries (meilleur moment, spécialités)
3. Conseils généraux pour optimiser ce trajet
4. Informations utiles sur l'itinéraire

Réponds de manière structurée et pratique.
"""
            
            # Préparation de la requête Mistral
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": route_context + user_prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.7,
                "top_p": 0.9,
                "stream": False
            }
            
            # Utilisation de la nouvelle méthode de retry
            result = self._call_mistral_api_with_retry(payload)
            
            if result:
                ai_response = result["response"]
                model = result["model"]
                tokens_used = result["tokens_used"]
                
                logger.info("✅ Conseils Mistral AI générés avec succès")
                
                return {
                    "ai_advice": ai_response,
                    "model": model,
                    "language": language,
                    "timestamp": time.time(),
                    "source": "mistral_ai_api",
                    "tokens_used": tokens_used,
                    "attempt": result["attempt"]
                }
                
            else:
                logger.warning("⚠️ Erreur lors de l'appel Mistral AI avec retry")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout Mistral AI API")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur requête Mistral AI: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur inattendue Mistral AI: {e}")
            return None
    
    def get_fallback_advice(self, 
                           origin: str, 
                           destination: str, 
                           eta: str, 
                           distance: str,
                           language: str = "fr") -> Dict:
        """Conseils de fallback intelligents quand Mistral n'est pas disponible"""
        logger.info(f"🔄 Utilisation du fallback pour: {origin} → {destination}")
        
        if language == 'en':
            advice = f"""
Travel Advice for {origin} → {destination}:

🚇 Transport Tips:
• Estimated time: {eta}
• Distance: {distance}
• Consider taking the metro during off-peak hours
• Check RATP app for real-time updates

🥖 Bakery Recommendations:
• Visit bakeries early morning for fresh bread
• Look for "artisan" bakeries for authentic French bread
• Try traditional baguettes and croissants

💡 General Tips:
• Plan your route in advance
• Have a backup transport option
• Enjoy the journey and discover new bakeries!
"""
        elif language == 'ja':
            advice = f"""
{origin} → {destination} への旅行アドバイス:

🚇 交通のヒント:
• 予想時間: {eta}
• 距離: {distance}
• ラッシュアワーを避けてメトロを利用
• RATPアプリでリアルタイム情報を確認

🥖 ベーカリーの推奨:
• 朝早くに訪れて新鮮なパンを購入
• 本格的なフランスパンのために「職人」ベーカリーを探す
• 伝統的なバゲットとクロワッサンを試す

💡 一般的なヒント:
• 事前にルートを計画
• バックアップの交通手段を用意
• 旅を楽しみ、新しいベーカリーを発見！
"""
        else:  # Français par défaut
            advice = f"""
Conseils de voyage pour {origin} → {destination}:

🚇 Conseils de transport:
• Temps estimé : {eta}
• Distance : {distance}
• Privilégiez le métro en heures creuses
• Consultez l'app RATP pour les mises à jour temps réel

🥖 Recommandations boulangeries:
• Visitez les boulangeries tôt le matin pour du pain frais
• Recherchez les boulangeries "artisanales" pour du vrai pain français
• Testez les baguettes et croissants traditionnels

💡 Conseils généraux:
• Planifiez votre itinéraire à l'avance
• Ayez une option de transport de secours
• Profitez du trajet et découvrez de nouvelles boulangeries !
"""
        
        return {
            "ai_advice": advice,
            "model": "fallback_intelligent",
            "language": language,
            "timestamp": time.time(),
            "source": "fallback_intelligent"
        }
    
    def generate_simple_chat_response(self, message: str, language: str = "fr") -> Optional[str]:
        """Génère une réponse simple de chat via Mistral AI avec gestion robuste du rate limit"""
        try:
            # Vérification de la configuration
            if not self.api_key:
                logger.warning("⚠️ Clé Mistral AI non configurée")
                return None

            # Construction du prompt contextuel pour le chat simple
            system_prompt = self._get_language_context(language)
            system_prompt += "\n\nTu es un assistant conciergerie expert en transport public et boulangeries artisanales à Paris. "
            system_prompt += "Réponds de manière utile, bienveillante et pratique. "
            system_prompt += "Donne des réponses détaillées et contextuelles, pas juste des phrases courtes."

            # Prompt utilisateur enrichi
            user_prompt = f"""Question de l'utilisateur: {message}

Instructions:
1. Réponds dans la langue de la question
2. Donne des conseils pratiques et détaillés
3. Mentionne les options de transport (RER B, Métro, Bus)
4. Suggère des boulangeries artisanales si pertinent
5. Sois utile et informatif, pas générique

Réponds de manière pratique et informative avec des détails concrets."""

            # Préparation de la requête Mistral
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.7,
                "top_p": 0.9,
                "stream": False
            }

            # Utilisation de la nouvelle méthode de retry robuste
            result = self._call_mistral_api_with_retry(payload)
            
            if result:
                ai_response = result["response"]
                logger.info(f"✅ Réponse Mistral AI générée avec succès (tentative {result['attempt']})")
                return ai_response
            else:
                logger.warning("⚠️ Échec de l'appel Mistral AI après tous les retry")
                return None

        except Exception as e:
            logger.error(f"❌ Erreur inattendue dans generate_simple_chat_response: {e}")
            return None

# Instance globale du service
mistral_ai_service = MistralAIService()
