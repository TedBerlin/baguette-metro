# 🔐 Guide Complet - SECRET_KEY

## 🎯 **Qu'est-ce que la SECRET_KEY ?**

### 📋 **Définition**
La `SECRET_KEY` est une **clé de sécurité cryptographique** utilisée par l'application Baguette Metro pour :

- **Chiffrer les sessions utilisateur**
- **Signer les cookies de session**
- **Protéger contre les attaques CSRF**
- **Sécuriser l'authentification**
- **Chiffrer les données sensibles**

### 🔑 **Caractéristiques**
- **Longueur** : 64 caractères (recommandé)
- **Complexité** : Mélange de lettres, chiffres et symboles
- **Unicité** : Unique par environnement (dev/prod)
- **Confidentialité** : Jamais partagée ou exposée

---

## 🚀 **Comment Créer une SECRET_KEY ?**

### ✅ **Méthode 1 : Script Automatique (Recommandé)**

```bash
python generate_secret_key.py
```

**Avantages :**
- ✅ Génération sécurisée automatique
- ✅ Mise à jour automatique des fichiers
- ✅ Permissions restrictives appliquées
- ✅ Validation de sécurité

### ✅ **Méthode 2 : Génération Manuelle**

#### 🔧 **Avec Python**
```python
import secrets
import string

# Génération d'une clé complexe
characters = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
secret_key = ''.join(secrets.choice(characters) for _ in range(64))
print(secret_key)
```

#### 🔧 **Avec OpenSSL**
```bash
openssl rand -base64 64
```

#### 🔧 **Avec Node.js**
```javascript
require('crypto').randomBytes(64).toString('base64')
```

---

## 📁 **Où Configurer la SECRET_KEY ?**

### 🎯 **Fichiers de Configuration**

#### 1️⃣ **`.streamlit/secrets.toml`**
```toml
# Secret Key (générée automatiquement)
SECRET_KEY = "}%V7%ot+5f9}FGbaJMeRh;Rh.vJy8=7ZQcyeI0q&,]u-$uCtz$QI}1_(7tV]T!>v"
```

#### 2️⃣ **`.env`**
```env
# Secret Key (générée automatiquement)
SECRET_KEY=}%V7%ot+5f9}FGbaJMeRh;Rh.vJy8=7ZQcyeI0q&,]u-$uCtz$QI}1_(7tV]T!>v
```

#### 3️⃣ **Variables d'environnement système**
```bash
export SECRET_KEY="votre-cle-secrete-ici"
```

---

## 🔒 **Sécurité et Bonnes Pratiques**

### ✅ **À FAIRE**

#### 🔐 **Génération Sécurisée**
- **Utilisez** des générateurs cryptographiques sécurisés
- **Longueur minimale** : 32 caractères (64 recommandé)
- **Complexité** : Mélange de types de caractères
- **Unicité** : Différente pour chaque environnement

#### 🔐 **Stockage Sécurisé**
- **Permissions restrictives** : `chmod 600`
- **Variables d'environnement** en production
- **Chiffrement** des fichiers de configuration
- **Backup sécurisé** des clés

#### 🔐 **Gestion Sécurisée**
- **Rotation régulière** : Tous les 6 mois
- **Monitoring** des accès
- **Audit** des permissions
- **Documentation** des procédures

### ❌ **À ÉVITER**

#### 🚨 **Pratiques Dangereuses**
- **Clés en dur** dans le code source
- **Clés partagées** entre environnements
- **Clés simples** ou prévisibles
- **Clés exposées** dans les logs
- **Clés commitées** dans Git

#### 🚨 **Exemples de Mauvaises Clés**
```python
# ❌ MAUVAIS - Trop simple
SECRET_KEY = "password123"

# ❌ MAUVAIS - Trop court
SECRET_KEY = "abc123"

# ❌ MAUVAIS - Prévisible
SECRET_KEY = "baguette-metro-2024"

# ✅ BON - Complexe et sécurisée
SECRET_KEY = "}%V7%ot+5f9}FGbaJMeRh;Rh.vJy8=7ZQcyeI0q&,]u-$uCtz$QI}1_(7tV]T!>v"
```

---

## 🎯 **Utilisation dans l'Application**

### 🔧 **FastAPI (Backend)**
```python
from fastapi import FastAPI
from fastapi.security import HTTPBearer
import os

app = FastAPI()

# Utilisation de la SECRET_KEY
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY non configurée")

# Configuration de sécurité
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 🔧 **Streamlit (Frontend)**
```python
import streamlit as st
import os

# Récupération de la SECRET_KEY
SECRET_KEY = st.secrets.get("SECRET_KEY")
if not SECRET_KEY:
    st.error("SECRET_KEY non configurée")
    st.stop()

# Utilisation pour la sécurité
st.session_state["secure"] = True
```

### 🔧 **Sessions Sécurisées**
```python
import jwt
from datetime import datetime, timedelta

def create_secure_session(user_id: str, secret_key: str):
    """Crée une session sécurisée"""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")

