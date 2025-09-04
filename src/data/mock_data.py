#!/usr/bin/env python3
"""
Données mock pour le MVP - Boulangeries et trajets RATP
"""

import random
from typing import Dict, List, Any
from datetime import datetime, timedelta

# Données mock des boulangeries parisiennes
MOCK_BAKERIES = [
    {
        "id": "bakery_001",
        "name": "Du Pain et des Idées",
        "address": "34 Rue Yves Toudic, 75010 Paris",
        "lat": 48.8704,
        "lng": 2.3624,
        "rating": 4.8,
        "reviews": 1247,
        "types": ["bakery", "food", "establishment"],
        "opening_hours": "06:00-20:00",
        "specialties": ["Pain au chocolat", "Croissants", "Baguettes tradition"],
        "price_level": 2,
        "photos": ["https://example.com/photo1.jpg"],
        "website": "https://dupainetdesidees.com"
    },
    {
        "id": "bakery_002",
        "name": "Poilâne",
        "address": "8 Rue du Cherche-Midi, 75006 Paris",
        "lat": 48.8534,
        "lng": 2.3324,
        "rating": 4.7,
        "reviews": 892,
        "types": ["bakery", "food", "establishment"],
        "opening_hours": "07:00-19:00",
        "specialties": ["Pain Poilâne", "Tartes", "Pâtisseries"],
        "price_level": 3,
        "photos": ["https://example.com/photo2.jpg"],
        "website": "https://poilane.com"
    },
    {
        "id": "bakery_003",
        "name": "Blé Sucré",
        "address": "7 Rue Antoine Vollon, 75012 Paris",
        "lat": 48.8512,
        "lng": 2.3894,
        "rating": 4.6,
        "reviews": 567,
        "types": ["bakery", "food", "establishment"],
        "opening_hours": "06:30-19:30",
        "specialties": ["Croissants", "Pain au chocolat", "Chaussons"],
        "price_level": 2,
        "photos": ["https://example.com/photo3.jpg"],
        "website": None
    },
    {
        "id": "bakery_004",
        "name": "Mamiche",
        "address": "45 Rue Condorcet, 75009 Paris",
        "lat": 48.8834,
        "lng": 2.3324,
        "rating": 4.5,
        "reviews": 423,
        "types": ["bakery", "food", "establishment"],
        "opening_hours": "07:00-20:00",
        "specialties": ["Baguettes", "Viennoiseries", "Sandwiches"],
        "price_level": 2,
        "photos": ["https://example.com/photo4.jpg"],
        "website": "https://mamiche.fr"
    },
    {
        "id": "bakery_005",
        "name": "Liberté",
        "address": "39 Rue de Bretagne, 75003 Paris",
        "lat": 48.8634,
        "lng": 2.3824,
        "rating": 4.4,
        "reviews": 678,
        "types": ["bakery", "food", "establishment"],
        "opening_hours": "06:00-21:00",
        "specialties": ["Pain bio", "Pâtisseries", "Tartes"],
        "price_level": 2,
        "photos": ["https://example.com/photo5.jpg"],
        "website": "https://liberte-boulangerie.com"
    },
    {
        "id": "bakery_006",
        "name": "Boulangerie Utopie",
        "address": "20 Rue Jean-Pierre Timbaud, 75011 Paris",
        "lat": 48.8664,
        "lng": 2.3724,
        "rating": 4.3,
        "reviews": 345,
        "types": ["bakery", "food", "establishment"],
        "opening_hours": "07:00-19:00",
        "specialties": ["Pain bio", "Viennoiseries", "Sandwiches"],
        "price_level": 2,
        "photos": ["https://example.com/photo6.jpg"],
        "website": None
    },
    {
        "id": "bakery_007",
        "name": "Boulangerie Bo",
        "address": "85 Rue de la Roquette, 75011 Paris",
        "lat": 48.8584,
        "lng": 2.3724,
        "rating": 4.2,
        "reviews": 234,
        "types": ["bakery", "food", "establishment"],
        "opening_hours": "06:30-20:00",
        "specialties": ["Croissants", "Pain au chocolat", "Baguettes"],
        "price_level": 1,
        "photos": ["https://example.com/photo7.jpg"],
        "website": None
    },
    {
        "id": "bakery_008",
        "name": "Boulangerie Julien",
        "address": "75 Rue Saint-Honoré, 75001 Paris",
        "lat": 48.8634,
        "lng": 2.3424,
        "rating": 4.1,
        "reviews": 456,
        "types": ["bakery", "food", "establishment"],
        "opening_hours": "06:00-19:30",
        "specialties": ["Pain tradition", "Viennoiseries", "Pâtisseries"],
        "price_level": 2,
        "photos": ["https://example.com/photo8.jpg"],
        "website": None
    }
]

