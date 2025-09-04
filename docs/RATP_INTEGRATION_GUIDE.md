# 🚇 Guide d'Intégration RATP

## 🎯 **Vue d'Ensemble**

L'intégration RATP de Baguette Metro combine **trois sources de données** pour optimiser les trajets :

### 📊 **Sources de Données**

#### 1️⃣ **GTFS-RT (General Transit Feed Specification - Real Time)**
- **Positions temps réel** des véhicules (métro, bus, tram)
- **Mise à jour** toutes les 30 secondes
- **Données** : latitude, longitude, vitesse, direction, niveau de congestion

#### 2️⃣ **PRIM (Programme de Recherche et d'Innovation en Mobilité)**
- **Fréquentation des stations** en temps réel
- **Données de flux** de passagers
- **Périodes** : peak, off-peak, night

#### 3️⃣ **Retards Historiques**
- **Base de données** des retards passés
- **Analyses prédictives** pour optimiser les trajets
- **Causes** : incidents, affluence, maintenance, météo

---

## 🚀 **Architecture Technique**

### 🔧 **Composants**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GTFS-RT API   │    │   PRIM API      │    │   Historique    │
│   (Positions)   │    │   (Fréquen.)    │    │   (Retards)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ RATP Integration│
                    │   (Module)      │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   SQLite DB     │
                    │   (Cache)       │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   FastAPI       │
                    │   (Routes)      │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Streamlit     │
                    │   (Interface)   │
                    └─────────────────┘
```

### 📁 **Structure des Fichiers**

```
src/
├── data/
│   └── ratp_data_integration.py    # Module principal RATP
├── api/
│   └── ratp_routes.py              # Routes API RATP
└── ...

data/
├── cache/
│   └── ratp/                       # Cache des données
│       ├── gtfs_rt_cache.json
│       └── prim_cache.json
└── ratp_data.db                    # Base SQLite
```

---

## 🔧 **Installation et Configuration**

### ✅ **Prérequis**

```bash
# Dépendances Python
pip install aiohttp pandas numpy sqlite3

# Variables d'environnement
export RATP_API_KEY="votre_cle_ratp_ici"
```

### ✅ **Configuration**

#### 📝 **1. Clé API RATP**
```bash
# Dans .env
RATP_API_KEY=votre_cle_ratp_ici

# Dans .streamlit/secrets.toml
RATP_API_KEY = "votre_cle_ratp_ici"
```

#### 📝 **2. URLs des APIs**
```python
# URLs par défaut (configurables)
GTFS_RT_URL = "https://api-ratp.pierre-grimaud.fr/v4/gtfs/rt"
PRIM_URL = "https://api-ratp.pierre-grimaud.fr/v4/prim"
```

#### 📝 **3. Intervalles de mise à jour**
```python
UPDATE_INTERVAL = 30      # secondes
CACHE_TTL = 300          # secondes (5 minutes)
```

---

## 🎯 **Utilisation**

### 🔧 **Initialisation**

```python
from src.data.ratp_data_integration import RATPDataIntegration

# Initialisation
ratp = RATPDataIntegration(api_key="votre_cle")

# Chargement des données historiques
ratp.load_historical_delays()
```

### 📡 **Collecte de Données**

#### 🚇 **GTFS-RT (Positions)**
```python
# Récupération asynchrone
vehicles = await ratp.fetch_gtfs_rt_data()

# Exemple de véhicule
vehicle = GTFSVehicle(
    vehicle_id="metro_001",
    trip_id="trip_123",
    route_id="1",
    latitude=48.8566,
    longitude=2.3522,
    bearing=45.0,
    speed=25.0,
    timestamp=1640995200,
    congestion_level="LOW",
    occupancy_status="MANY_SEATS_AVAILABLE"
)
```

#### 👥 **PRIM (Fréquentation)**
```python
# Récupération asynchrone
stations = await ratp.fetch_prim_data()

# Exemple de station
station = PRIMStation(
    station_id="chatelet",
    station_name="Châtelet",
    line_id="1",
    passenger_count=1250,
    timestamp=datetime.now(),
    direction="La Défense",
    period="peak"
)
```

#### 📊 **Retards Historiques**
```python
# Chargement des retards
delays = ratp.load_historical_delays()

# Exemple de retard
delay = HistoricalDelay(
    line_id="1",
    station_id="chatelet",
    delay_minutes=8,
    date=datetime.now(),
    cause="Incident technique",
    impact_level="medium"
)
```

### 🔍 **Requêtes et Analyses**

#### 🚗 **Positions des Véhicules**
```python
# Tous les véhicules
vehicles = ratp.get_vehicle_positions()

# Véhicules d'une ligne spécifique
vehicles_line_1 = ratp.get_vehicle_positions(route_id="1")
```

#### 🏢 **Congestion des Stations**
```python
# Niveau de congestion d'une station
congestion = ratp.get_station_congestion("chatelet")