def verify_secure_session(token: str, secret_key: str):
    """Vérifie une session sécurisée"""
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
```

---

## 🔄 **Rotation des Clés**

### 📅 **Calendrier de Rotation**

#### 🔄 **Fréquence Recommandée**
- **Développement** : À chaque changement majeur
- **Staging** : Tous les 3 mois
- **Production** : Tous les 6 mois
- **Sécurité** : Immédiatement en cas de compromission

#### 🔄 **Procédure de Rotation**

1. **Générer** une nouvelle clé
2. **Sauvegarder** l'ancienne clé
3. **Mettre à jour** les fichiers de configuration
4. **Redémarrer** l'application
5. **Tester** la fonctionnalité
6. **Supprimer** l'ancienne clé

### 🔄 **Script de Rotation**
```bash
#!/bin/bash
# Script de rotation de SECRET_KEY

echo "🔄 Rotation de la SECRET_KEY..."

# 1. Sauvegarde de l'ancienne clé
cp .streamlit/secrets.toml .streamlit/secrets.toml.backup

# 2. Génération de la nouvelle clé
python generate_secret_key.py

# 3. Redémarrage de l'application
python start_app.py

echo "✅ Rotation terminée"
```

---

## 🚨 **Gestion des Incidents**

### 🚨 **Clé Compromise**

#### 🔍 **Signes de Compromission**
- **Accès non autorisés** aux sessions
- **Données sensibles** exposées
- **Erreurs de signature** dans les logs
- **Comportement anormal** de l'application

#### 🚨 **Actions Immédiates**
1. **Révoquer** immédiatement la clé compromise
2. **Générer** une nouvelle clé sécurisée
3. **Mettre à jour** tous les environnements
4. **Redémarrer** toutes les instances
5. **Auditer** les logs d'accès
6. **Notifier** l'équipe de sécurité

### 🚨 **Clé Perdue**

#### 🔍 **Récupération**
1. **Vérifier** les sauvegardes sécurisées
2. **Générer** une nouvelle clé si nécessaire
3. **Mettre à jour** la configuration
4. **Réinitialiser** toutes les sessions utilisateur

---

## 📊 **Monitoring et Audit**

### 📈 **Métriques de Sécurité**

#### 🔍 **Surveillance Continue**
- **Tentatives d'accès** non autorisées
- **Erreurs de signature** de session
- **Utilisation anormale** des clés
- **Temps de rotation** des clés

#### 🔍 **Logs de Sécurité**
```python
import logging

# Configuration des logs de sécurité
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)

# Log des événements de sécurité
def log_security_event(event_type: str, details: dict):
    security_logger.info(f"SECURITY_EVENT: {event_type} - {details}")
```

### 📈 **Alertes Automatiques**

#### 🔔 **Types d'Alertes**
- **Tentative d'accès** à la SECRET_KEY
- **Erreur de signature** répétée
- **Rotation de clé** manquante
- **Compromission** détectée

---

## 🎯 **Environnements**

### 🏗️ **Développement**
```toml
# .streamlit/secrets.toml (dev)
SECRET_KEY = "dev-secret-key-for-testing-only"
```

### 🧪 **Staging**
```toml
# .streamlit/secrets.toml (staging)
SECRET_KEY = "staging-secret-key-2024"
```

### 🚀 **Production**
```toml
# .streamlit/secrets.toml (prod)
SECRET_KEY = "}%V7%ot+5f9}FGbaJMeRh;Rh.vJy8=7ZQcyeI0q&,]u-$uCtz$QI}1_(7tV]T!>v"
```

---

## 📚 **Ressources et Références**

### 🔗 **Documentation Officielle**
- **FastAPI Security** : https://fastapi.tiangolo.com/tutorial/security/
- **Streamlit Secrets** : https://docs.streamlit.io/library/advanced-features/secrets-management
- **Python Secrets** : https://docs.python.org/3/library/secrets.html

### 🔗 **Outils Recommandés**
- **Python secrets** : Génération sécurisée
- **OpenSSL** : Cryptographie avancée
- **JWT** : Tokens sécurisés
- **Hashlib** : Hachage sécurisé

### 🔗 **Bonnes Pratiques**
- **OWASP** : https://owasp.org/
- **NIST Guidelines** : https://www.nist.gov/
- **Security Best Practices** : https://security.stackexchange.com/

---

## 🎉 **Résumé**

### ✅ **Checklist de Sécurité**
- [ ] **SECRET_KEY générée** de manière sécurisée
- [ ] **Longueur suffisante** (64 caractères)
- [ ] **Complexité appropriée** (mélange de caractères)
- [ ] **Stockage sécurisé** (permissions restrictives)
- [ ] **Variables d'environnement** en production
- [ ] **Rotation planifiée** (tous les 6 mois)
- [ ] **Monitoring configuré** (logs et alertes)
- [ ] **Procédures documentées** (incidents et récupération)

### 🚀 **Prêt pour la Production**
Votre application Baguette Metro est maintenant **sécurisée** avec une SECRET_KEY robuste !

---

**Baguette Metro Team** - Guide de sécurité SECRET_KEY

*Dernière mise à jour : Août 2024*





