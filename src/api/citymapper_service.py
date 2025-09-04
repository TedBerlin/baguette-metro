#!/usr/bin/env python3
"""
Service Citymapper mock pour Baguette & Métro
Simulation intelligente des comparaisons d'itinéraires
"""

import random
from typing import List, Dict
from datetime import datetime, timedelta

class CitymapperMockService:
    def __init__(self):
        self.routes_cache = {}
        self.last_update = datetime.now()
        
    async def compare_routes(self, origin: str, destination: str, time: str = None) -> Dict:
        """Comparaison d'itinéraires mock intelligente"""
        try:
            # Génération d'itinéraires réalistes
            routes = self._generate_realistic_routes(origin, destination, time)
            
            # Calcul des métriques intelligentes
            enhanced_routes = self._enhance_routes_with_metrics(routes)
            
            # Mise à jour du cache
            cache_key = f"{origin}_{destination}_{time}"
            self.routes_cache[cache_key] = {
                "routes": enhanced_routes,
                "timestamp": datetime.now().isoformat(),
                "origin": origin,
                "destination": destination
            }
            
            return {
                "routes": enhanced_routes,
                "comparison": self._generate_comparison_summary(enhanced_routes),
                "recommendations": self._generate_recommendations(enhanced_routes),
                "timestamp": datetime.now().isoformat(),
                "source": "citymapper_mock"
            }
            
        except Exception as e:
            print(f"Erreur service Citymapper mock: {e}")
            return {"error": str(e)}
    
    def _generate_realistic_routes(self, origin: str, destination: str, time: str = None) -> List[Dict]:
        """Génération d'itinéraires réalistes selon l'origine et destination"""
        # Heure de départ (par défaut maintenant)
        if time:
            try:
                departure_time = datetime.strptime(time, "%H:%M")
                hour = departure_time.hour
            except:
                hour = datetime.now().hour
        else:
            hour = datetime.now().hour
        
        # Détermination du contexte (heures de pointe, etc.)
        is_peak_hour = 7 <= hour <= 9 or 17 <= hour <= 19
        is_night = 23 <= hour or hour <= 5
        
        routes = []
        
        # Route 1: Métro + Bus (toujours disponible)
        metro_bus = {
            "route": "Métro + Bus",
            "duration": self._calculate_duration(origin, destination, "metro_bus", is_peak_hour),
            "cost": "2.10€",
            "comfort": "Moyen",
            "eco_friendly": True,
            "reliability": 0.85,
            "crowding": "Moyen" if is_peak_hour else "Faible",
            "transfers": random.randint(1, 2),
            "accessibility": "Élevée",
            "real_time_updates": True
        }
        routes.append(metro_bus)
        
        # Route 2: Vélo (selon météo et heure)
        if not is_night and not is_peak_hour:
            velo = {
                "route": "Vélo",
                "duration": self._calculate_duration(origin, destination, "velo", is_peak_hour),
                "cost": "0€",
                "comfort": "Élevé",
                "eco_friendly": True,
                "reliability": 0.95,
                "crowding": "Faible",
                "transfers": 0,
                "accessibility": "Moyenne",
                "real_time_updates": False
            }
            routes.append(velo)
        
        # Route 3: Marche (si distance < 2km)
        distance = self._estimate_distance(origin, destination)
        if distance < 2.0:
            marche = {
                "route": "Marche",
                "duration": f"{int(distance * 15)} min",
                "cost": "0€",
                "comfort": "Élevé",
                "eco_friendly": True,
                "reliability": 1.0,
                "crowding": "Faible",
                "transfers": 0,
                "accessibility": "Élevée",
                "real_time_updates": False
            }
            routes.append(marche)
        
        # Route 4: Taxi/VTC (toujours disponible)
        taxi = {
            "route": "Taxi/VTC",
            "duration": self._calculate_duration(origin, destination, "taxi", is_peak_hour),
            "cost": f"{random.randint(15, 35)}€",
            "comfort": "Élevé",
            "eco_friendly": False,
            "reliability": 0.90,
            "crowding": "Faible",
            "transfers": 0,
            "accessibility": "Élevée",
            "real_time_updates": True
        }
        routes.append(taxi)
        
        # Route 5: RER + Métro (pour longues distances)
        if distance > 5.0:
            rer_metro = {
                "route": "RER + Métro",
                "duration": self._calculate_duration(origin, destination, "rer_metro", is_peak_hour),
                "cost": "3.80€",
                "comfort": "Moyen",
                "eco_friendly": True,
                "reliability": 0.80,
                "crowding": "Élevé" if is_peak_hour else "Moyen",
                "transfers": random.randint(1, 2),
                "accessibility": "Élevée",
                "real_time_updates": True
            }
            routes.append(rer_metro)
        
        return routes
    
    def _calculate_duration(self, origin: str, destination: str, mode: str, is_peak_hour: bool) -> str:
        """Calcul réaliste de la durée selon le mode et l'heure"""
        base_distance = self._estimate_distance(origin, destination)
        
        # Multiplicateurs selon le mode
        mode_multipliers = {
            "metro_bus": 1.0,
            "velo": 0.6,
            "taxi": 0.7,
            "rer_metro": 1.2,
            "marche": 3.0
        }
        
        # Multiplicateur heure de pointe
        peak_multiplier = 1.3 if is_peak_hour else 1.0
        
        # Calcul de la durée en minutes
        duration_minutes = int(base_distance * mode_multipliers.get(mode, 1.0) * peak_multiplier * 8)
        
        if duration_minutes < 60:
            return f"{duration_minutes} min"
        else:
            hours = duration_minutes // 60
            minutes = duration_minutes % 60
            return f"{hours}h{minutes:02d}"
    
    def _estimate_distance(self, origin: str, destination: str) -> float:
        """Estimation réaliste de la distance"""
        # Simulation basée sur les noms des lieux
        # En production, utiliserait de vraies coordonnées GPS
        
        # Distances typiques Paris
        distances = {
            "paris": 0.5,
            "champs": 1.2,
            "tour": 2.1,
            "montmartre": 3.5,
            "montparnasse": 2.8,
            "gare": 1.8,
            "aeroport": 25.0,
            "versailles": 18.0
        }
        
        # Calcul basé sur les mots-clés
        total_distance = 0
        for word in distances:
            if word in origin.lower() or word in destination.lower():
                total_distance += distances[word]
        
        # Distance par défaut si aucune correspondance
        if total_distance == 0:
            total_distance = random.uniform(1.5, 8.0)
        
        return round(total_distance, 1)
    
    def _enhance_routes_with_metrics(self, routes: List[Dict]) -> List[Dict]:
        """Enrichissement des routes avec des métriques intelligentes"""
        for route in routes:
            # Score global (0-100)
            route["score"] = self._calculate_route_score(route)
            
            # Indicateurs visuels
            route["status"] = self._get_route_status(route["score"])
            route["trend"] = self._get_route_trend(route)
            
            # Informations supplémentaires
            route["advantages"] = self._get_route_advantages(route)
            route["disadvantages"] = self._get_route_disadvantages(route)
        
        # Tri par score décroissant
        routes.sort(key=lambda x: x["score"], reverse=True)
        
        return routes
    
    def _calculate_route_score(self, route: Dict) -> int:
        """Calcul du score global d'une route (0-100)"""
        score = 0
        
        # Durée (30 points)
        duration_str = route["duration"]
        if "min" in duration_str:
            minutes = int(duration_str.replace(" min", ""))
            if minutes <= 15:
                score += 30
            elif minutes <= 30:
                score += 25
            elif minutes <= 45:
                score += 20
            else:
                score += 15
        else:
            score += 20  # Heures
        
        # Coût (25 points)
        cost_str = route["cost"]
        if cost_str == "0€":
            score += 25
        elif "€" in cost_str:
            cost = float(cost_str.replace("€", ""))
            if cost <= 3:
                score += 20
            elif cost <= 10:
                score += 15
            else:
                score += 10
        
        # Confort (20 points)
        comfort_scores = {"Faible": 10, "Moyen": 15, "Élevé": 20}
        score += comfort_scores.get(route["comfort"], 15)
        
        # Éco-responsabilité (15 points)
        if route["eco_friendly"]:
            score += 15
        
        # Fiabilité (10 points)
        score += int(route["reliability"] * 10)
        
        return min(100, score)
    
    def _get_route_status(self, score: int) -> str:
        """Statut de la route basé sur le score"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Bon"
        elif score >= 40:
            return "Moyen"
        else:
            return "Faible"
    
    def _get_route_trend(self, route: Dict) -> str:
        """Tendance de la route (amélioration/dégradation)"""
        trends = ["stable", "improving", "declining"]
        weights = [0.6, 0.25, 0.15]  # 60% stable, 25% amélioration, 15% dégradation
        return random.choices(trends, weights=weights)[0]
    
    def _get_route_advantages(self, route: Dict) -> List[str]:
        """Avantages de la route"""
        advantages = []
        
        if route["cost"] == "0€":
            advantages.append("Gratuit")
        if route["eco_friendly"]:
            advantages.append("Éco-responsable")
        if route["comfort"] == "Élevé":
            advantages.append("Confortable")
        if route["reliability"] >= 0.9:
            advantages.append("Très fiable")
        if route["transfers"] == 0:
            advantages.append("Sans correspondance")
        
        return advantages
    
    def _get_route_disadvantages(self, route: Dict) -> List[str]:
        """Inconvénients de la route"""
        disadvantages = []
        
        if route["cost"] != "0€" and float(route["cost"].replace("€", "")) > 20:
            disadvantages.append("Coûteux")
        if not route["eco_friendly"]:
            disadvantages.append("Impact environnemental")
        if route["crowding"] == "Élevé":
            disadvantages.append("Affluence importante")
        if route["transfers"] > 1:
            disadvantages.append("Plusieurs correspondances")
        
        return disadvantages
    
    def _generate_comparison_summary(self, routes: List[Dict]) -> Dict:
        """Résumé de la comparaison des routes"""
        if not routes:
            return {}
        
        best_route = routes[0]
        avg_score = sum(route["score"] for route in routes) / len(routes)
        
        return {
            "best_route": best_route["route"],
            "best_score": best_route["score"],
            "average_score": round(avg_score, 1),
            "total_routes": len(routes),
            "eco_routes_count": sum(1 for route in routes if route["eco_friendly"]),
            "free_routes_count": sum(1 for route in routes if route["cost"] == "0€")
        }
    
    def _generate_recommendations(self, routes: List[Dict]) -> List[str]:
        """Génération de recommandations intelligentes"""
        recommendations = []
        
        if not routes:
            return ["Aucune route disponible"]
        
        best_route = routes[0]
        
        # Recommandation principale
        if best_route["score"] >= 80:
            recommendations.append(f"Route recommandée : {best_route['route']} (Score: {best_route['score']}/100)")
        else:
            recommendations.append(f"Route disponible : {best_route['route']} (Score: {best_route['score']}/100)")
        
        # Recommandations contextuelles
        eco_routes = [r for r in routes if r["eco_friendly"]]
        if eco_routes:
            recommendations.append(f"Options éco-responsables disponibles : {len(eco_routes)} routes")
        
        free_routes = [r for r in routes if r["cost"] == "0€"]
        if free_routes:
            recommendations.append(f"Routes gratuites disponibles : {len(free_routes)} options")
        
        # Recommandation météo/temps
        current_hour = datetime.now().hour
        if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:
            recommendations.append("Heures de pointe : Privilégiez les transports en commun")
        elif 23 <= current_hour or current_hour <= 5:
            recommendations.append("Heures nocturnes : Vérifiez les horaires de transport")
        
        return recommendations
    
    async def get_real_time_updates(self) -> List[Dict]:
        """Mises à jour temps réel mock"""
        updates = [
            {
                "type": "Trafic",
                "message": "Trafic dense sur le périphérique nord-est",
                "severity": "medium",
                "timestamp": datetime.now().isoformat(),
                "affected_routes": ["Taxi/VTC", "Bus"]
            },
            {
                "type": "Météo",
                "message": "Pluie prévue cet après-midi, privilégiez les transports couverts",
                "severity": "low",
                "timestamp": datetime.now().isoformat(),
                "affected_routes": ["Vélo", "Marche"]
            },
            {
                "type": "Événement",
                "message": "Affluence exceptionnelle à Châtelet (événement culturel)",
                "severity": "high",
                "timestamp": datetime.now().isoformat(),
                "affected_routes": ["Métro + Bus", "RER + Métro"]
            }
        ]
        
        return updates

# Instance globale du service Citymapper mock
citymapper_mock_service = CitymapperMockService()

