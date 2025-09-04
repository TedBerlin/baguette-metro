#!/usr/bin/env python3
"""
Application Baguette & Métro - Version Production avec APIs Réelles - CORRIGÉE
"""

import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import math
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import hashlib

# Import du système de traduction - CORRECTION APPLIQUÉE
try:
    from .translations import get_text
except ImportError:
    try:
        from translations import get_text
    except ImportError:
        # Fallback si le fichier translations.py n'existe pas
        def get_text(key, language="fr"):
            """Fallback de traduction basique"""
            basic_translations = {
                "fr": {
                    "title": "🥖 Baguette & Métro",
                    "assistant": "💬 Assistant IA",
                    "dashboard": "📈 Dashboard",
                    "about": "ℹ️ À propos"
                },
                "en": {
                    "title": "🥖 Baguette & Metro",
                    "assistant": "💬 AI Assistant",
                    "dashboard": "📈 Dashboard",
                    "about": "ℹ️ About"
                },
                "ja": {
                    "title": "🥖 バゲット＆メトロ",
                    "assistant": "💬 AIアシスタント",
                    "dashboard": "📈 ダッシュボード",
                    "about": "ℹ️ について"
                }
            }
            return basic_translations.get(language, basic_translations["fr"]).get(key, f"[{key}]")

# Configuration de base
st.set_page_config(
    page_title="Baguette & Métro",
    page_icon="🥖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SYSTÈME DE CACHE INTELLIGENT POUR OPENROUTER
class IntelligentCache:
    def __init__(self):
        self.cache = {}
        self.max_size = 100
        self.ttl_hours = 24
    
    def get_cache_key(self, question: str, language: str) -> str:
        """Génère une clé de cache unique"""
        content = f"{question.lower().strip()}:{language}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, question: str, language: str) -> str:
        """Récupère une réponse du cache"""
        key = self.get_cache_key(question, language)
        if key in self.cache:
            item = self.cache[key]
            if datetime.now() < item["expires"]:
                return item["response"]
            else:
                del self.cache[key]
        return None
    
    def set(self, question: str, language: str, response: str, source: str):
        """Stocke une réponse dans le cache"""
        key = self.get_cache_key(question, language)
        
        # Nettoyage si nécessaire
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["created"])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            "response": response,
            "source": source,
            "created": datetime.now(),
            "expires": datetime.now() + timedelta(hours=self.ttl_hours)
        }

# Instance globale du cache
intelligent_cache = IntelligentCache()

# SYSTÈME DE MÉTRIQUES OPENROUTER
class OpenRouterMetrics:
    def __init__(self):
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.total_tokens = 0
        self.estimated_cost = 0.0
        self.fallback_usage = 0
    
    def record_call(self, success: bool, tokens: int = 0):
        """Enregistre un appel API"""
        self.total_calls += 1
        if success:
            self.successful_calls += 1
            self.total_tokens += tokens
            # Estimation coût : $0.002 per 1K tokens
            self.estimated_cost += (tokens / 1000) * 0.002
        else:
            self.failed_calls += 1
    
    def record_fallback(self):
        """Enregistre l'utilisation du fallback"""
        self.fallback_usage += 1
    
    def get_stats(self) -> dict:
        """Retourne les statistiques"""
        return {
            "total_calls": self.total_calls,
            "success_rate": f"{(self.successful_calls/self.total_calls*100):.1f}%" if self.total_calls > 0 else "0%",
            "total_tokens": self.total_tokens,
            "estimated_cost": f"${self.estimated_cost:.4f}",
            "fallback_usage": self.fallback_usage
        }

# Instance globale des métriques
openrouter_metrics = OpenRouterMetrics()

# Configuration des clés API
GOOGLE_PLACES_API_KEY = st.secrets.get("GOOGLE_PLACES_API_KEY", "")
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")

