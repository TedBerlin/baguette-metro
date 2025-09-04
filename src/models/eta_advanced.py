#!/usr/bin/env python3
"""
Système ETA avancé avec ML et optimisation boulangerie
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os
import logging
from typing import Dict, List, Tuple, Optional
import asyncio
import aiohttp

logger = logging.getLogger(__name__)


class AdvancedETAModel:
    """Modèle ETA avancé avec ML et données temps réel"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.geolocator = Nominatim(user_agent="baguette_metro")
        self.cache = {}
        self.model_path = "models/eta_model.joblib"
        self.scaler_path = "models/eta_scaler.joblib"
        
        # Paramètres RATP
        self.ratp_params = {
            'metro_speed_kmh': 35,  # Vitesse moyenne métro
            'walking_speed_kmh': 5,  # Vitesse marche
            'transfer_time_min': 3,  # Temps de correspondance
            'peak_hours': [(7, 9), (17, 19)],  # Heures de pointe
            'night_hours': [(23, 6)]  # Heures de nuit
        }
        
        # Lignes RATP avec caractéristiques
        self.metro_lines = {
            '1': {'speed': 35, 'frequency': 2, 'crowding': 0.8},
            '2': {'speed': 32, 'frequency': 3, 'crowding': 0.7},
            '3': {'speed': 30, 'frequency': 3, 'crowding': 0.6},
            '4': {'speed': 33, 'frequency': 2, 'crowding': 0.9},
            '5': {'speed': 31, 'frequency': 3, 'crowding': 0.7},
            '6': {'speed': 28, 'frequency': 3, 'crowding': 0.6},
            '7': {'speed': 30, 'frequency': 3, 'crowding': 0.7},
            '8': {'speed': 29, 'frequency': 4, 'crowding': 0.5},
            '9': {'speed': 30, 'frequency': 3, 'crowding': 0.6},
            '10': {'speed': 28, 'frequency': 4, 'crowding': 0.5},
            '11': {'speed': 32, 'frequency': 3, 'crowding': 0.6},
            '12': {'speed': 30, 'frequency': 3, 'crowding': 0.7},
            '13': {'speed': 31, 'frequency': 3, 'crowding': 0.7},
            '14': {'speed': 40, 'frequency': 1.5, 'crowding': 0.8}
        }
        
        self._load_or_train_model()
    
    def _load_or_train_model(self):
        """Charge ou entraîne le modèle ML"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                logger.info("Modèle ETA chargé depuis le cache")
            else:
                self._train_model()
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {e}")
            self._train_model()
    
    def _train_model(self):
        """Entraîne le modèle avec des données synthétiques"""
        logger.info("Entraînement du modèle ETA...")
        
        # Génération de données synthétiques
        np.random.seed(42)
        n_samples = 10000
        
        # Caractéristiques d'entraînement
        distances = np.random.uniform(0.5, 20, n_samples)  # km
        hours = np.random.randint(0, 24, n_samples)
        days = np.random.randint(0, 7, n_samples)
        temperatures = np.random.uniform(-5, 35, n_samples)
        is_peak = np.array([1 if 7 <= h <= 9 or 17 <= h <= 19 else 0 for h in hours])
        is_weekend = np.array([1 if d >= 5 else 0 for d in days])
        
        # Calcul des ETA réels (avec bruit)
        base_eta = distances * 3 + 5  # 3 min/km + 5 min constantes
        peak_factor = 1 + (is_peak * 0.3)  # +30% en heures de pointe
        weekend_factor = 1 + (is_weekend * 0.1)  # +10% le weekend
        weather_factor = 1 + (np.abs(temperatures - 20) * 0.01)  # Impact météo
        
        eta_real = base_eta * peak_factor * weekend_factor * weather_factor
        eta_real += np.random.normal(0, 2, n_samples)  # Bruit
        eta_real = np.maximum(5, eta_real)  # Minimum 5 min
        
        # Features pour le modèle
        X = np.column_stack([
            distances, hours, days, temperatures, is_peak, is_weekend
        ])
        
        # Entraînement
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, eta_real)
        
        # Sauvegarde
        os.makedirs("models", exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        
        logger.info("Modèle ETA entraîné et sauvegardé")
    
    def predict_eta(self, start_lat: float, start_lon: float, 
                   end_lat: float, end_lon: float,
                   departure_time: Optional[datetime] = None,
                   include_bakery: bool = False,
                   bakery_coords: Optional[Tuple[float, float]] = None) -> Dict:
        """
        Prédit l'ETA avec ML et optimisation boulangerie
        
        Args:
            start_lat, start_lon: Coordonnées de départ
            end_lat, end_lon: Coordonnées d'arrivée
            departure_time: Heure de départ (défaut: maintenant)
            include_bakery: Inclure un arrêt boulangerie
            bakery_coords: Coordonnées de la boulangerie
            
        Returns:
            Dict avec ETA et détails
        """
        if departure_time is None:
            departure_time = datetime.now()
        
        # Calcul distance totale
        start_coords = (start_lat, start_lon)
        end_coords = (end_lat, end_lon)
        total_distance = geodesic(start_coords, end_coords).km
        
        # Features pour le modèle ML
        hour = departure_time.hour
        day = departure_time.weekday()
        temperature = 20  # Température par défaut (pourrait venir d'une API météo)
        is_peak = 1 if (7 <= hour <= 9 or 17 <= hour <= 19) else 0
        is_weekend = 1 if day >= 5 else 0
        
        features = np.array([[
            total_distance, hour, day, temperature, is_peak, is_weekend
        ]])
        
        # Prédiction ML
        features_scaled = self.scaler.transform(features)
        base_eta = self.model.predict(features_scaled)[0]
        
        # Optimisation avec boulangerie
        if include_bakery and bakery_coords:
            bakery_lat, bakery_lon = bakery_coords
            
            # Distance vers la boulangerie
            dist_to_bakery = geodesic(start_coords, (bakery_lat, bakery_lon)).km
            dist_bakery_to_end = geodesic((bakery_lat, bakery_lon), end_coords).km
            
            # Calcul ETA avec boulangerie
            eta_to_bakery = self._calculate_eta_with_features(
                dist_to_bakery, hour, day, is_peak, is_weekend
            )
            eta_bakery_to_end = self._calculate_eta_with_features(
                dist_bakery_to_end, hour, day, is_peak, is_weekend
            )
            
            bakery_stop_time = 10  # 10 min d'arrêt boulangerie
            bakery_eta = eta_to_bakery + bakery_stop_time + eta_bakery_to_end
            
            # Recommandation
            time_saved = base_eta - bakery_eta
            recommendation = "Trajet avec boulangerie recommandé" if time_saved > 0 else "Trajet direct recommandé"
            
            return {
                "base_eta": round(base_eta, 1),
                "bakery_eta": round(bakery_eta, 1),
                "time_saved": round(time_saved, 1),
                "recommendation": recommendation,
                "bakery": {
                    "name": "Boulangerie Optimisée",
                    "address": f"Près de {bakery_lat:.4f}, {bakery_lon:.4f}",
                    "rating": 4.5,
                    "lat": bakery_lat,
                    "lng": bakery_lon,
                    "stop_time": bakery_stop_time
                },
                "route_details": {
                    "total_distance_km": round(total_distance, 2),
                    "dist_to_bakery_km": round(dist_to_bakery, 2),
                    "dist_bakery_to_end_km": round(dist_bakery_to_end, 2),
                    "is_peak_hour": bool(is_peak),
                    "is_weekend": bool(is_weekend)
                }
            }
        else:
            # Trajet direct
            return {
                "base_eta": round(base_eta, 1),
                "bakery_eta": None,
                "time_saved": 0,
                "recommendation": "Trajet direct",
                "route_details": {
                    "total_distance_km": round(total_distance, 2),
                    "is_peak_hour": bool(is_peak),
                    "is_weekend": bool(is_weekend)
                }
            }
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calcule la distance entre deux points géographiques
        
        Args:
            lat1, lon1: Coordonnées du point de départ
            lat2, lon2: Coordonnées du point d'arrivée
            
        Returns:
            Distance en kilomètres
        """
        return geodesic((lat1, lon1), (lat2, lon2)).kilometers
    
    def _calculate_eta_with_features(self, distance: float, hour: int, day: int, 
                                   is_peak: int, is_weekend: int) -> float:
        """Calcule ETA avec features spécifiques"""
        features = np.array([[
            distance, hour, day, 20, is_peak, is_weekend
        ]])
        features_scaled = self.scaler.transform(features)
        return self.model.predict(features_scaled)[0]
    
    def find_optimal_bakery(self, start_lat: float, start_lon: float,
                          end_lat: float, end_lon: float) -> Optional[Tuple[float, float]]:
        """Trouve la boulangerie optimale sur le trajet"""
        # Simulation de recherche de boulangerie
        # En réalité, cela utiliserait une API Google Places ou OpenStreetMap
        
        # Point intermédiaire sur le trajet
        mid_lat = (start_lat + end_lat) / 2
        mid_lon = (start_lon + end_lon) / 2
        
        # Ajout d'un décalage aléatoire pour simuler une boulangerie
        offset_lat = np.random.uniform(-0.01, 0.01)
        offset_lon = np.random.uniform(-0.01, 0.01)
        
        return (mid_lat + offset_lat, mid_lon + offset_lon)
    
    def get_route_optimization_tips(self, eta_result: Dict) -> List[str]:
        """Génère des conseils d'optimisation"""
        tips = []
        
        if eta_result["route_details"]["is_peak_hour"]:
            tips.append("🚇 Évitez les heures de pointe pour un trajet plus rapide")
        
        if eta_result["route_details"]["is_weekend"]:
            tips.append("📅 Le weekend, les transports sont moins fréquents")
        
        if eta_result["route_details"]["total_distance_km"] > 10:
            tips.append("🔄 Considérez les correspondances pour les longues distances")
        
        if eta_result.get("bakery_eta"):
            if eta_result["time_saved"] > 0:
                tips.append("🥖 L'arrêt boulangerie vous fait gagner du temps !")
            else:
                tips.append("⏱️ L'arrêt boulangerie rallonge votre trajet")
        
        return tips


# Instance globale
eta_model = AdvancedETAModel()


def calculate_eta_advanced(start_lat: float, start_lon: float,
                          end_lat: float, end_lon: float,
                          include_bakery: bool = True) -> Dict:
    """
    Fonction principale pour calculer l'ETA avancé
    """
    try:
        bakery_coords = None
        if include_bakery:
            bakery_coords = eta_model.find_optimal_bakery(start_lat, start_lon, end_lat, end_lon)
        
        result = eta_model.predict_eta(
            start_lat, start_lon, end_lat, end_lon,
            include_bakery=include_bakery,
            bakery_coords=bakery_coords
        )
        
        # Ajout des conseils d'optimisation
        result["optimization_tips"] = eta_model.get_route_optimization_tips(result)
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur lors du calcul ETA: {e}")
        return {
            "base_eta": 25,
            "bakery_eta": 28,
            "time_saved": -3,
            "recommendation": "Erreur de calcul - Trajet direct recommandé",
            "error": str(e)
        }
