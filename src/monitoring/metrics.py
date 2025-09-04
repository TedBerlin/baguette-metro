"""
Système de monitoring pour l'API et le modèle ML
"""

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)

class APIMetrics:
    """Collecteur de métriques pour l'API"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.request_count = 0
        self.error_count = 0
        self.response_times = deque(maxlen=max_history)
        self.endpoint_usage = defaultdict(int)
        self.error_log = deque(maxlen=100)
        self.start_time = datetime.now()
        self.lock = threading.Lock()
    
    def record_request(self, endpoint: str, method: str, response_time: float, 
                      status_code: int, error: str = None):
        """Enregistre une requête"""
        with self.lock:
            self.request_count += 1
            self.response_times.append(response_time)
            self.endpoint_usage[f"{method} {endpoint}"] += 1
            
            if status_code >= 400 or error:
                self.error_count += 1
                if error:
                    self.error_log.append({
                        "timestamp": datetime.now().isoformat(),
                        "endpoint": endpoint,
                        "error": error,
                        "status_code": status_code
                    })
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques"""
        with self.lock:
            if not self.response_times:
                avg_response_time = 0
                min_response_time = 0
                max_response_time = 0
            else:
                avg_response_time = sum(self.response_times) / len(self.response_times)
                min_response_time = min(self.response_times)
                max_response_time = max(self.response_times)
            
            uptime = datetime.now() - self.start_time
            
            return {
                "uptime_seconds": uptime.total_seconds(),
                "uptime_formatted": str(uptime).split('.')[0],
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "error_rate": (self.error_count / self.request_count * 100) if self.request_count > 0 else 0,
                "avg_response_time_ms": round(avg_response_time * 1000, 2),
                "min_response_time_ms": round(min_response_time * 1000, 2),
                "max_response_time_ms": round(max_response_time * 1000, 2),
                "requests_per_minute": self._calculate_rpm(),
                "top_endpoints": self._get_top_endpoints(),
                "recent_errors": list(self.error_log)[-5:]  # 5 dernières erreurs
            }
    
    def _calculate_rpm(self) -> float:
        """Calcule les requêtes par minute"""
        if self.request_count == 0:
            return 0.0
        
        uptime_minutes = (datetime.now() - self.start_time).total_seconds() / 60
        return round(self.request_count / uptime_minutes, 2)
    
    def _get_top_endpoints(self) -> List[Dict[str, Any]]:
        """Retourne les endpoints les plus utilisés"""
        sorted_endpoints = sorted(
            self.endpoint_usage.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return [
            {"endpoint": endpoint, "count": count}
            for endpoint, count in sorted_endpoints[:5]
        ]

class MLMetrics:
    """Collecteur de métriques pour le modèle ML"""
    
    def __init__(self):
        self.prediction_count = 0
        self.avg_prediction_time = 0
        self.model_accuracy = 0.98  # R² score
        self.feature_importance = {}
        self.prediction_history = deque(maxlen=100)
        self.start_time = datetime.now()
        self.lock = threading.Lock()
    
    def record_prediction(self, prediction_time: float, features: Dict, 
                         prediction: float, confidence: float):
        """Enregistre une prédiction"""
        with self.lock:
            self.prediction_count += 1
            
            # Mise à jour du temps moyen
            if self.prediction_count == 1:
                self.avg_prediction_time = prediction_time
            else:
                self.avg_prediction_time = (
                    (self.avg_prediction_time * (self.prediction_count - 1) + prediction_time) 
                    / self.prediction_count
                )
            
            # Historique des prédictions
            self.prediction_history.append({
                "timestamp": datetime.now().isoformat(),
                "prediction_time_ms": round(prediction_time * 1000, 2),
                "prediction_minutes": round(prediction, 2),
                "confidence": confidence,
                "features_summary": {
                    "distance_km": features.get("distance_km", 0),
                    "is_peak_hour": features.get("is_peak_hour", 0),
                    "is_weekend": features.get("is_weekend", 0)
                }
            })
    
    def update_feature_importance(self, importance: Dict[str, float]):
        """Met à jour l'importance des features"""
        with self.lock:
            self.feature_importance = importance
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques ML"""
        with self.lock:
            uptime = datetime.now() - self.start_time
            
            return {
                "uptime_seconds": uptime.total_seconds(),
                "total_predictions": self.prediction_count,
                "avg_prediction_time_ms": round(self.avg_prediction_time * 1000, 2),
                "model_accuracy": self.model_accuracy,
                "predictions_per_minute": self._calculate_ppm(),
                "feature_importance": self.feature_importance,
                "recent_predictions": list(self.prediction_history)[-10:],  # 10 dernières
                "performance_grade": self._get_performance_grade()
            }
    
    def _calculate_ppm(self) -> float:
        """Calcule les prédictions par minute"""
        if self.prediction_count == 0:
            return 0.0
        
        uptime_minutes = (datetime.now() - self.start_time).total_seconds() / 60
        return round(self.prediction_count / uptime_minutes, 2)
    
    def _get_performance_grade(self) -> str:
        """Retourne une note de performance"""
        if self.avg_prediction_time < 0.01:  # < 10ms
            return "A+"
        elif self.avg_prediction_time < 0.05:  # < 50ms
            return "A"
        elif self.avg_prediction_time < 0.1:  # < 100ms
            return "B"
        elif self.avg_prediction_time < 0.5:  # < 500ms
            return "C"
        else:
            return "D"

class SystemMonitor:
    """Moniteur système principal"""
    
    def __init__(self):
        self.api_metrics = APIMetrics()
        self.ml_metrics = MLMetrics()
        self.system_start_time = datetime.now()
    
    def get_full_status(self) -> Dict[str, Any]:
        """Retourne le statut complet du système"""
        return {
            "system": {
                "status": "healthy",
                "uptime": str(datetime.now() - self.system_start_time).split('.')[0],
                "timestamp": datetime.now().isoformat()
            },
            "api": self.api_metrics.get_stats(),
            "ml_model": self.ml_metrics.get_stats(),
            "summary": self._get_summary()
        }
    
    def _get_summary(self) -> Dict[str, Any]:
        """Résumé des performances"""
        api_stats = self.api_metrics.get_stats()
        ml_stats = self.ml_metrics.get_stats()
        
        return {
            "overall_health": "excellent" if api_stats["error_rate"] < 1 else "good",
            "performance_score": ml_stats["performance_grade"],
            "total_operations": api_stats["total_requests"] + ml_stats["total_predictions"],
            "avg_response_time": api_stats["avg_response_time_ms"],
            "model_accuracy": ml_stats["model_accuracy"]
        }

# Instance globale
system_monitor = SystemMonitor()

def get_system_monitor() -> SystemMonitor:
    """Retourne l'instance du moniteur système"""
    return system_monitor