# Résultat
{
    "station_id": "chatelet",
    "congestion_level": "HIGH",
    "avg_passengers": 1250,
    "max_passengers": 1800,
    "avg_delay_minutes": 5.2,
    "delay_count": 3
}
```

#### 📈 **Performance des Lignes**
```python
# Performance d'une ligne
performance = ratp.get_line_performance("1")

# Résultat
{
    "line_id": "1",
    "performance": "GOOD",
    "avg_delay_minutes": 3.5,
    "total_delays": 12,
    "high_impact_delays": 2,
    "active_vehicles": 45
}
```

---

## 🌐 **API Endpoints**

### 🔍 **Health Check**
```http
GET /ratp/health
```

**Réponse :**
```json
{
    "status": "healthy",
    "service": "RATP Data Integration",
    "timestamp": "2024-08-27T10:30:00",
    "features": [
        "GTFS-RT (positions temps réel)",
        "PRIM (fréquentation stations)",
        "Retards historiques",
        "Analyses de performance"
    ]
}
```

### 🚗 **Positions des Véhicules**
```http
GET /ratp/vehicles?route_id=1&limit=100
```

**Paramètres :**
- `route_id` (optionnel) : ID de la ligne
- `limit` (optionnel) : Nombre maximum de véhicules (1-1000)

### 🏢 **Congestion des Stations**
```http
GET /ratp/stations/{station_id}/congestion
```

### 📈 **Performance des Lignes**
```http
GET /ratp/lines/{line_id}/performance
```

### ⏰ **Retards Récents**
```http
GET /ratp/delays?line_id=1&days=7
```

**Paramètres :**
- `line_id` (optionnel) : ID de la ligne
- `station_id` (optionnel) : ID de la station
- `days` (optionnel) : Nombre de jours à analyser (1-30)

### 📊 **Analytics Summary**
```http
GET /ratp/analytics/summary
```

### 🔄 **Refresh des Données**
```http
POST /ratp/refresh
```

### 📁 **Statut du Cache**
```http
GET /ratp/cache/status
```

---

## 🗄️ **Base de Données**

### 📊 **Tables**

#### 🚗 **gtfs_vehicles**
```sql
CREATE TABLE gtfs_vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id TEXT,
    trip_id TEXT,
    route_id TEXT,
    latitude REAL,
    longitude REAL,
    bearing REAL,
    speed REAL,
    timestamp INTEGER,
    congestion_level TEXT,
    occupancy_status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 👥 **prim_stations**