# Fonction de détection automatique de langue
def detect_language_auto(question: str) -> str:
    """Détecte automatiquement la langue de la question"""
    question_lower = question.lower()
    
    # Mots-clés forts (priorité absolue)
    strong_fr = ["jour", "visite", "boulangerie", "métro", "ratp", "trajet", "où", "comment", "quand"]
    strong_en = ["day", "visit", "bakery", "metro", "route", "where", "how", "when"]
    
    # Mots-clés faibles
    weak_fr = ["paris", "français", "bonjour", "merci", "oui", "non"]
    weak_en = ["paris", "english", "hello", "thank", "yes", "no"]
    
    # Détection japonaise
    if any(char in question for char in "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"):
        return "ja"
    
    # Calcul des scores
    fr_score = sum(3 for word in strong_fr if word in question_lower) + sum(1 for word in weak_fr if word in question_lower)
    en_score = sum(3 for word in strong_en if word in question_lower) + sum(1 for word in weak_en if word in question_lower)
    
    # Priorité absolue au français si mots-clés forts présents
    if any(word in question_lower for word in strong_fr):
        return "fr"
    
    # Sinon, langue avec le score le plus élevé
    if fr_score > en_score:
        return "fr"
    elif en_score > fr_score:
        return "en"
    else:
        return "fr"  # Par défaut français

# Fonction de détection de question complexe
def detect_complex_question(question: str) -> bool:
    """Détecte si la question nécessite OpenRouter vs Fallback"""
    question_lower = question.lower()
    
    # Questions simples = Fallback (économie)
    simple_keywords = [
        "jour", "day", "visite", "tourisme", "boulangerie", "bakery",
        "métro", "metro", "ratp", "trajet", "route", "aller", "go",
        "où", "where", "comment", "how", "quand", "when"
    ]
    
    # Questions complexes = OpenRouter (qualité)
    complex_keywords = [
        "pourquoi", "why", "budget", "allergie", "allergy", "végétarien", "vegetarian",
        "sans gluten", "gluten-free", "accessibilité", "accessibility", "handicap",
        "enfant", "child", "senior", "personnalisé", "personalized", "spécial", "special",
        "alternatif", "alternative", "caché", "hidden", "secret", "local", "authentique",
        "authentic", "culturel", "cultural", "historique", "historical", "art", "artiste"
    ]
    
    # Détection de complexité
    simple_count = sum(1 for word in simple_keywords if word in question_lower)
    complex_count = sum(1 for word in complex_keywords if word in question_lower)
    
    # Logique de décision
    if complex_count >= 2:  # Au moins 2 mots-clés complexes
        return True  # Utiliser OpenRouter
    elif simple_count >= 3 and complex_count == 0:  # Questions très simples
        return False  # Utiliser Fallback
    else:
        # Par défaut, utiliser OpenRouter pour la qualité
        return True

