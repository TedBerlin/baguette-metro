#!/usr/bin/env python3
"""
Module de cartographie Folium pour Baguette & Métro
"""

import folium
import streamlit as st
from typing import Tuple, List, Dict, Optional
import random

# Coordonnées de Paris (centre)
PARIS_CENTER = (48.8566, 2.3522)

def create_paris_map(zoom_start: int = 12) -> folium.Map:
    """
    Crée une carte de base centrée sur Paris
    """
    return folium.Map(
        location=PARIS_CENTER,
        zoom_start=zoom_start,
        tiles='OpenStreetMap',
        control_scale=True
    )

def add_departure_marker(map_obj: folium.Map, coords: Tuple[float, float], name: str) -> folium.Map:
    """
    Ajoute un marqueur de départ sur la carte
    """
    folium.Marker(
        location=coords,
        popup=f"📍 Départ: {name}",
        tooltip=f"📍 Départ: {name}",
        icon=folium.Icon(color='green', icon='play', prefix='fa')
    ).add_to(map_obj)
    return map_obj

def add_arrival_marker(map_obj: folium.Map, coords: Tuple[float, float], name: str) -> folium.Map:
    """
    Ajoute un marqueur d'arrivée sur la carte
    """
    folium.Marker(
        location=coords,
        popup=f"🎯 Arrivée: {name}",
        tooltip=f"🎯 Arrivée: {name}",
        icon=folium.Icon(color='red', icon='flag-checkered', prefix='fa')
    ).add_to(map_obj)
    return map_obj

def add_bakery_markers(map_obj: folium.Map, bakeries: List[Dict], recommended_index: int = 0) -> folium.Map:
    """
    Ajoute des marqueurs pour les boulangeries avec distinction de la recommandée
    """
    for i, bakery in enumerate(bakeries):
        # Distinguer la boulangerie recommandée
        if i == recommended_index:
            # Marqueur spécial pour la boulangerie recommandée
            folium.Marker(
                location=(bakery['lat'], bakery['lng']),
                popup=f"🥖 <b>RECOMMANDÉE</b><br>{bakery['name']}<br>⭐ {bakery['rating']}/5.0<br>📍 {bakery['address']}<br>⏰ Arrêt: {bakery.get('stop_time', '5-10')} min",
                tooltip=f"🥖 RECOMMANDÉE: {bakery['name']}",
                icon=folium.Icon(color='red', icon='star', prefix='fa')
            ).add_to(map_obj)
        else:
            # Marqueur normal pour les autres boulangeries
            folium.Marker(
                location=(bakery['lat'], bakery['lng']),
                popup=f"🥖 {bakery['name']}<br>⭐ {bakery['rating']}/5.0<br>📍 {bakery['address']}",
                tooltip=f"🥖 {bakery['name']}",
                icon=folium.Icon(color='orange', icon='bread-slice', prefix='fa')
            ).add_to(map_obj)
    return map_obj

def add_route_line(map_obj: folium.Map, departure: Tuple[float, float], arrival: Tuple[float, float], 
                  bakeries: List[Dict] = None) -> folium.Map:
    """
    Ajoute une ligne de trajet avec arrêts boulangerie
    """
    # Ligne principale départ → arrivée
    folium.PolyLine(
        locations=[departure, arrival],
        color='blue',
        weight=3,
        opacity=0.7,
        popup="Trajet principal"
    ).add_to(map_obj)
    
    # Si des boulangeries sont spécifiées, ajouter des lignes vers elles
    if bakeries:
        for bakery in bakeries:
            # Ligne vers la boulangerie
            folium.PolyLine(
                locations=[departure, (bakery['lat'], bakery['lng']), arrival],
                color='orange',
                weight=2,
                opacity=0.5,
                dash_array='5, 10',
                popup=f"Trajet avec arrêt: {bakery['name']}"
            ).add_to(map_obj)
    
    return map_obj

