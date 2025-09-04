"""
Entraîneur ML léger pour prédiction ETA
Utilise scikit-learn pour éviter les problèmes TensorFlow
"""

import pandas as pd
import numpy as np
import joblib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# ML Libraries
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.linear_model import Ridge, Lasso

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LightweightMLTrainer:
    """Entraîneur ML léger pour prédiction ETA"""
    
    def __init__(self, model_type: str = "random_forest"):
        """
        Initialise l'entraîneur
        
        Args:
            model_type: Type de modèle ("random_forest", "gradient_boosting", "neural_network", "svr")
        """
        self.model_type = model_type
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.model = None
        self.feature_importance = None
        
        # Paramètres du modèle
        self.feature_columns = [
            'hour', 'day_of_week', 'month', 'is_peak_hour', 'is_weekend',
            'temperature', 'humidity', 'precipitation', 'wind_speed',
            'line_id', 'station_id', 'direction_id',
            'distance_km', 'stops_count', 'transfer_count'
        ]
        
        # Colonnes catégorielles
        self.categorical_columns = ['line_id', 'station_id', 'direction_id']
        
        # Colonnes numériques
        self.numerical_columns = [
            'hour', 'day_of_week', 'month', 'is_peak_hour', 'is_weekend',
            'temperature', 'humidity', 'precipitation', 'wind_speed',
            'distance_km', 'stops_count', 'transfer_count'
        ]
    
    def generate_historical_data(self, num_samples: int = 10000) -> pd.DataFrame:
        """
        Génère des données historiques synthétiques pour l'entraînement
        
        Args:
            num_samples: Nombre d'échantillons à générer
            
        Returns:
            DataFrame avec données historiques
        """
        logger.info(f"Génération de {num_samples} échantillons de données historiques...")
        
        # Dates sur 6 mois
        start_date = datetime.now() - timedelta(days=180)
        dates = pd.date_range(start=start_date, end=datetime.now(), freq='H')
        
        data = []
        
        for _ in range(num_samples):
            # Date et heure aléatoire
            timestamp = pd.to_datetime(np.random.choice(dates))
            
            # Caractéristiques temporelles
            hour = timestamp.hour
            day_of_week = timestamp.weekday()
            month = timestamp.month
            is_weekend = 1 if day_of_week >= 5 else 0
            
            # Heures de pointe (7-9h et 17-19h)
            is_peak_hour = 1 if (7 <= hour <= 9) or (17 <= hour <= 19) else 0
            
            # Données météo simulées
            temperature = np.random.normal(15, 10)  # 15°C ± 10°C
            humidity = np.random.uniform(30, 90)
            precipitation = np.random.exponential(0.1)  # Pluie occasionnelle
            wind_speed = np.random.exponential(5)
            
            # Données de transport
            line_id = f"line_{np.random.randint(1, 15)}"
            station_id = f"station_{np.random.randint(1, 100)}"
            direction_id = np.random.randint(0, 2)
            
            # Distance et complexité du trajet
            distance_km = np.random.uniform(1, 20)
            stops_count = max(1, int(distance_km * 0.8))
            transfer_count = np.random.poisson(0.5)  # 0-2 transferts en moyenne
            
            # ETA de base avec variations
            base_eta = distance_km * 2 + stops_count * 0.5 + transfer_count * 3
            
            # Facteurs de retard
            peak_delay = 1.3 if is_peak_hour else 1.0
            weather_delay = 1.2 if precipitation > 0.5 else 1.0
            weekend_factor = 0.9 if is_weekend else 1.0
            
            # ETA final avec bruit
            eta_minutes = base_eta * peak_delay * weather_delay * weekend_factor
            eta_minutes += np.random.normal(0, 2)  # Bruit gaussien
            eta_minutes = max(1, eta_minutes)  # Minimum 1 minute
            
            data.append({
                'timestamp': timestamp,
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
                'transfer_count': transfer_count,
                'eta_minutes': eta_minutes
            })
        
        df = pd.DataFrame(data)
        logger.info(f"Données générées : {len(df)} échantillons")
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prépare les features pour l'entraînement
        
        Args:
            df: DataFrame avec données historiques
            
        Returns:
            X: Features (samples, features)
            y: Targets (samples,)
        """
        logger.info("Préparation des features pour l'entraînement...")
        
        # Encodage des variables catégorielles
        for col in self.categorical_columns:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col])
            else:
                df[f'{col}_encoded'] = self.label_encoders[col].transform(df[col])
        
        # Sélection des features
        feature_cols = [f'{col}_encoded' if col in self.categorical_columns else col 
                       for col in self.feature_columns]
        
        # Normalisation des features numériques
        features_scaled = self.scaler.fit_transform(df[feature_cols])
        
        X = features_scaled
        y = df['eta_minutes'].values
        
        logger.info(f"Features préparées : X={X.shape}, y={y.shape}")
        return X, y
    
    def build_model(self) -> object:
        """
        Construit le modèle selon le type spécifié
        
        Returns:
            Modèle scikit-learn
        """
        if self.model_type == "random_forest":
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == "gradient_boosting":
            model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
        elif self.model_type == "neural_network":
            model = MLPRegressor(
                hidden_layer_sizes=(100, 50, 25),
                activation='relu',
                solver='adam',
                alpha=0.001,
                learning_rate='adaptive',
                max_iter=500,
                random_state=42
            )
        elif self.model_type == "svr":
            model = SVR(
                kernel='rbf',
                C=1.0,
                gamma='scale',
                epsilon=0.1
            )
        elif self.model_type == "ridge":
            model = Ridge(alpha=1.0, random_state=42)
        elif self.model_type == "lasso":
            model = Lasso(alpha=0.1, random_state=42)
        else:
            raise ValueError(f"Type de modèle non supporté : {self.model_type}")
        
        return model
    
    def train_model(self, X_train: np.ndarray, y_train: np.ndarray, 
                   X_val: np.ndarray, y_val: np.ndarray) -> object:
        """
        Entraîne le modèle
        
        Args:
            X_train, y_train: Données d'entraînement
            X_val, y_val: Données de validation
            
        Returns:
            Modèle entraîné
        """
        logger.info(f"Entraînement du modèle {self.model_type}...")
        
        # Construction du modèle
        self.model = self.build_model()
        
        # Entraînement
        self.model.fit(X_train, y_train)
        
        # Évaluation sur validation
        y_val_pred = self.model.predict(X_val)
        val_mae = mean_absolute_error(y_val, y_val_pred)
        val_r2 = r2_score(y_val, y_val_pred)
        
        logger.info(f"Validation MAE: {val_mae:.2f}, R²: {val_r2:.3f}")
        
        # Feature importance (si disponible)
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance = self.model.feature_importances_
            logger.info("Feature importance calculée")
        
        logger.info("Entraînement terminé")
        return self.model
    
    def evaluate_model(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """
        Évalue le modèle
        
        Args:
            X_test, y_test: Données de test
            
        Returns:
            Métriques d'évaluation
        """
        if self.model is None:
            return {"error": "Modèle non entraîné"}
        
        # Prédictions
        y_pred = self.model.predict(X_test)
        
        # Métriques
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_test, y_test, cv=5, scoring='neg_mean_absolute_error')
        cv_mae = -cv_scores.mean()
        
        metrics = {
            "mae": mae,
            "mse": mse,
            "rmse": rmse,
            "r2": r2,
            "cv_mae": cv_mae,
            "cv_std": cv_scores.std()
        }
        
        logger.info(f"Métriques d'évaluation : {metrics}")
        return metrics
    
    def save_model(self, filepath: str):
        """
        Sauvegarde le modèle et les préprocesseurs
        
        Args:
            filepath: Chemin de sauvegarde
        """
        if self.model is None:
            logger.warning("Aucun modèle à sauvegarder")
            return
        
        # Sauvegarde du modèle
        model_path = f"{filepath}_model.joblib"
        joblib.dump(self.model, model_path)
        
        # Sauvegarde des préprocesseurs
        preprocessors = {
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns,
            'categorical_columns': self.categorical_columns,
            'numerical_columns': self.numerical_columns,
            'feature_importance': self.feature_importance,
            'model_type': self.model_type
        }
        
        preprocessors_path = f"{filepath}_preprocessors.joblib"
        joblib.dump(preprocessors, preprocessors_path)
        
        logger.info(f"Modèle sauvegardé : {model_path}")
        logger.info(f"Préprocesseurs sauvegardés : {preprocessors_path}")
    
    def load_model(self, filepath: str):
        """
        Charge le modèle et les préprocesseurs
        
        Args:
            filepath: Chemin de chargement
        """
        # Chargement du modèle
        model_path = f"{filepath}_model.joblib"
        self.model = joblib.load(model_path)
        
        # Chargement des préprocesseurs
        preprocessors_path = f"{filepath}_preprocessors.joblib"
        preprocessors = joblib.load(preprocessors_path)
        
        self.scaler = preprocessors['scaler']
        self.label_encoders = preprocessors['label_encoders']
        self.feature_columns = preprocessors['feature_columns']
        self.categorical_columns = preprocessors['categorical_columns']
        self.numerical_columns = preprocessors['numerical_columns']
        self.feature_importance = preprocessors.get('feature_importance')
        self.model_type = preprocessors.get('model_type', 'unknown')
        
        logger.info(f"Modèle chargé : {model_path}")
    
    def predict_eta(self, features: Dict) -> float:
        """
        Prédit l'ETA pour de nouvelles données
        
        Args:
            features: Dictionnaire avec les features
            
        Returns:
            ETA prédit en minutes
        """
        if self.model is None:
            logger.warning("Modèle non chargé - Retour à la prédiction basique")
            return features.get('distance_km', 5) * 2
        
        # Préparation des features
        feature_vector = []
        
        for col in self.feature_columns:
            if col in self.categorical_columns:
                # Encodage des variables catégorielles
                if col in self.label_encoders:
                    encoded_value = self.label_encoders[col].transform([features[col]])[0]
                    feature_vector.append(encoded_value)
                else:
                    feature_vector.append(0)  # Valeur par défaut
            else:
                feature_vector.append(features.get(col, 0))
        
        # Normalisation
        feature_vector = self.scaler.transform([feature_vector])
        
        # Prédiction
        prediction = self.model.predict(feature_vector)[0]
        
        return max(1, prediction)  # Minimum 1 minute
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Retourne l'importance des features
        
        Returns:
            Dictionnaire feature -> importance
        """
        if self.feature_importance is None:
            return {}
        
        feature_names = [f'{col}_encoded' if col in self.categorical_columns else col 
                        for col in self.feature_columns]
        
        return dict(zip(feature_names, self.feature_importance))


def main():
    """Fonction principale pour entraîner le modèle"""
    logger.info("=== Entraînement du modèle ML léger ===")
    
    # Initialisation de l'entraîneur
    trainer = LightweightMLTrainer(model_type="random_forest")
    
    # Génération des données
    df = trainer.generate_historical_data(num_samples=50000)
    
    # Préparation des features
    X, y = trainer.prepare_features(df)
    
    # Split train/validation/test
    X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.2, random_state=42)
    
    logger.info(f"Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
    
    # Entraînement
    model = trainer.train_model(X_train, y_train, X_val, y_val)
    
    # Évaluation
    metrics = trainer.evaluate_model(X_test, y_test)
    
    # Sauvegarde
    trainer.save_model("models/lightweight_eta_model")
    
    # Affichage de l'importance des features
    feature_importance = trainer.get_feature_importance()
    logger.info("Top 5 features importantes:")
    for feature, importance in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]:
        logger.info(f"  {feature}: {importance:.3f}")
    
    logger.info("=== Entraînement terminé avec succès ===")
    logger.info(f"Métriques finales : {metrics}")


if __name__ == "__main__":
    main()





