import numpy as np
from geopy.distance import geodesic


class SimpleETAModel:
    def predict_eta(self, start_lat, start_lon, end_lat, end_lon):
        """Modèle simple basé sur la distance + constante métro"""
        # Calcul distance à vol d'oiseau
        start_coords = (start_lat, start_lon)
        end_coords = (end_lat, end_lon)
        distance_km = geodesic(start_coords, end_coords).km

        # Estimation : 5min/km en métro + 5min constantes
        eta = (distance_km * 5) + 5
        return max(5, min(eta, 60))  # Entre 5min et 1h