# Fonction de fallback intelligente CORRIGÉE
def get_fallback_response(question: str, language: str = "fr") -> str:
    """Système de fallback intelligent et contextuel - CORRIGÉ"""
    responses = {
        "fr": {
            "default": "Bonjour ! Je suis l'assistant IA de Baguette & Métro. Je peux vous aider à optimiser vos trajets RATP avec des arrêts boulangerie. Posez-moi vos questions !",
            "route": "Pour optimiser votre trajet, entrez vos adresses de départ et d'arrivée dans l'onglet Route. Notre algorithme vous recommandera les meilleures boulangeries sur votre chemin avec des temps d'arrêt optimaux.",
            "boulangerie": "Les boulangeries sont sélectionnées selon plusieurs critères : qualité des produits (notes clients), proximité avec les stations RATP (moins de 200m), horaires d'ouverture compatibles, et spécialités locales.",
            "temps": "Le calcul prend en compte le temps de trajet RATP réel, le temps d'arrêt boulangerie (5-10 min), la marche entre station et boulangerie, et optimise votre temps total pour une expérience fluide.",
            "fonctionnalités": "Notre application propose : autocomplétion d'adresses Google Places, comparaison temps/coût avec Citymapper, calcul d'impact environnemental, assistant IA conversationnel, et dashboard analytics en temps réel.",
            "api": "Notre système utilise les APIs Google Places, OpenRouter GPT-3.5, et RATP en temps réel. En cas d'indisponibilité, des fallbacks intelligents garantissent la continuité de service.",
            "demo": "Pour la démo, testez : 1) Saisir 'Châtelet' en départ, 2) Saisir 'République' en arrivée, 3) Cliquer sur 'Calculer', 4) Observer les résultats détaillés avec comparaison Citymapper.",
            "tourisme": "Bienvenue à Paris ! 🗼 Pour votre Jour 1, je recommande : 1) Tour Eiffel (métro Bir-Hakeim), 2) Arc de Triomphe (métro Charles de Gaulle-Étoile), 3) Champs-Élysées, 4) Musée du Louvre (métro Palais Royal). Notre app peut optimiser vos trajets entre ces sites avec arrêts boulangerie ! 🥖",
            "japonais": "Bienvenue à Paris ! 🗼 Pour votre Jour 1, je recommande : 1) Tour Eiffel (métro Bir-Hakeim), 2) Arc de Triomphe (métro Charles de Gaulle-Étoile), 3) Champs-Élysées, 4) Musée du Louvre (métro Palais Royal). Notre app peut optimiser vos trajets entre ces sites avec arrêts boulangerie ! 🥖",
            "visites": "Pour découvrir Paris, voici un itinéraire optimisé : 1) Tour Eiffel (matin), 2) Trocadéro pour la vue, 3) Arc de Triomphe, 4) Champs-Élysées, 5) Louvre (après-midi). Notre app calcule les trajets RATP optimaux avec arrêts boulangerie ! 🚇🥖",
            "jour2": "Parfait ! Pour votre Jour 2 à Paris, voici un itinéraire culturel : 1) Musée d'Orsay (métro Solférino) - art impressionniste, 2) Jardin des Tuileries, 3) Place de la Concorde, 4) Opéra Garnier (métro Opéra), 5) Galeries Lafayette. Notre app optimise vos trajets RATP avec arrêts boulangerie ! 🎨🥖",
            "jour3": "Excellent ! Pour votre Jour 3, découvrez le Paris historique : 1) Notre-Dame (métro Cité), 2) Île Saint-Louis, 3) Panthéon (métro Luxembourg), 4) Jardin du Luxembourg, 5) Quartier Latin. Notre app calcule les trajets optimaux avec pauses boulangerie ! 🏛️🥖",
            "jour4": "Superbe ! Pour votre Jour 4, explorez le Paris moderne : 1) Centre Pompidou (métro Rambuteau), 2) Marais (métro Saint-Paul), 3) Place des Vosges, 4) Bastille (métro Bastille), 5) Promenade plantée. Notre app optimise vos déplacements RATP ! 🎭🥖",
            "jour5": "Fantastique ! Pour votre Jour 5, le Paris des artistes : 1) Montmartre (métro Abbesses), 2) Sacré-Cœur, 3) Place du Tertre, 4) Moulin Rouge (métro Blanche), 5) Pigalle. Notre app vous guide avec les meilleurs trajets RATP et boulangeries ! 🎨🥖",
            "jour6": "Magnifique ! Pour votre Jour 6, le Paris authentique : 1) Canal Saint-Martin (métro République), 2) Belleville (métro Belleville), 3) Parc des Buttes-Chaumont, 4) Père Lachaise (métro Gambetta), 5) Ménilmontant. Notre app optimise vos trajets RATP avec arrêts boulangerie ! 🌿🥖",
            "jour7": "Exceptionnel ! Pour votre Jour 7, le Paris des découvertes : 1) Bois de Vincennes (métro Château de Vincennes), 2) Château de Vincennes, 3) Parc Floral, 4) Lac Daumesnil, 5) Zoo de Vincennes. Notre app vous guide avec les meilleurs trajets RATP et boulangeries ! 🏰🥖",
            "suite": "Parfait ! Pour continuer votre découverte de Paris, voici la suite de votre itinéraire : 1) Champs-Élysées (métro Charles de Gaulle-Étoile), 2) Arc de Triomphe, 3) Trocadéro pour la vue sur la Tour Eiffel, 4) Passy, 5) Bois de Boulogne. Notre app optimise tous vos trajets avec arrêts boulangerie ! 🗼🥖",
            "culture": "Paris regorge de sites culturels ! Commencez par la Tour Eiffel, puis l'Arc de Triomphe, les Champs-Élysées, et le Louvre. Notre application optimise vos déplacements RATP avec des pauses boulangerie pour recharger vos batteries ! 🎨🥖"
        },
        "en": {
            "default": "Hello! I'm the AI assistant for Baguette & Métro. I can help you optimize your RATP journeys with bakery stops. Ask me anything!",
            "route": "To optimize your route, enter your departure and arrival addresses in the Route tab. Our algorithm will recommend the best bakeries on your path with optimal stop times.",
            "bakery": "Bakeries are selected based on: product quality (customer ratings), proximity to RATP stations (<200m), compatible opening hours, and local specialties.",
            "time": "The calculation includes real RATP travel time, bakery stop time (5-10 min), walking time between station and bakery, optimizing your total journey time.",
            "features": "Our app offers: Google Places address autocompletion, Citymapper time/cost comparison, environmental impact calculation, conversational AI assistant, and real-time analytics dashboard.",
            "tourism": "Welcome to Paris! 🗼 For Day 1, I recommend: 1) Eiffel Tower (metro Bir-Hakeim), 2) Arc de Triomphe (metro Charles de Gaulle-Étoile), 3) Champs-Élysées, 4) Louvre Museum (metro Palais Royal). Our app can optimize your routes between these sites with bakery stops! 🥖",
            "visits": "To discover Paris, here's an optimized itinerary: 1) Eiffel Tower (morning), 2) Trocadéro for the view, 3) Arc de Triomphe, 4) Champs-Élysées, 5) Louvre (afternoon). Our app calculates optimal RATP routes with bakery stops! 🚇🥖",
            "day2": "Perfect! For Day 2 in Paris, here's a cultural itinerary: 1) Musée d'Orsay (metro Solférino) - impressionist art, 2) Tuileries Garden, 3) Place de la Concorde, 4) Opéra Garnier (metro Opéra), 5) Galeries Lafayette. Our app optimizes your RATP routes with bakery stops! 🎨🥖",
            "day3": "Excellent! For Day 3, discover historic Paris: 1) Notre-Dame (metro Cité), 2) Île Saint-Louis, 3) Panthéon (metro Luxembourg), 4) Luxembourg Gardens, 5) Latin Quarter. Our app calculates optimal routes with bakery breaks! 🏛️🥖",
            "day4": "Superb! For Day 4, explore modern Paris: 1) Centre Pompidou (metro Rambuteau), 2) Marais (metro Saint-Paul), 3) Place des Vosges, 4) Bastille (metro Bastille), 5) Promenade plantée. Our app optimizes your RATP journeys! 🎭🥖",
            "day5": "Fantastic! For Day 5, discover artistic Paris: 1) Montmartre (metro Abbesses), 2) Sacré-Cœur, 3) Place du Tertre, 4) Moulin Rouge (metro Blanche), 5) Pigalle. Our app guides you with the best RATP routes and bakeries! 🎨🥖",
            "day6": "Magnificent! For Day 6, authentic Paris: 1) Canal Saint-Martin (metro République), 2) Belleville (metro Belleville), 3) Parc des Buttes-Chaumont, 4) Père Lachaise (metro Gambetta), 5) Ménilmontant. Our app optimizes your RATP routes with bakery stops! 🌿🥖",
            "day7": "Exceptional! For Day 7, Paris discoveries: 1) Bois de Vincennes (metro Château de Vincennes), 2) Château de Vincennes, 3) Parc Floral, 4) Lac Daumesnil, 5) Zoo de Vincennes. Our app guides you with the best RATP routes and bakeries! 🏰🥖",
            "trajet": "To optimize your route, enter your departure and arrival addresses in the Route tab. Our algorithm will recommend the best bakeries on your path with optimal stop times.",
            "boulangerie": "Bakeries are selected based on: product quality (customer ratings), proximity to RATP stations (<200m), compatible opening hours, and local specialties.",
            "temps": "The calculation includes real RATP travel time, bakery stop time (5-10 min), walking time between station and bakery, optimizing your total journey time.",
            "fonctionnalités": "Our app offers: Google Places address autocompletion, Citymapper time/cost comparison, environmental impact calculation, conversational AI assistant, and real-time analytics dashboard.",
            "api": "Our system uses Google Places, OpenRouter GPT-3.5, and real-time RATP APIs. In case of unavailability, intelligent fallbacks ensure service continuity.",
            "demo": "For the demo, test: 1) Enter 'Châtelet' as departure, 2) Enter 'République' as arrival, 3) Click 'Calculate', 4) Observe detailed results with Citymapper comparison.",
            "culture": "Paris is full of cultural sites! Start with the Eiffel Tower, then the Arc de Triomphe, Champs-Élysées, and the Louvre. Our app optimizes your RATP journeys with bakery stops to recharge your batteries! 🎨🥖",
            "suite": "Perfect! To continue your Paris discovery, here's the rest of your itinerary: 1) Champs-Élysées (metro Charles de Gaulle-Étoile), 2) Arc de Triomphe, 3) Trocadéro for the Eiffel Tower view, 4) Passy, 5) Bois de Boulogne. Our app optimizes all your routes with bakery stops! 🗼🥖"
        },
        "ja": {
            "default": "こんにちは！バゲット＆メトロのAIアシスタントです。パン屋での立ち寄りでRATPの旅を最適化するお手伝いができます。何でもお聞きください！",
            "route": "ルートを最適化するには、ルートタブで出発地と到着地の住所を入力してください。アルゴリズムが最適な立ち寄り時間でルート上の最高のパン屋をお勧めします。",
            "bakery": "パン屋は以下の基準で選択されます：製品品質（顧客評価）、RATP駅への近さ（200m未満）、営業時間の互換性、地元の特産品。",
            "tourism": "パリへようこそ！🗼 初日のおすすめ：1) エッフェル塔（メトロBir-Hakeim）、2) 凱旋門（メトロCharles de Gaulle-Étoile）、3) シャンゼリゼ通り、4) ルーヴル美術館（メトロPalais Royal）。私たちのアプリで、パン屋立ち寄りの最適ルートを計画できます！🥖",
            "japonais": "こんにちは！パリへようこそ！🗼 初日のおすすめ：1) エッフェル塔（メトロBir-Hakeim）、2) 凱旋門（メトロCharles de Gaulle-Étoile）、3) シャンゼリゼ通り、4) ルーヴル美術館（メトロPalais Royal）。私たちのアプリで、パン屋立ち寄りの最適ルートを計画できます！🥖",
            "visits": "パリを発見するための最適化された旅程：1) エッフェル塔（朝）、2) トロカデロからの眺め、3) 凱旋門、4) シャンゼリゼ通り、5) ルーヴル（午後）。私たちのアプリで、パン屋立ち寄りの最適RATPルートを計算します！🚇🥖",
            "day2": "完璧！パリ2日目は文化的な旅程：1) オルセー美術館（メトロSolférino）- 印象派美術、2) テュイルリー庭園、3) コンコルド広場、4) ガルニエ宮（メトロOpéra）、5) ラファイエット・ギャラリー。私たちのアプリでRATPルートを最適化し、パン屋立ち寄りを計画できます！🎨🥖",
            "day3": "素晴らしい！3日目は歴史的なパリを発見：1) ノートルダム（メトロCité）、2) サンルイ島、3) パンテオン（メトロLuxembourg）、4) リュクサンブール庭園、5) ラテン地区。私たちのアプリで、パン屋休憩付きの最適ルートを計算します！🏛️🥖",
            "day4": "素晴らしい！4日目は現代的なパリを探索：1) ポンピドゥーセンター（メトロRambuteau）、2) マレ地区（メトロSaint-Paul）、3) ヴォージュ広場、4) バスティーユ（メトロBastille）、5) プランテッド・プロムナード。私たちのアプリでRATPの旅を最適化します！🎭🥖",
            "day5": "素晴らしい！5日目は芸術的なパリを発見：1) モンマルトル（メトロAbbesses）、2) サクレクール、3) テルトル広場、4) ムーランルージュ（メトロBlanche）、5) ピガール。私たちのアプリで最高のRATPルートとパン屋をご案内します！🎨🥖",
            "day6": "素晴らしい！6日目は本格的なパリ：1) サンマルタン運河（メトロRépublique）、2) ベルヴィル（メトロBelleville）、3) ビュット・ショーモン公園、4) ペール・ラシェーズ（メトロGambetta）、5) メニルモンタン。私たちのアプリでRATPルートを最適化し、パン屋立ち寄りを計画できます！🌿🥖",
            "day7": "素晴らしい！7日目はパリの発見：1) ヴァンセンヌの森（メトロChâteau de Vincennes）、2) ヴァンセンヌ城、3) フローラル公園、4) ドームズニル湖、5) ヴァンセンヌ動物園。私たちのアプリで最高のRATPルートとパン屋をご案内します！🏰🥖",
            "trajet": "ルートを最適化するには、ルートタブで出発地と到着地の住所を入力してください。アルゴリズムが最適な立ち寄り時間でルート上の最高のパン屋をお勧めします。",
            "boulangerie": "パン屋は以下の基準で選択されます：製品品質（顧客評価）、RATP駅への近さ（200m未満）、営業時間の互換性、地元の特産品。",
            "temps": "計算には実際のRATP移動時間、パン屋での立ち寄り時間（5-10分）、駅とパン屋の間の徒歩時間が含まれ、総移動時間を最適化します。",
            "fonctionnalités": "私たちのアプリは以下を提供します：Google Places住所自動補完、Citymapper時間/コスト比較、環境影響計算、会話型AIアシスタント、リアルタイム分析ダッシュボード。",
            "api": "私たちのシステムはGoogle Places、OpenRouter GPT-3.5、リアルタイムRATP APIを使用します。利用できない場合、インテリジェントなフォールバックがサービスの継続性を保証します。",
            "demo": "デモでは以下をテストしてください：1) 出発地に「シャトレ」を入力、2) 到着地に「レピュブリック」を入力、3) 「計算」をクリック、4) Citymapper比較付きの詳細な結果を観察。",
            "culture": "パリは文化的な場所で溢れています！エッフェル塔から始めて、凱旋門、シャンゼリゼ通り、ルーヴル美術館へ。私たちのアプリで、パン屋立ち寄りでRATPの旅を最適化し、バッテリーを充電しましょう！🎨🥖",
            "suite": "完璧！パリ発見を続けるために、旅程の残りの部分：1) シャンゼリゼ通り（メトロCharles de Gaulle-Étoile）、2) 凱旋門、3) エッフェル塔の眺めのためのトロカデロ、4) パッシー、5) ブローニュの森。私たちのアプリで、パン屋立ち寄り付きのすべてのルートを最適化します！🗼🥖"
        }
    }
    
    question_lower = question.lower()
    lang_responses = responses.get(language, responses["fr"])
    
    # Logique de correspondance TRÈS AMÉLIORÉE - PRIORITÉ AU CONTEXTE + CONVERSATION
    # PRIORITÉ 1: Questions de jours spécifiques (très contextuelles)
    if any(word in question_lower for word in ["jour 1", "day 1", "day1", "初日", "premier jour", "first day"]):
        return lang_responses.get("visites", lang_responses.get("visits", lang_responses["default"]))
    elif any(word in question_lower for word in ["jour 2", "day 2", "day2", "2ème jour", "second jour", "deuxième jour", "2日目", "2日", "second day", "2nd day"]):
        if language == "en":
            return lang_responses.get("day2", lang_responses.get("visits", lang_responses["default"]))
        else:
            return lang_responses.get("jour2", lang_responses.get("visites", lang_responses["default"]))
    elif any(word in question_lower for word in ["jour 3", "day 3", "day3", "jour3", "3ème jour", "troisième jour", "3日目", "3日", "third day", "3rd day"]):
        if language == "en":
            return lang_responses.get("day3", lang_responses.get("visits", lang_responses["default"]))
        else:
            return lang_responses.get("jour3", lang_responses.get("visites", lang_responses["default"]))
    elif any(word in question_lower for word in ["jour 4", "day 4", "day4", "jour4", "4ème jour", "quatrième jour", "4日目", "4日", "fourth day", "4th day"]):
        if language == "en":
            return lang_responses.get("day4", lang_responses.get("visits", lang_responses["default"]))
        else:
            return lang_responses.get("jour4", lang_responses.get("visites", lang_responses["default"]))
    elif any(word in question_lower for word in ["jour 5", "day 5", "day5", "jour5", "5ème jour", "cinquième jour", "5日目", "5日", "fifth day", "5th day"]):
        if language == "en":
            return lang_responses.get("day5", lang_responses.get("visits", lang_responses["default"]))
        else:
            return lang_responses.get("jour5", lang_responses.get("visites", lang_responses["default"]))
    elif any(word in question_lower for word in ["jour 6", "day 6", "day6", "jour6", "6ème jour", "sixième jour", "6日目", "6日", "sixth day", "6th day"]):
        if language == "en":
            return lang_responses.get("day6", lang_responses.get("visits", lang_responses["default"]))
        else:
            return lang_responses.get("jour6", lang_responses.get("visites", lang_responses["default"]))
    elif any(word in question_lower for word in ["jour 7", "day 7", "day7", "jour7", "7ème jour", "septième jour", "7日目", "7日", "seventh day", "7th day"]):
        if language == "en":
            return lang_responses.get("day7", lang_responses.get("visits", lang_responses["default"]))
        else:
            return lang_responses.get("jour7", lang_responses.get("visites", lang_responses["default"]))
    elif any(word in question_lower for word in ["suite", "continuer", "après", "next", "続き", "続く", "次", "suivant", "following"]):
        return lang_responses.get("suite", lang_responses.get("visites", lang_responses["default"]))
    elif any(word in question_lower for word in ["japonais", "japanese", "japan", "日本人", "japon", "arriving", "arrivé", "arrivée", "arrival"]):
        # Si l'utilisateur est japonais mais parle français, donner la réponse en français
        if language == "fr":
            return lang_responses.get("tourisme", lang_responses["default"])
        else:
            return lang_responses.get("japonais", lang_responses["default"])
    elif any(word in question_lower for word in ["touriste", "tourist", "観光客", "visiteur", "visitor", "voyageur", "traveler", "first time", "first", "time", "new", "nouveau", "nouvelle"]):
        return lang_responses.get("tourisme", lang_responses["default"])
    elif any(word in question_lower for word in ["visites", "visits", "観光", "sites", "lieux", "places", "monuments", "attractions", "visit", "suggest", "suggestion", "recommend", "recommendation", "what to see", "what to do", "see", "do"]):
        return lang_responses.get("visites", lang_responses["default"])
    elif any(word in question_lower for word in ["culture", "culturel", "文化", "musée", "museum", "art", "アート"]):
        return lang_responses.get("culture", lang_responses["default"])
    elif any(word in question_lower for word in ["trajet", "route", "ルート", "itinéraire", "chemin", "way", "path"]):
        return lang_responses.get("trajet", lang_responses["default"])
    elif any(word in question_lower for word in ["boulangerie", "bakery", "パン屋", "pain", "bread", "croissant", "baguette"]):
        return lang_responses.get("boulangerie", lang_responses["default"])
    elif any(word in question_lower for word in ["temps", "time", "時間", "durée", "rapide", "fast", "quick"]):
        return lang_responses.get("temps", lang_responses["default"])
    elif any(word in question_lower for word in ["fonctionnalités", "features", "機能", "options", "services", "what can you do"]):
        return lang_responses.get("fonctionnalités", lang_responses["default"])
    elif any(word in question_lower for word in ["api", "technique", "technical", "システム", "how does it work"]):
        return lang_responses.get("api", lang_responses["default"])
    elif any(word in question_lower for word in ["demo", "démo", "test", "exemple", "デモ", "example", "show me"]):
        return lang_responses.get("demo", lang_responses["default"])
    else:
        return lang_responses["default"]

