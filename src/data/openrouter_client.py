import os
import json
import requests
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        
        if not self.api_key:
            logger.warning("OpenRouter API key not found. Using mock data.")
            self.client = None
        else:
            self.client = self._create_client()
            logger.info("OpenRouter client initialized successfully")

    def _create_client(self):
        """Crée un client OpenRouter configuré"""
        import openai
        
        client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        return client

    def get_nearby_bakeries(self, lat: float, lng: float, radius: int = 500) -> List[Dict]:
        """
        Trouve les boulangeries à proximité en utilisant l'IA
        """
        if not self.client:
            return self._get_mock_bakeries(lat, lng)

        try:
            # Créer un prompt pour l'IA
            prompt = self._create_bakery_prompt(lat, lng, radius)
            
            # Appel à l'IA via OpenRouter
            response = self.client.chat.completions.create(
                model="anthropic/claude-3.5-sonnet",  # Modèle Claude pour de meilleurs résultats
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un assistant spécialisé dans la recherche de boulangeries et commerces alimentaires. Tu dois retourner des données réalistes et précises au format JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Faible température pour des résultats cohérents
                max_tokens=1000
            )
            
            # Parser la réponse JSON
            content = response.choices[0].message.content
            bakeries = self._parse_ai_response(content)
            
            logger.info(f"Found {len(bakeries)} bakeries near {lat},{lng} via OpenRouter")
            return bakeries

        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            return self._get_mock_bakeries(lat, lng)

    def _create_bakery_prompt(self, lat: float, lng: float, radius: int) -> str:
        """Crée un prompt pour l'IA"""
        return f"""
        Trouve 3-5 boulangeries réalistes autour des coordonnées {lat}, {lng} dans un rayon de {radius}m.
        
        Retourne UNIQUEMENT un JSON valide avec cette structure exacte :
        {{
            "bakeries": [
                {{
                    "name": "Nom de la boulangerie",
                    "address": "Adresse complète",
                    "rating": 4.5,
                    "lat": {lat + 0.001},
                    "lng": {lng + 0.001},
                    "place_id": "unique_id",
                    "open_now": true,
                    "description": "Courte description"
                }}
            ]
        }}
        
        Règles importantes :
        - Utilise des noms de boulangeries réalistes parisiens
        - Les coordonnées doivent être proches de {lat}, {lng} (±0.002)
        - Les notes entre 3.5 et 5.0
        - Adresses réalistes dans Paris
        - Retourne UNIQUEMENT le JSON, pas d'autre texte
        """

    def _parse_ai_response(self, content: str) -> List[Dict]:
        """Parse la réponse de l'IA"""
        try:
            # Nettoyer la réponse
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            # Parser le JSON
            data = json.loads(content)
            bakeries = data.get('bakeries', [])
            
            # Valider et nettoyer les données
            validated_bakeries = []
            for bakery in bakeries:
                if self._validate_bakery(bakery):
                    validated_bakeries.append(bakery)
            
            return validated_bakeries
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return self._get_mock_bakeries(48.8566, 2.3522)

    def _validate_bakery(self, bakery: Dict) -> bool:
        """Valide les données d'une boulangerie"""
        required_fields = ['name', 'address', 'rating', 'lat', 'lng']
        return all(field in bakery for field in required_fields)

    def _get_mock_bakeries(self, lat: float, lng: float) -> List[Dict]:
        """Données mock pour le développement"""
        return [
            {
                'name': 'Boulangerie Parisienne (OpenRouter)',
                'address': '123 Rue du Pain, 75001 Paris',
                'rating': 4.7,
                'lat': lat + 0.001,
                'lng': lng + 0.001,
                'place_id': 'openrouter_1',
                'open_now': True,
                'description': 'Boulangerie traditionnelle parisienne'
            },
            {
                'name': 'Fournil Moderne (OpenRouter)',
                'address': '456 Avenue de la Baguette, 75002 Paris',
                'rating': 4.3,
                'lat': lat - 0.001,
                'lng': lng - 0.001,
                'place_id': 'openrouter_2',
                'open_now': True,
                'description': 'Fournil artisanal avec viennoiseries'
            },
            {
                'name': 'Pain & Co (OpenRouter)',
                'address': '789 Boulevard du Croissant, 75003 Paris',
                'rating': 4.6,
                'lat': lat + 0.002,
                'lng': lng - 0.002,
                'place_id': 'openrouter_3',
                'open_now': False,
                'description': 'Boulangerie moderne avec spécialités'
            }
        ]

    def get_bakery_details(self, place_id: str) -> Optional[Dict]:
        """Récupère les détails complémentaires d'une boulangerie"""
        if not self.client or not place_id:
            return None

        try:
            prompt = f"""
            Donne des détails supplémentaires pour la boulangerie avec l'ID {place_id}.
            Retourne un JSON avec : horaires, spécialités, prix moyens, ambiance.
            """
            
            response = self.client.chat.completions.create(
                model="anthropic/claude-3.5-sonnet",
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en boulangeries parisiennes."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Error getting bakery details: {e}")
            return None


# Instance globale du client
openrouter_client = OpenRouterClient()

