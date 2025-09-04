"""
Modèle ML avancé pour prédiction ETA
Utilise LSTM/Transformer pour prédire les temps d'attente basé sur données historiques GTFS
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
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Deep Learning
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras import Model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, MultiHeadAttention, LayerNormalization
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    # Création d'une classe Model factice pour éviter les erreurs d'import
    class Model:
        def __init__(self, *args, **kwargs):
            pass
        def compile(self, *args, **kwargs):
            pass
        def fit(self, *args, **kwargs):
            pass
        def predict(self, *args, **kwargs):
            pass
        def save(self, *args, **kwargs):
            pass
    
    print("⚠️ TensorFlow non disponible - Utilisation du modèle basique")

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedETATrainer:
    """Entraîneur pour modèle ML avancé de prédiction ETA"""
    
    def __init__(self, model_type: str = "lstm"):
        """
        Initialise l'entraîneur
        
        Args:
            model_type: Type de modèle ("lstm", "transformer", "hybrid")
        """
        self.model_type = model_type
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.model = None
        self.history = None
        
        # Paramètres du modèle
        self.sequence_length = 24  # 24 heures d'historique
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
    
    def prepare_sequences(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prépare les séquences pour l'entraînement LSTM/Transformer
        
        Args:
            df: DataFrame avec données historiques
            
        Returns:
            X: Features en séquences (samples, sequence_length, features)
            y: Targets (samples,)
        """
        logger.info("Préparation des séquences pour l'entraînement...")
        
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
        
        # Création des séquences
        X, y = [], []
        
        for i in range(self.sequence_length, len(features_scaled)):
            X.append(features_scaled[i-self.sequence_length:i])
            y.append(df.iloc[i]['eta_minutes'])
        
        X = np.array(X)
        y = np.array(y)
        
        logger.info(f"Séquences créées : X={X.shape}, y={y.shape}")
        return X, y
    
    def build_lstm_model(self, input_shape: Tuple[int, int]) -> Model:
        """
        Construit un modèle LSTM
        
        Args:
            input_shape: Forme des données d'entrée (sequence_length, features)
            
        Returns:
            Modèle Keras
        """
        model = Sequential([
            LSTM(128, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(64, return_sequences=False),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dropout(0.1),
            Dense(1, activation='linear')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def build_transformer_model(self, input_shape: Tuple[int, int]) -> Model:
        """
        Construit un modèle Transformer
        
        Args:
            input_shape: Forme des données d'entrée (sequence_length, features)
            
        Returns:
            Modèle Keras
        """
        inputs = Input(shape=input_shape)
        
        # Multi-head attention
        attention_output = MultiHeadAttention(
            num_heads=8, key_dim=16
        )(inputs, inputs)
        
        # Add & Norm
        attention_output = LayerNormalization()(attention_output + inputs)
        
        # Feed forward
        ffn = Dense(128, activation='relu')(attention_output)
        ffn = Dense(input_shape[1])(ffn)
        ffn = LayerNormalization()(ffn + attention_output)
        
        # Global average pooling
        pooled = tf.keras.layers.GlobalAveragePooling1D()(ffn)
        
        # Output layers
        dense1 = Dense(64, activation='relu')(pooled)
        dropout = Dropout(0.2)(dense1)
        outputs = Dense(1, activation='linear')(dropout)
        
        model = Model(inputs=inputs, outputs=outputs)
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def train_model(self, X_train: np.ndarray, y_train: np.ndarray, 
                   X_val: np.ndarray, y_val: np.ndarray) -> Model:
        """
        Entraîne le modèle
        
        Args:
            X_train, y_train: Données d'entraînement
            X_val, y_val: Données de validation
            
        Returns:
            Modèle entraîné
        """
        logger.info(f"Entraînement du modèle {self.model_type}...")
        
        if not TENSORFLOW_AVAILABLE:
            logger.warning("TensorFlow non disponible - Utilisation du modèle basique")
            return None
        
        # Callbacks
        callbacks = [
            EarlyStopping(patience=10, restore_best_weights=True),
            ReduceLROnPlateau(factor=0.5, patience=5, min_lr=1e-6)
        ]
        
        # Construction du modèle
        if self.model_type == "lstm":
            self.model = self.build_lstm_model((X_train.shape[1], X_train.shape[2]))
        elif self.model_type == "transformer":
            self.model = self.build_transformer_model((X_train.shape[1], X_train.shape[2]))
        else:
            raise ValueError(f"Type de modèle non supporté : {self.model_type}")
        
        # Entraînement
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=100,
            batch_size=32,
            callbacks=callbacks,
            verbose=1
        )
        
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
        
        metrics = {
            "mae": mae,
            "mse": mse,
            "rmse": rmse,
            "r2": r2
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
        model_path = f"{filepath}_model.h5"
        self.model.save(model_path)
        
        # Sauvegarde des préprocesseurs
        preprocessors = {
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns,
            'categorical_columns': self.categorical_columns,
            'numerical_columns': self.numerical_columns,
            'sequence_length': self.sequence_length
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
        if not TENSORFLOW_AVAILABLE:
            logger.warning("TensorFlow non disponible - Impossible de charger le modèle")
            return
        
        # Chargement du modèle
        model_path = f"{filepath}_model.h5"
        self.model = tf.keras.models.load_model(model_path)
        
        # Chargement des préprocesseurs
        preprocessors_path = f"{filepath}_preprocessors.joblib"
        preprocessors = joblib.load(preprocessors_path)
        
        self.scaler = preprocessors['scaler']
        self.label_encoders = preprocessors['label_encoders']
        self.feature_columns = preprocessors['feature_columns']
        self.categorical_columns = preprocessors['categorical_columns']
        self.numerical_columns = preprocessors['numerical_columns']
        self.sequence_length = preprocessors['sequence_length']
        
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
        
        # Création d'une séquence (répétition pour simuler l'historique)
        sequence = np.tile(feature_vector, (self.sequence_length, 1))
        sequence = sequence.reshape(1, self.sequence_length, -1)
        
        # Prédiction
        prediction = self.model.predict(sequence, verbose=0)[0][0]
        
        return max(1, prediction)  # Minimum 1 minute


def main():
    """Fonction principale pour entraîner le modèle"""
    logger.info("=== Entraînement du modèle ML avancé ===")
    
    # Initialisation de l'entraîneur
    trainer = AdvancedETATrainer(model_type="lstm")
    
    # Génération des données
    df = trainer.generate_historical_data(num_samples=50000)
    
    # Préparation des séquences
    X, y = trainer.prepare_sequences(df)
    
    # Split train/validation/test
    X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.2, random_state=42)
    
    logger.info(f"Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
    
    # Entraînement
    model = trainer.train_model(X_train, y_train, X_val, y_val)
    
    if model is not None:
        # Évaluation
        metrics = trainer.evaluate_model(X_test, y_test)
        
        # Sauvegarde
        trainer.save_model("models/advanced_eta_model")
        
        logger.info("=== Entraînement terminé avec succès ===")
        logger.info(f"Métriques finales : {metrics}")
    else:
        logger.warning("Entraînement échoué - TensorFlow non disponible")


if __name__ == "__main__":
    main()