# Données mock des lignes RATP
MOCK_RATP_LINES = [
    {"id": "line_1", "name": "Ligne 1", "color": "#FFCD00", "stations": ["La Défense", "Champs-Élysées", "Louvre", "Bastille", "Château de Vincennes"]},
    {"id": "line_2", "name": "Ligne 2", "color": "#003CA6", "stations": ["Porte Dauphine", "Étoile", "Pigalle", "Barbès", "Nation"]},
    {"id": "line_3", "name": "Ligne 3", "color": "#837902", "stations": ["Pont de Levallois", "Saint-Lazare", "Opéra", "République", "Gallieni"]},
    {"id": "line_4", "name": "Ligne 4", "color": "#BE4189", "stations": ["Porte de Clignancourt", "Gare du Nord", "Châtelet", "Montparnasse", "Mairie de Montrouge"]},
    {"id": "line_5", "name": "Ligne 5", "color": "#996633", "stations": ["Bobigny", "Gare du Nord", "Gare de l'Est", "Bastille", "Place d'Italie"]},
    {"id": "line_6", "name": "Ligne 6", "color": "#76C6BC", "stations": ["Charles de Gaulle", "Étoile", "Montparnasse", "Denfert-Rochereau", "Nation"]},
    {"id": "line_7", "name": "Ligne 7", "color": "#F49A00", "stations": ["La Courneuve", "Gare de l'Est", "Châtelet", "Place d'Italie", "Villejuif"]},
    {"id": "line_8", "name": "Ligne 8", "color": "#C9910D", "stations": ["Balard", "Invalides", "Opéra", "République", "Créteil"]},
    {"id": "line_9", "name": "Ligne 9", "color": "#B6BD00", "stations": ["Pont de Sèvres", "Trocadéro", "Opéra", "République", "Mairie de Montreuil"]},
    {"id": "line_10", "name": "Ligne 10", "color": "#E3B32A", "stations": ["Boulogne", "Auteuil", "Duroc", "Cluny", "Gare d'Austerlitz"]},
    {"id": "line_11", "name": "Ligne 11", "color": "#8D5E2A", "stations": ["Châtelet", "République", "Belleville", "Mairie des Lilas"]},
    {"id": "line_12", "name": "Ligne 12", "color": "#007852", "stations": ["Front Populaire", "Gare du Nord", "Madeleine", "Montparnasse", "Mairie d'Issy"]},
    {"id": "line_13", "name": "Ligne 13", "color": "#8EC8D6", "stations": ["Saint-Denis", "Gare du Nord", "Invalides", "Châtillon"]},
    {"id": "line_14", "name": "Ligne 14", "color": "#62259D", "stations": ["Saint-Lazare", "Madeleine", "Pyramides", "Châtelet", "Bibliothèque"]}
]

# Données mock des trajets populaires
MOCK_POPULAR_ROUTES = [
    {
        "id": "route_001",
        "name": "Tour Eiffel → Louvre",
        "start": {"name": "Tour Eiffel", "lat": 48.8584, "lng": 2.2945},
        "end": {"name": "Musée du Louvre", "lat": 48.8606, "lng": 2.3376},
        "lines": ["Ligne 6", "Ligne 1"],
        "duration": 15,
        "distance": 2.1,
        "popularity": 95
    },
    {
        "id": "route_002",
        "name": "Gare du Nord → Champs-Élysées",
        "start": {"name": "Gare du Nord", "lat": 48.8809, "lng": 2.3553},
        "end": {"name": "Champs-Élysées", "lat": 48.8698, "lng": 2.3077},
        "lines": ["Ligne 4", "Ligne 1"],
        "duration": 12,
        "distance": 1.8,
        "popularity": 87
    },
    {
        "id": "route_003",
        "name": "Montmartre → Notre-Dame",
        "start": {"name": "Sacré-Cœur", "lat": 48.8867, "lng": 2.3431},
        "end": {"name": "Notre-Dame", "lat": 48.8530, "lng": 2.3499},
        "lines": ["Ligne 2", "Ligne 4"],
        "duration": 18,
        "distance": 2.5,
        "popularity": 76
    },
    {
        "id": "route_004",
        "name": "Bastille → Arc de Triomphe",
        "start": {"name": "Place de la Bastille", "lat": 48.8534, "lng": 2.3688},
        "end": {"name": "Arc de Triomphe", "lat": 48.8738, "lng": 2.2950},
        "lines": ["Ligne 1", "Ligne 6"],
        "duration": 20,
        "distance": 3.2,
        "popularity": 82
    },
    {
        "id": "route_005",
        "name": "Gare de Lyon → Opéra",
        "start": {"name": "Gare de Lyon", "lat": 48.8443, "lng": 2.3733},
        "end": {"name": "Opéra Garnier", "lat": 48.8716, "lng": 2.3317},
        "lines": ["Ligne 1", "Ligne 8"],
        "duration": 14,
        "distance": 2.0,
        "popularity": 91
    }
]

