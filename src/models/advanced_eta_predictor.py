"""
Prédicteur ETA avancé avec modèles LSTM/Transformer
Intègre les modèles ML avancés dans le système de prédiction
"""

import os
import logging
from typing import Dict, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime

# Import du trainer avancé
from .train_eta_model import AdvancedETATrainer
from .lightweight_ml_trainer import LightweightMLTrainer

# Import du modèle basique pour fallback
from .eta_advanced import AdvancedETAModel

logger = logging.getLogger(__name__)

class AdvancedETAPredictor:
    """
    Prédicteur ETA avancé qui combine modèles ML et règles métier
    """
    
    def __init__(self, model_path: str = "models/advanced_eta_model", lightweight_path: str = "models/lightweight_eta_model"):
        """
        Initialise le prédicteur avancé
        
        Args:
            model_path: Chemin vers le modèle TensorFlow
            lightweight_path: Chemin vers le modèle scikit-learn léger
        """
        self.model_path = model_path
        self.lightweight_path = lightweight_path
        self.advanced_trainer = None
        self.lightweight_trainer = None
        self.basic_model = AdvancedETAModel()
        self.model_loaded = False
        self.lightweight_loaded = False
        
        # Tentative de chargement des modèles
        self._load_advanced_model()
        self._load_lightweight_model()
    
    def _load_advanced_model(self):
        """Charge le modèle ML avancé s'il existe"""
        try:
            model_file = f"{self.model_path}_model.h5"
            preprocessors_file = f"{self.model_path}_preprocessors.joblib"
            
            if os.path.exists(model_file) and os.path.exists(preprocessors_file):
                self.advanced_trainer = AdvancedETATrainer()
                self.advanced_trainer.load_model(self.model_path)
                self.model_loaded = True
                logger.info("✅ Modèle ML avancé chargé avec succès")
            else:
                logger.warning("⚠️ Modèle ML avancé non trouvé - Utilisation du modèle basique")
                self.model_loaded = False
                
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement du modèle avancé : {e}")
            self.model_loaded = False
    
    def _load_lightweight_model(self):
        """Charge le modèle ML léger s'il existe"""
        try:
            model_file = f"{self.lightweight_path}_model.joblib"
            preprocessors_file = f"{self.lightweight_path}_preprocessors.joblib"
            
            if os.path.exists(model_file) and os.path.exists(preprocessors_file):
                self.lightweight_trainer = LightweightMLTrainer()
                self.lightweight_trainer.load_model(self.lightweight_path)
                self.lightweight_loaded = True
                logger.info("✅ Modèle ML léger chargé avec succès")
            else:
                logger.warning("⚠️ Modèle ML léger non trouvé")
                self.lightweight_loaded = False
                
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement du modèle léger : {e}")
            self.lightweight_loaded = False
    
    def _extract_features(self, start_lat: float, start_lon: float, 
                         end_lat: float, end_lon: float) -> Dict:
        """
        Extrait les features pour la prédiction
        
        Args:
            start_lat, start_lon: Coordonnées de départ
            end_lat, end_lon: Coordonnées d'arrivée
            
        Returns:
            Dictionnaire avec les features
        """
        now = datetime.now()
        
        # Calcul de la distance
        distance_km = self.basic_model.calculate_distance(
            start_lat, start_lon, end_lat, end_lon
        )
        
        # Features temporelles
        hour = now.hour
        day_of_week = now.weekday()
        month = now.month
        is_weekend = 1 if day_of_week >= 5 else 0
        is_peak_hour = 1 if (7 <= hour <= 9) or (17 <= hour <= 19) else 0
        
        # Données météo simulées (à remplacer par API météo réelle)
        temperature = 15 + 10 * np.sin(2 * np.pi * hour / 24)  # Variation diurne
        humidity = 60 + 20 * np.sin(2 * np.pi * hour / 24)
        precipitation = 0.1 if np.random.random() < 0.1 else 0  # 10% de chance de pluie
        wind_speed = np.random.exponential(5)
        
        # Données de transport simulées
        line_id = f"line_{np.random.randint(1, 15)}"
        station_id = f"station_{np.random.randint(1, 100)}"
        direction_id = np.random.randint(0, 2)
        
        # Complexité du trajet
        stops_count = max(1, int(distance_km * 0.8))
        transfer_count = np.random.poisson(0.5)
        
        return {
            'hour': hour,
            'day_of_week': day_of_week,
            'month': month,
            'is_peak_hour': is_peak_hour,
            'is_weekend': is_weekend,
            'temperature': temperature,
            'humidity': humidity,
            'precipitation': precipitation,
            'wind_speed': wind_speed,
            'line_id': line_id,
            'station_id': station_id,
            'direction_id': direction_id,
            'distance_km': distance_km,
            'stops_count': stops_count,
            'transfer_count': transfer_count
        }
    
    def predict_eta(self, start_lat: float, start_lon: float, 
                   end_lat: float, end_lon: float) -> Dict:
        """
        Prédit l'ETA en utilisant le modèle le plus approprié
        
        Args:
            start_lat, start_lon: Coordonnées de départ
            end_lat, end_lon: Coordonnées d'arrivée
            
        Returns:
            Dictionnaire avec prédiction et métadonnées
        """
        # Extraction des features
        features = self._extract_features(start_lat, start_lon, end_lat, end_lon)
        
        # Prédiction avec le modèle le plus approprié
        if self.lightweight_loaded and self.lightweight_trainer:
            try:
                eta_minutes = self.lightweight_trainer.predict_eta(features)
                model_type = "lightweight_ml"
                confidence = 0.90
            except Exception as e:
                logger.warning(f"Erreur prédiction légère : {e} - Fallback vers modèle basique")
                basic_result = self.basic_model.predict_eta(start_lat, start_lon, end_lat, end_lon)
                eta_minutes = basic_result["base_eta"]
                model_type = "basic_fallback"
                confidence = 0.7
        elif self.model_loaded and self.advanced_trainer:
            try:
                eta_minutes = self.advanced_trainer.predict_eta(features)
                model_type = "advanced_ml"
                confidence = 0.85
            except Exception as e:
                logger.warning(f"Erreur prédiction avancée : {e} - Fallback vers modèle basique")
                basic_result = self.basic_model.predict_eta(start_lat, start_lon, end_lat, end_lon)
                eta_minutes = basic_result["base_eta"]
                model_type = "basic_fallback"
                confidence = 0.7
        else:
            # Utilisation du modèle basique
            basic_result = self.basic_model.predict_eta(start_lat, start_lon, end_lat, end_lon)
            eta_minutes = basic_result["base_eta"]
            model_type = "basic"
            confidence = 0.7
        
        # Ajout de bruit réaliste
        noise = np.random.normal(0, eta_minutes * 0.1)  # 10% de bruit
        eta_minutes = max(1, eta_minutes + noise)
        
        # Calcul de l'intervalle de confiance
        confidence_interval = eta_minutes * 0.15  # ±15%
        
        return {
            "eta_minutes": round(eta_minutes, 1),
            "eta_seconds": int(eta_minutes * 60),
            "confidence": confidence,
            "confidence_interval": round(confidence_interval, 1),
            "model_type": model_type,
            "features": features,
            "timestamp": datetime.now().isoformat()
        }
    
    def predict_with_bakery_stop(self, start_lat: float, start_lon: float,
                                end_lat: float, end_lon: float,
                                bakery_lat: float, bakery_lon: float) -> Dict:
        """
        Prédit l'ETA avec arrêt boulangerie
        
        Args:
            start_lat, start_lon: Coordonnées de départ
            end_lat, end_lon: Coordonnées d'arrivée
            bakery_lat, bakery_lon: Coordonnées de la boulangerie
            
        Returns:
            Dictionnaire avec prédictions détaillées
        """
        # ETA direct
        direct_eta = self.predict_eta(start_lat, start_lon, end_lat, end_lon)
        
        # ETA avec arrêt boulangerie
        eta_to_bakery = self.predict_eta(start_lat, start_lon, bakery_lat, bakery_lon)
        eta_from_bakery = self.predict_eta(bakery_lat, bakery_lon, end_lat, end_lon)
        
        # Temps d'arrêt à la boulangerie (2-5 minutes)
        bakery_stop_time = np.random.uniform(2, 5)
        
        # ETA total avec boulangerie
        total_eta_with_bakery = (
            eta_to_bakery["eta_minutes"] + 
            bakery_stop_time + 
            eta_from_bakery["eta_minutes"]
        )
        
        # Différence avec le trajet direct
        time_difference = total_eta_with_bakery - direct_eta["eta_minutes"]
        
        # Recommandation
        if time_difference <= 5:
            recommendation = "recommandé"
            recommendation_reason = "Arrêt boulangerie rapide"
        elif time_difference <= 10:
            recommendation = "acceptable"
            recommendation_reason = "Délai modéré pour une pause gourmande"
        else:
            recommendation = "non_recommandé"
            recommendation_reason = "Délai trop important"
        
        return {
            "direct_eta": direct_eta,
            "eta_with_bakery": {
                "eta_to_bakery": eta_to_bakery,
                "bakery_stop_time": round(bakery_stop_time, 1),
                "eta_from_bakery": eta_from_bakery,
                "total_eta": round(total_eta_with_bakery, 1)
            },
            "comparison": {
                "time_difference": round(time_difference, 1),
                "recommendation": recommendation,
                "recommendation_reason": recommendation_reason
            },
            "bakery_location": {
                "lat": bakery_lat,
                "lon": bakery_lon
            }
        }
    
    def get_model_status(self) -> Dict:
        """
        Retourne le statut du modèle
        
        Returns:
            Dictionnaire avec informations sur le modèle
        """
        return {
            "advanced_model_loaded": self.model_loaded,
            "lightweight_model_loaded": self.lightweight_loaded,
            "basic_model_available": True,
            "model_path": self.model_path,
            "lightweight_path": self.lightweight_path,
            "last_update": datetime.now().isoformat(),
            "features_count": len(self.advanced_trainer.feature_columns) if self.advanced_trainer else 0,
            "lightweight_features_count": len(self.lightweight_trainer.feature_columns) if self.lightweight_trainer else 0
        }
    
    def retrain_model(self, num_samples: int = 50000) -> Dict:
        """
        Réentraîne le modèle avec de nouvelles données
        
        Args:
            num_samples: Nombre d'échantillons pour l'entraînement
            
        Returns:
            Dictionnaire avec résultats de l'entraînement
        """
        try:
            logger.info("🔄 Début du réentraînement du modèle...")
            
            # Création du dossier models s'il n'existe pas
            os.makedirs("models", exist_ok=True)
            
            # Initialisation et entraînement
            trainer = AdvancedETATrainer(model_type="lstm")
            
            # Génération des données
            df = trainer.generate_historical_data(num_samples=num_samples)
            
            # Préparation des séquences
            X, y = trainer.prepare_sequences(df)
            
            # Split des données
            from sklearn.model_selection import train_test_split
            X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.2, random_state=42)
            
            # Entraînement
            model = trainer.train_model(X_train, y_train, X_val, y_val)
            
            if model is not None:
                # Évaluation
                metrics = trainer.evaluate_model(X_test, y_test)
                
                # Sauvegarde
                trainer.save_model(self.model_path)
                
                # Rechargement du modèle
                self._load_advanced_model()
                
                logger.info("✅ Réentraînement terminé avec succès")
                
                return {
                    "success": True,
                    "metrics": metrics,
                    "model_loaded": self.model_loaded,
                    "samples_used": num_samples
                }
            else:
                logger.warning("⚠️ Réentraînement échoué - TensorFlow non disponible")
                return {
                    "success": False,
                    "error": "TensorFlow non disponible",
                    "model_loaded": False
                }
                
        except Exception as e:
            logger.error(f"❌ Erreur lors du réentraînement : {e}")
            return {
                "success": False,
                "error": str(e),
                "model_loaded": self.model_loaded
            }


# Instance globale pour utilisation dans l'API
advanced_predictor = AdvancedETAPredictor()


def get_advanced_predictor() -> AdvancedETAPredictor:
    """
    Retourne l'instance globale du prédicteur avancé
    
    Returns:
        Instance du prédicteur avancé
    """
    return advanced_predictor