```sql
CREATE TABLE prim_stations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    station_id TEXT,
    station_name TEXT,
    line_id TEXT,
    passenger_count INTEGER,
    timestamp TIMESTAMP,
    direction TEXT,
    period TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### ⏰ **historical_delays**
```sql
CREATE TABLE historical_delays (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    line_id TEXT,
    station_id TEXT,
    delay_minutes INTEGER,
    date TIMESTAMP,
    cause TEXT,
    impact_level TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 🔍 **Index de Performance**
```sql
CREATE INDEX idx_gtfs_vehicle_id ON gtfs_vehicles(vehicle_id);
CREATE INDEX idx_gtfs_timestamp ON gtfs_vehicles(timestamp);
CREATE INDEX idx_prim_station_id ON prim_stations(station_id);
CREATE INDEX idx_prim_timestamp ON prim_stations(timestamp);
CREATE INDEX idx_delays_line_id ON historical_delays(line_id);
CREATE INDEX idx_delays_date ON historical_delays(date);
```

---

## 🧪 **Tests et Validation**

### ✅ **Test Automatique**
```bash
python test_ratp_integration.py
```

### ✅ **Test Manuel**
```bash
# Test health check
curl http://0.0.0.0:8000/ratp/health

# Test positions véhicules
curl http://0.0.0.0:8000/ratp/vehicles

# Test congestion station
curl http://0.0.0.0:8000/ratp/stations/chatelet/congestion

# Test performance ligne
curl http://0.0.0.0:8000/ratp/lines/1/performance
```

### ✅ **Validation des Données**
```python
# Vérification de la qualité des données
def validate_gtfs_data(vehicles):
    for vehicle in vehicles:
        assert -90 <= vehicle.latitude <= 90
        assert -180 <= vehicle.longitude <= 180
        assert vehicle.speed >= 0
        assert vehicle.timestamp > 0

def validate_prim_data(stations):
    for station in stations:
        assert station.passenger_count >= 0
        assert station.period in ["peak", "off_peak", "night"]
```

---

## 📈 **Monitoring et Performance**

### 📊 **Métriques Clés**

#### ⚡ **Performance**
- **Temps de réponse API** : < 500ms
- **Fréquence de mise à jour** : 30 secondes
- **Taille du cache** : < 100MB
- **Disponibilité** : 99.9%

#### 📈 **Qualité des Données**
- **Couverture GTFS-RT** : > 95%
- **Couverture PRIM** : > 80%
- **Précision des positions** : ±10m
- **Actualité des données** : < 1 minute

### 🔍 **Logs et Debugging**

#### 📝 **Logs d'Application**
```python
import logging

logger = logging.getLogger(__name__)
logger.info(f"GTFS-RT: {len(vehicles)} véhicules récupérés")
logger.warning(f"Erreur {response.status} pour {endpoint}")
logger.error(f"Erreur récupération GTFS-RT: {e}")
```

#### 🔍 **Monitoring en Temps Réel**
```python
# Métriques de performance
performance_metrics = {
    "api_response_time": response_time,
    "data_freshness": data_age,
    "cache_hit_rate": cache_hits / total_requests,
    "error_rate": errors / total_requests
}
```

---

## 🚨 **Gestion d'Erreurs**

### ⚠️ **Erreurs Courantes**

#### 🔌 **Erreur de Connexion**
```python
try:
    vehicles = await ratp.fetch_gtfs_rt_data()
except aiohttp.ClientError as e:
    logger.error(f"Erreur de connexion: {e}")
    # Utiliser les données en cache
    vehicles = ratp.get_cached_vehicles()
```

#### 📡 **Erreur API**
```python
if response.status_code != 200:
    logger.warning(f"Erreur API {response.status_code}")
    # Retry avec backoff exponentiel
    await asyncio.sleep(retry_delay)
```

#### 💾 **Erreur Base de Données**
```python
try:
    ratp._save_gtfs_to_db(vehicles)
except sqlite3.Error as e:
    logger.error(f"Erreur base de données: {e}")
    # Sauvegarde en cache de secours
    ratp._save_gtfs_cache(vehicles)
```

### 🔄 **Stratégies de Récupération**

#### 📦 **Cache de Secours**
```python
def get_vehicle_positions_with_fallback(self, route_id=None):
    try:
        return self.get_vehicle_positions(route_id)
    except Exception:
        return self.get_cached_vehicles(route_id)
```

#### 🔄 **Retry Automatique**
```python
async def fetch_with_retry(self, endpoint, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await self.fetch_data(endpoint)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            await asyncio.sleep(2 ** attempt)  # Backoff exponentiel
```

---

## 🔮 **Évolutions Futures**

### 🚀 **Fonctionnalités Planifiées**

#### 🤖 **IA Prédictive**
- **Prédiction des retards** basée sur l'historique
- **Optimisation des trajets** en temps réel
- **Alertes intelligentes** pour les incidents

#### 📱 **Notifications Temps Réel**
- **WebSockets** pour les mises à jour en temps réel
- **Push notifications** pour les incidents
- **Alertes personnalisées** par ligne/station

#### 🗺️ **Visualisation Avancée**
- **Cartes interactives** des positions
- **Graphiques de performance** en temps réel
- **Heatmaps** de congestion

### 🔧 **Améliorations Techniques**

#### ⚡ **Performance**
- **Cache Redis** pour les données fréquentes
- **CDN** pour les données statiques
- **Load balancing** pour les requêtes

#### 🔒 **Sécurité**
- **Authentification** des requêtes API
- **Chiffrement** des données sensibles
- **Rate limiting** pour éviter les abus

#### 📊 **Analytics**
- **Machine Learning** pour la prédiction
- **Big Data** pour l'analyse historique
- **Real-time analytics** pour les insights

---

## 📚 **Ressources et Références**

### 🔗 **Documentation Officielle**
- **GTFS-RT** : https://developers.google.com/transit/gtfs-realtime
- **RATP API** : https://api-ratp.pierre-grimaud.fr/
- **PRIM** : https://prim.ratp.fr/

### 🔗 **Outils et Bibliothèques**
- **aiohttp** : Client HTTP asynchrone
- **pandas** : Manipulation de données
- **sqlite3** : Base de données légère
- **FastAPI** : Framework API moderne

### 🔗 **Standards**
- **GTFS** : General Transit Feed Specification
- **GTFS-RT** : GTFS Real-Time
- **REST API** : Architecture API
- **JSON** : Format de données

---

## 🎉 **Conclusion**

L'intégration RATP de Baguette Metro offre une **solution complète** pour :

- ✅ **Collecte temps réel** des données de transport
- ✅ **Analyse prédictive** des performances
- ✅ **Optimisation intelligente** des trajets
- ✅ **Interface utilisateur** moderne et intuitive

**L'application est maintenant prête pour une utilisation en production avec des données RATP complètes !** 🚀

---

**Baguette Metro Team** - Guide d'intégration RATP

*Dernière mise à jour : Août 2024*