# Données mock des statistiques
MOCK_STATS = {
    "total_users": 12847,
    "total_routes": 45623,
    "total_bakeries": 1234,
    "time_saved_hours": 342,
    "popular_bakeries": ["Du Pain et des Idées", "Poilâne", "Blé Sucré"],
    "popular_lines": ["Ligne 1", "Ligne 4", "Ligne 6"],
    "peak_hours": ["08:00-09:00", "17:00-18:00"],
    "avg_route_duration": 18.5,
    "avg_bakery_rating": 4.3
}

def get_mock_bakeries(lat: float = 48.8566, lng: float = 2.3522, radius: int = 500) -> List[Dict[str, Any]]:
    """Retourne des boulangeries mock à proximité"""
    # Simulation de filtrage par distance
    nearby_bakeries = []
    for bakery in MOCK_BAKERIES:
        # Calcul simple de distance (formule de Haversine simplifiée)
        distance = ((bakery["lat"] - lat) ** 2 + (bakery["lng"] - lng) ** 2) ** 0.5 * 111000  # mètres
        if distance <= radius:
            bakery_copy = bakery.copy()
            bakery_copy["distance"] = round(distance)
            nearby_bakeries.append(bakery_copy)
    
    # Tri par distance
    nearby_bakeries.sort(key=lambda x: x["distance"])
    return nearby_bakeries[:10]  # Limite à 10 résultats

def get_mock_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float, include_bakery: bool = True) -> Dict[str, Any]:
    """Simule un calcul de trajet avec boulangerie"""
    # Calcul de distance simple
    distance = ((end_lat - start_lat) ** 2 + (end_lon - start_lon) ** 2) ** 0.5 * 111  # km
    
    # Temps de base (3 min/km + 5 min constantes)
    base_time = distance * 3 + 5
    
    # Ajout temps boulangerie si demandé
    bakery_time = 8 if include_bakery else 0
    total_time = base_time + bakery_time
    
    # Boulangerie recommandée
    recommended_bakery = None
    if include_bakery:
        nearby_bakeries = get_mock_bakeries((start_lat + end_lat) / 2, (start_lon + end_lon) / 2, 1000)
        if nearby_bakeries:
            recommended_bakery = nearby_bakeries[0]
    
    return {
        "eta_minutes": round(total_time, 1),
        "eta_seconds": int(total_time * 60),
        "distance_km": round(distance, 2),
        "include_bakery": include_bakery,
        "bakery_time": bakery_time,
        "recommended_bakery": recommended_bakery,
        "lines_used": random.sample([line["name"] for line in MOCK_RATP_LINES], random.randint(1, 3)),
        "transfers": random.randint(0, 2),
        "model_type": "mock_simulation",
        "timestamp": datetime.now().isoformat()
    }

def get_mock_stats() -> Dict[str, Any]:
    """Retourne les statistiques mock"""
    return MOCK_STATS.copy()

def get_mock_popular_routes() -> List[Dict[str, Any]]:
    """Retourne les trajets populaires"""
    return MOCK_POPULAR_ROUTES.copy()

def get_mock_ratp_lines() -> List[Dict[str, Any]]:
    """Retourne les lignes RATP"""
    return MOCK_RATP_LINES.copy()

def generate_mock_usage_data(days: int = 30) -> List[Dict[str, Any]]:
    """Génère des données d'utilisation mock"""
    data = []
    base_date = datetime.now() - timedelta(days=days)
    
    for i in range(days):
        date = base_date + timedelta(days=i)
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "users": random.randint(300, 500),
            "routes": random.randint(1200, 1800),
            "bakeries_found": random.randint(80, 120),
            "avg_rating": round(random.uniform(4.0, 4.8), 1)
        })
    
    return data





