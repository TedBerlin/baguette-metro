#!/usr/bin/env python3
"""
Audit spécifique Google Places API - Problème Charles de Gaulle
"""

import requests
import json

def audit_charles_de_gaulle():
    """Audit spécifique pour Charles de Gaulle"""
    
    api_key = "AIzaSyAPuZgSlRBQfTKlTY96mHbkJ4p939nNib4"
    
    print("🔍 AUDIT SPÉCIFIQUE : CHARLES DE GAULLE")
    print("=" * 60)
    
    # Test 1: Recherche "Charles de Gaulle"
    print("\n🧪 Test 1: Recherche 'Charles de Gaulle'")
    url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    
    params = {
        "input": "Charles de Gaulle",
        "key": api_key,
        "language": "fr",
        "types": "geocode",
        "components": "country:fr"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status API: {data.get('status')}")
            
            if data.get("status") == "OK":
                predictions = data.get("predictions", [])
                print(f"Nombre de prédictions: {len(predictions)}")
                
                for i, pred in enumerate(predictions):
                    print(f"  {i+1}. {pred.get('description')}")
                    print(f"     Place ID: {pred.get('place_id')}")
                    print(f"     Types: {pred.get('types')}")
                    print()
            else:
                print(f"Erreur API: {data.get('error_message', 'Aucun message')}")
        else:
            print(f"Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 2: Recherche "CDG" (abréviation)
    print("\n🧪 Test 2: Recherche 'CDG'")
    params["input"] = "CDG"
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status API: {data.get('status')}")
            
            if data.get("status") == "OK":
                predictions = data.get("predictions", [])
                print(f"Nombre de prédictions: {len(predictions)}")
                
                for i, pred in enumerate(predictions):
                    print(f"  {i+1}. {pred.get('description')}")
                    print(f"     Place ID: {pred.get('place_id')}")
                    print(f"     Types: {pred.get('types')}")
                    print()
            else:
                print(f"Erreur API: {data.get('error_message', 'Aucun message')}")
        else:
            print(f"Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 3: Recherche "Aéroport Charles de Gaulle"
    print("\n🧪 Test 3: Recherche 'Aéroport Charles de Gaulle'")
    params["input"] = "Aéroport Charles de Gaulle"
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status API: {data.get('status')}")
            
            if data.get("status") == "OK":
                predictions = data.get("predictions", [])
                print(f"Nombre de prédictions: {len(predictions)}")
                
                for i, pred in enumerate(predictions):
                    print(f"  {i+1}. {pred.get('description')}")
                    print(f"     Place ID: {pred.get('place_id')}")
                    print(f"     Types: {pred.get('types')}")
                    print()
            else:
                print(f"Erreur API: {data.get('error_message', 'Aucun message')}")
        else:
            print(f"Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 4: Recherche sans restriction de type
    print("\n🧪 Test 4: Recherche sans restriction de type")
    params["input"] = "Charles de Gaulle"
    params.pop("types", None)  # Supprimer la restriction de type
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status API: {data.get('status')}")
            
            if data.get("status") == "OK":
                predictions = data.get("predictions", [])
                print(f"Nombre de prédictions: {len(predictions)}")
                
                for i, pred in enumerate(predictions):
                    print(f"  {i+1}. {pred.get('description')}")
                    print(f"     Place ID: {pred.get('place_id')}")
                    print(f"     Types: {pred.get('types')}")
                    print()
            else:
                print(f"Erreur API: {data.get('error_message', 'Aucun message')}")
        else:
            print(f"Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 5: Recherche avec establishment
    print("\n🧪 Test 5: Recherche avec type 'establishment'")
    params["input"] = "Charles de Gaulle"
    params["types"] = "establishment"
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status API: {data.get('status')}")
            
            if data.get("status") == "OK":
                predictions = data.get("predictions", [])
                print(f"Nombre de prédictions: {len(predictions)}")
                
                for i, pred in enumerate(predictions):
                    print(f"  {i+1}. {pred.get('description')}")
                    print(f"     Place ID: {pred.get('place_id')}")
                    print(f"     Types: {pred.get('types')}")
                    print()
            else:
                print(f"Erreur API: {data.get('error_message', 'Aucun message')}")
        else:
            print(f"Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("🚀 AUDIT GOOGLE PLACES - DIAGNOSTIC CHARLES DE GAULLE")
    print("=" * 60)
    audit_charles_de_gaulle()
    print("\n" + "=" * 60)
    print("✅ Audit terminé")



