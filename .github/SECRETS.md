# 🔐 Configuration des Secrets GitHub

Ce document liste tous les secrets nécessaires pour le pipeline CI/CD de Baguette & Métro.

## 📍 Où configurer les secrets

1. Aller sur votre repository GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Cliquer sur **"New repository secret"**

## 🔑 Secrets requis

### 🔧 **Docker Hub**
```
DOCKER_USERNAME=votre_username_dockerhub
DOCKER_PASSWORD=votre_password_dockerhub
```

### 🤖 **OpenRouter API**
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 🗺️ **Google Places API** (optionnel)
```
GOOGLE_PLACES_API_KEY=votre_cle_google_places
```

### 🚇 **RATP API** (optionnel)
```
RATP_GTFS_URL=https://api-ratp.pierre-grimaud.fr/v4
```

### 📊 **Codecov** (optionnel)
```
CODECOV_TOKEN=votre_token_codecov
```

### 🔔 **Notifications** (optionnel)
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=votre_email@gmail.com
EMAIL_PASSWORD=votre_password_app
```

### ☁️ **Déploiement Cloud** (optionnel)
```
AWS_ACCESS_KEY_ID=votre_aws_access_key
AWS_SECRET_ACCESS_KEY=votre_aws_secret_key
AWS_REGION=eu-west-3
GCP_PROJECT_ID=votre_project_id
GCP_SERVICE_ACCOUNT_KEY={"type": "service_account", ...}
AZURE_SUBSCRIPTION_ID=votre_subscription_id
AZURE_TENANT_ID=votre_tenant_id
AZURE_CLIENT_ID=votre_client_id
AZURE_CLIENT_SECRET=votre_client_secret
```

## 🛡️ **Sécurité**

### ✅ **Bonnes pratiques**
- Utilisez des tokens d'accès personnels plutôt que des mots de passe
- Limitez les permissions des tokens au minimum nécessaire
- Régénérez régulièrement les tokens
- Ne committez jamais de secrets dans le code

### ❌ **À éviter**
- Mots de passe en clair
- Tokens avec permissions excessives
- Secrets dans les fichiers de configuration
- Partage de secrets via email/chat

## 🔄 **Rotation des secrets**

### **Recommandé :**
- **Tokens API** : Tous les 90 jours
- **Mots de passe** : Tous les 6 mois
- **Clés SSH** : Tous les ans

### **Procédure de rotation :**
1. Créer le nouveau secret
2. Mettre à jour dans GitHub Secrets
3. Tester le pipeline CI/CD
4. Supprimer l'ancien secret

## 📋 **Vérification**

Pour vérifier que tous les secrets sont configurés :

```bash
# Test local des secrets
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

required_secrets = [
    'OPENROUTER_API_KEY',
    'DOCKER_USERNAME',
    'DOCKER_PASSWORD'
]

for secret in required_secrets:
    value = os.getenv(secret)
    if value:
        print(f'✅ {secret}: Configuré')
    else:
        print(f'❌ {secret}: Manquant')
"
```

## 🚨 **En cas de compromission**

1. **Révoquer immédiatement** le secret compromis
2. **Créer un nouveau secret** avec des permissions minimales
3. **Mettre à jour** dans GitHub Secrets
4. **Vérifier les logs** pour détecter les abus
5. **Notifier l'équipe** si nécessaire

---

**Dernière mise à jour** : 27 août 2025  
**Responsable** : Équipe Baguette & Métro