def generate_sample_bakeries(departure: Tuple[float, float], arrival: Tuple[float, float], 
                           count: int = 3) -> List[Dict]:
    """
    Génère des boulangeries d'exemple entre le départ et l'arrivée
    """
    bakeries = [
        {
            'name': 'Boulangerie Du Palais',
            'address': '12 Rue de Rivoli, 75001 Paris',
            'lat': 48.8566 + random.uniform(-0.01, 0.01),
            'lng': 2.3522 + random.uniform(-0.01, 0.01),
            'rating': 4.8,
            'specialties': ['Baguette tradition', 'Croissants au beurre', 'Pain au chocolat']
        },
        {
            'name': 'Maison Julien',
            'address': '75 Rue Saint-Antoine, 75004 Paris',
            'lat': 48.8566 + random.uniform(-0.01, 0.01),
            'lng': 2.3522 + random.uniform(-0.01, 0.01),
            'rating': 4.7,
            'specialties': ['Éclairs au café', 'Tarte aux fruits', 'Pain de campagne']
        },
        {
            'name': 'Le Grenier à Pain',
            'address': '38 Rue des Abbesses, 75018 Paris',
            'lat': 48.8566 + random.uniform(-0.01, 0.01),
            'lng': 2.3522 + random.uniform(-0.01, 0.01),
            'rating': 4.9,
            'specialties': ['Pain au levain', 'Croissants artisanaux', 'Pâtisseries fines']
        }
    ]
    
    return bakeries[:count]

def create_route_map(departure_coords: Tuple[float, float], departure_name: str,
                    arrival_coords: Tuple[float, float], arrival_name: str,
                    bakeries: List[Dict] = None, recommended_index: int = 0) -> folium.Map:
    """
    Crée une carte complète avec trajet et boulangeries
    """
    # Créer la carte de base
    map_obj = create_paris_map(zoom_start=13)
    
    # Ajouter les marqueurs
    map_obj = add_departure_marker(map_obj, departure_coords, departure_name)
    map_obj = add_arrival_marker(map_obj, arrival_coords, arrival_name)
    
    # Ajouter les boulangeries si fournies
    if bakeries:
        map_obj = add_bakery_markers(map_obj, bakeries, recommended_index)
        map_obj = add_route_line(map_obj, departure_coords, arrival_coords, bakeries)
    else:
        map_obj = add_route_line(map_obj, departure_coords, arrival_coords)
    
    return map_obj

def display_map_in_streamlit(map_obj: folium.Map, height: int = 500) -> None:
    """
    Affiche la carte dans Streamlit
    """
    st.components.v1.html(map_obj._repr_html_(), height=height)

def create_metro_stations_map() -> folium.Map:
    """
    Crée une carte avec les principales stations de métro parisiennes
    """
    map_obj = create_paris_map(zoom_start=11)
    
    # Stations de métro principales
    metro_stations = [
        {'name': 'Châtelet', 'coords': (48.8584, 2.3470), 'lines': ['1', '4', '7', '11', '14']},
        {'name': 'Gare du Nord', 'coords': (48.8809, 2.3553), 'lines': ['4', '5']},
        {'name': 'Gare de Lyon', 'coords': (48.8443, 2.3735), 'lines': ['1', '14']},
        {'name': 'République', 'coords': (48.8674, 2.3636), 'lines': ['3', '5', '8', '9', '11']},
        {'name': 'Opéra', 'coords': (48.8704, 2.3324), 'lines': ['3', '7', '8']},
        {'name': 'Bastille', 'coords': (48.8534, 2.3688), 'lines': ['1', '5', '8']},
        {'name': 'Charles de Gaulle - Étoile', 'coords': (48.8738, 2.2950), 'lines': ['1', '2', '6']},
        {'name': 'Montparnasse-Bienvenüe', 'coords': (48.8421, 2.3219), 'lines': ['4', '6', '12', '13']}
    ]
    
    for station in metro_stations:
        folium.Marker(
            location=station['coords'],
            popup=f"🚇 {station['name']}<br>Lignes: {', '.join(station['lines'])}",
            tooltip=f"🚇 {station['name']}",
            icon=folium.Icon(color='blue', icon='subway', prefix='fa')
        ).add_to(map_obj)
    
    return map_obj
