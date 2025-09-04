import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os

logger = logging.getLogger(__name__)


class ETAPredictor:
    """Modèle de prédiction des temps de trajet"""
    
    def __init__(self, model_type: str = "random_forest"):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        self.is_trained = False
        
    def _create_model(self):
        """Crée le modèle selon le type spécifié"""
        if self.model_type == "random_forest":
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == "gradient_boosting":
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
        else:
            raise ValueError(f"Type de modèle non supporté: {self.model_type}")
    
    def _extract_features(self, data: Dict) -> np.ndarray:
        """
        Extrait les features du dictionnaire de données
        
        Args:
            data: Dictionnaire contenant les données du trajet
            
        Returns:
            Array numpy des features
        """
        features = []
        
        # Features temporelles
        current_time = datetime.now()
        features.extend([
            current_time.hour,
            current_time.minute,
            current_time.weekday(),
            current_time.month,
            current_time.day
        ])
        
        # Features géographiques
        features.extend([
            data.get('start_lat', 0),
            data.get('start_lon', 0),
            data.get('end_lat', 0),
            data.get('end_lon', 0)
        ])
        
        # Distance calculée
        distance = self._calculate_distance(
            data.get('start_lat', 0), data.get('start_lon', 0),
            data.get('end_lat', 0), data.get('end_lon', 0)
        )
        features.append(distance)
        
        # Features météo (simulées)
        features.extend([
            data.get('temperature', 20),
            data.get('humidity', 50),
            data.get('precipitation', 0)
        ])
        
        # Features de trafic (simulées)
        features.extend([
            data.get('traffic_level', 0.5),
            data.get('is_rush_hour', 0),
            data.get('is_weekend', 0)
        ])
        
        # Features de transport
        features.extend([
            data.get('line_crowding', 0.5),
            data.get('transfer_count', 0),
            data.get('station_count', 5)
        ])
        
        return np.array(features).reshape(1, -1)
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcule la distance entre deux points géographiques (formule de Haversine)"""
        from math import radians, cos, sin, asin, sqrt
        
        # Conversion en radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Différences
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        # Formule de Haversine
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Rayon de la Terre en km
        r = 6371
        
        return c * r
    
    def _generate_training_data(self, n_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """
        Génère des données d'entraînement synthétiques
        
        Args:
            n_samples: Nombre d'échantillons à générer
            
        Returns:
            Tuple (X, y) avec les features et les targets
        """
        np.random.seed(42)
        
        X = []
        y = []
        
        # Coordonnées parisiennes approximatives
        paris_bounds = {
            'lat_min': 48.8, 'lat_max': 48.9,
            'lon_min': 2.3, 'lon_max': 2.4
        }
        
        for _ in range(n_samples):
            # Génération de features aléatoires
            start_lat = np.random.uniform(paris_bounds['lat_min'], paris_bounds['lat_max'])
            start_lon = np.random.uniform(paris_bounds['lon_min'], paris_bounds['lon_max'])
            end_lat = np.random.uniform(paris_bounds['lat_min'], paris_bounds['lat_max'])
            end_lon = np.random.uniform(paris_bounds['lon_min'], paris_bounds['lon_max'])
            
            # Distance
            distance = self._calculate_distance(start_lat, start_lon, end_lat, end_lon)
            
            # Heure de la journée (0-23)
            hour = np.random.randint(0, 24)
            
            # Jour de la semaine (0-6)
            weekday = np.random.randint(0, 7)
            
            # Niveau de trafic (0-1)
            traffic_level = np.random.beta(2, 2)
            
            # Heures de pointe
            is_rush_hour = 1 if hour in [7, 8, 9, 17, 18, 19] else 0
            
            # Weekend
            is_weekend = 1 if weekday >= 5 else 0
            
            # Météo
            temperature = np.random.normal(15, 10)
            humidity = np.random.uniform(30, 90)
            precipitation = np.random.exponential(0.1)
            
            # Transport
            line_crowding = np.random.beta(2, 2)
            transfer_count = np.random.poisson(1)
            station_count = max(1, int(distance * 2 + np.random.normal(0, 1)))
            
            # Features
            features = [
                hour, 0, weekday, 8, 15,  # Temps
                start_lat, start_lon, end_lat, end_lon,  # Géographie
                distance,  # Distance
                temperature, humidity, precipitation,  # Météo
                traffic_level, is_rush_hour, is_weekend,  # Trafic
                line_crowding, transfer_count, station_count  # Transport
            ]
            
            # Target: temps de trajet en minutes
            # Base: 2 minutes par km + variations
            base_time = distance * 2
            traffic_factor = 1 + traffic_level * 0.5
            rush_hour_factor = 1.3 if is_rush_hour else 1.0
            weekend_factor = 0.9 if is_weekend else 1.0
            weather_factor = 1 + precipitation * 0.2
            
            eta = base_time * traffic_factor * rush_hour_factor * weekend_factor * weather_factor
            eta += np.random.normal(0, 2)  # Bruit
            eta = max(1, int(eta))  # Minimum 1 minute
            
            X.append(features)
            y.append(eta)
        
        return np.array(X), np.array(y)
    
    def train(self, X: Optional[np.ndarray] = None, y: Optional[np.ndarray] = None):
        """
        Entraîne le modèle
        
        Args:
            X: Features d'entraînement (optionnel, génère des données si non fourni)
            y: Targets d'entraînement (optionnel, génère des données si non fourni)
        """
        logger.info("Début de l'entraînement du modèle ETA")
        
        # Créer le modèle
        self._create_model()
        
        # Générer des données si non fournies
        if X is None or y is None:
            logger.info("Génération de données d'entraînement synthétiques")
            X, y = self._generate_training_data(1000)
        
        # Diviser les données
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Normaliser les features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Sauvegarder les noms des features
        self.feature_names = [f"feature_{i}" for i in range(X_train.shape[1])]
        
        # Entraîner le modèle
        logger.info(f"Entraînement du modèle {self.model_type}")
        self.model.fit(X_train_scaled, y_train)
        
        # Évaluer le modèle
        y_pred = self.model.predict(X_test_scaled)
        
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        logger.info(f"Performance du modèle:")
        logger.info(f"  MAE: {mae:.2f} minutes")
        logger.info(f"  MSE: {mse:.2f}")
        logger.info(f"  R²: {r2:.3f}")
        
        # Validation croisée
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5)
        logger.info(f"  CV Score: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        self.is_trained = True
        logger.info("Entraînement terminé")
    
    def predict(self, data: Dict) -> int:
        """
        Prédit le temps de trajet
        
        Args:
            data: Dictionnaire contenant les données du trajet
            
        Returns:
            Temps de trajet prédit en minutes
        """
        if not self.is_trained:
            raise ValueError("Le modèle doit être entraîné avant de faire des prédictions")
        
        # Extraire les features
        features = self._extract_features(data)
        
        # Normaliser
        features_scaled = self.scaler.transform(features)
        
        # Prédire
        prediction = self.model.predict(features_scaled)[0]
        
        # Arrondir et s'assurer que c'est positif
        eta = max(1, int(round(prediction)))
        
        logger.info(f"Prédiction ETA: {eta} minutes")
        return eta
    
    def save_model(self, filepath: str):
        """Sauvegarde le modèle entraîné"""
        if not self.is_trained:
            raise ValueError("Le modèle doit être entraîné avant d'être sauvegardé")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_names': self.feature_names,
            'model_type': self.model_type,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Modèle sauvegardé: {filepath}")
    
    def load_model(self, filepath: str):
        """Charge un modèle entraîné"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Fichier modèle non trouvé: {filepath}")
        
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoders = model_data['label_encoders']
        self.feature_names = model_data['feature_names']
        self.model_type = model_data['model_type']
        self.is_trained = model_data['is_trained']
        
        logger.info(f"Modèle chargé: {filepath}")
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Retourne l'importance des features"""
        if not self.is_trained or not hasattr(self.model, 'feature_importances_'):
            return {}
        
        importance_dict = {}
        for i, importance in enumerate(self.model.feature_importances_):
            feature_name = self.feature_names[i] if i < len(self.feature_names) else f"feature_{i}"
            importance_dict[feature_name] = float(importance)
        
        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))


# Instance globale du prédicteur
eta_predictor = ETAPredictor()


def train_eta_model():
    """Fonction utilitaire pour entraîner le modèle"""
    logger.info("Entraînement du modèle ETA")
    eta_predictor.train()
    
    # Sauvegarder le modèle
    os.makedirs('models', exist_ok=True)
    eta_predictor.save_model('models/eta_predictor.joblib')
    
    return eta_predictor


def load_eta_model():
    """Fonction utilitaire pour charger le modèle"""
    model_path = 'models/eta_predictor.joblib'
    
    if os.path.exists(model_path):
        eta_predictor.load_model(model_path)
        return eta_predictor
    else:
        logger.warning("Modèle non trouvé, entraînement d'un nouveau modèle")
        return train_eta_model()


def predict_eta(data: Dict) -> int:
    """Fonction utilitaire pour prédire l'ETA"""
    return eta_predictor.predict(data)