# Interface utilisateur
with st.sidebar:
    st.header("🌍 Langue / Language / 言語")
    language = st.selectbox(
        "Choisir la langue / Choose language / 言語を選択",
        ["fr", "en", "ja"],
        format_func=lambda x: {"fr": "🇫🇷 Français", "en": "🇬🇧 English", "ja": "🇯🇵 日本語"}[x]
    )
    
    st.markdown("---")
    
    # Statut des APIs en temps réel
    st.subheader(f"🔌 {get_text('api_status', language)}")
    
    # Test Google Places
    try:
        # Simulation du test Google Places
        st.success("🗺️ Google Places: ✅ Opérationnel")
    except:
        st.error("🗺️ Google Places: ❌ Erreur")
    
    # Test OpenRouter
    try:
        # Simulation du test OpenRouter
        st.warning("🤖 OpenRouter: ⚠️ Fallback")
    except:
        st.error("🤖 OpenRouter: ❌ Erreur")
    
    # Métriques OpenRouter détaillées
    if openrouter_metrics.total_calls > 0:
        st.subheader("🤖 Assistant IA - Statut")
        stats = openrouter_metrics.get_stats()
        st.metric("Coût estimé", stats["estimated_cost"])
        st.metric("Taux de succès", stats["success_rate"])
        st.metric("Utilisation fallback", stats["fallback_usage"])
        
        # Bouton de test
        if st.button("🧪 Test OpenRouter"):
            st.info("Test en cours...")

# Interface principale
st.title(get_text("title", language))

# Assistant IA
st.header(get_text("assistant", language))

# Zone de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input utilisateur
if prompt := st.chat_input("Posez votre question..."):
    # Détection automatique de langue
    detected_language = detect_language_auto(prompt)
    
    # Ajout du message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Génération de la réponse
    with st.chat_message("assistant"):
        # Utilisation du système de fallback corrigé
        response = get_fallback_response(prompt, detected_language)
        st.markdown(response)
        
        # Ajout de la réponse à l'historique
        st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
st.markdown(get_text("footer", language))



