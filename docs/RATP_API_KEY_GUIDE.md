# 🔑 Guide Configuration Clé API RATP

## 📋 Vue d'ensemble

La clé API RATP est nécessaire pour accéder aux données temps réel de la RATP (positions des véhicules, trafic, retards).

## 🎯 Sources de Clés API RATP

### 1. **API Pierre Grimaud (Recommandée)**
- **URL :** https://api-ratp.pierre-grimaud.fr/
- **Documentation :** https://api-ratp.pierre-grimaud.fr/v4/
- **Gratuit :** Oui (avec limitations)
- **Inscription :** Non requise pour les endpoints publics

### 2. **API Officielle RATP**
- **URL :** https://data.ratp.fr/
- **Documentation :** https://data.ratp.fr/api/v1/
- **Gratuit :** Oui (données statiques)
- **Inscription :** Non requise

### 3. **APIs Alternatives**
- **Transilien API :** Pour les trains de banlieue
- **Île-de-France Mobilités :** Données régionales
- **APIs privées :** Via partenariats RATP

## 🔐 Configuration de la Clé

### **Méthode 1 : Script Automatique (Recommandée)**

```bash
python setup_ratp_real_api_key.py
```

Le script vous guidera pour :
1. Saisir la clé API (masquée)
2. Confirmer la configuration
3. Tester la validité de la clé
4. Sauvegarder dans les fichiers de configuration

### **Méthode 2 : Configuration Manuelle**

#### **Étape 1 : Obtenir la Clé**
1. Visitez https://api-ratp.pierre-grimaud.fr/
2. Consultez la documentation des endpoints
3. Notez votre clé API (si requise)

#### **Étape 2 : Configurer le Fichier Secrets**

Éditez `.streamlit/secrets.toml` :

```toml
# Clés API existantes...
RATP_API_KEY = "votre_vraie_cle_api_ici"
RATP_BASE_URL = "https://api-ratp.pierre-grimaud.fr/v4"
RATP_COLLECTION_ENABLED = true
```

#### **Étape 3 : Configurer le Fichier .env**

Éditez `.env` :

```env
# Variables existantes...
RATP_API_KEY=votre_vraie_cle_api_ici
RATP_BASE_URL=https://api-ratp.pierre-grimaud.fr/v4
RATP_COLLECTION_ENABLED=true
```

## 🧪 Test de la Configuration

### **Test Automatique**
```bash
python setup_ratp_real_api_key.py
```

### **Test Manuel**
```bash
python -c "
import requests
import toml
from pathlib import Path

# Lecture de la clé
secrets = toml.load('.streamlit/secrets.toml')
api_key = secrets.get('RATP_API_KEY', '')

if api_key:
    response = requests.get('https://api-ratp.pierre-grimaud.fr/v4/lines/metros')
    print(f'Status: {response.status_code}')
    print(f'Données: {len(response.json().get(\"result\", {}).get(\"metros\", []))} lignes')
else:
    print('Aucune clé configurée')
"
```

## 📊 Endpoints Disponibles

### **Endpoints Publics (Sans Clé)**
- `GET /lines/metros` - Liste des lignes de métro
- `GET /lines/buses` - Liste des lignes de bus
- `GET /lines/tramways` - Liste des lignes de tramway
- `GET /stations` - Liste des stations

### **Endpoints Privés (Avec Clé)**
- `GET /traffic` - État du trafic
- `GET /schedules` - Horaires en temps réel
- `GET /disruptions` - Perturbations
- `GET /crowding` - Affluence

## 🔧 Utilisation dans l'Application

### **Dans le Code Python**
```python
import os
import streamlit as st

# Récupération de la clé
ratp_api_key = st.secrets.get("RATP_API_KEY", "")
ratp_base_url = st.secrets.get("RATP_BASE_URL", "https://api-ratp.pierre-grimaud.fr/v4")

# Utilisation
headers = {
    'Authorization': f'Bearer {ratp_api_key}',
    'Content-Type': 'application/json'
}

response = requests.get(f"{ratp_base_url}/traffic", headers=headers)
```

### **Dans l'Interface Streamlit**
```python
# La clé est automatiquement disponible via st.secrets
if st.secrets.get("RATP_API_KEY"):
    st.success("✅ Clé API RATP configurée")
else:
    st.warning("⚠️ Clé API RATP manquante")
```

## 🚨 Sécurité

### **Bonnes Pratiques**
1. **Ne jamais commiter** la clé dans Git
2. **Utiliser getpass** pour la saisie sécurisée
3. **Masquer la clé** dans les logs
4. **Rotation régulière** des clés

### **Fichiers à Protéger**
- `.streamlit/secrets.toml`
- `.env`
- Tout fichier contenant des clés API

### **Variables d'Environnement**
```bash
export RATP_API_KEY="votre_cle_api"
export RATP_BASE_URL="https://api-ratp.pierre-grimaud.fr/v4"
```

## 🔄 Mise à Jour de la Clé

### **Changement de Clé**
1. Exécutez `python setup_ratp_real_api_key.py`
2. Saisissez la nouvelle clé
3. Confirmez le changement
4. Redémarrez l'application

### **Suppression de Clé**
```bash
# Éditer .streamlit/secrets.toml
RATP_API_KEY = ""
```

## 📞 Support

### **Problèmes Courants**
1. **Clé invalide :** Vérifiez la clé sur l'API
2. **Limite de requêtes :** Respectez les quotas
3. **Erreur réseau :** Vérifiez la connectivité
4. **Service indisponible :** Consultez le statut de l'API

### **Ressources**
- **Documentation API :** https://api-ratp.pierre-grimaud.fr/v4/
- **Statut Service :** https://status.ratp.fr/
- **Support RATP :** https://www.ratp.fr/contact

## 🎯 Prochaines Étapes

Après configuration de la clé :
1. **Redémarrez l'API :** `python start_ratp_api.py`
2. **Testez l'interface :** http://localhost:8501
3. **Vérifiez les données :** Positions des véhicules en temps réel
4. **Explorez les fonctionnalités :** Analytics, retards, trafic

---

**Note :** L'API Pierre Grimaud est gratuite et ne nécessite pas d'inscription pour les endpoints publics. Pour les fonctionnalités avancées, une clé API peut être requise.





