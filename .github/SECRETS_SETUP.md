# 🔐 Configuration des Secrets GitHub

Ce guide explique comment configurer les secrets GitHub pour le déploiement automatique de Baguette Metro.

## 📋 Secrets Requis

### 🔑 Secrets d'API (Optionnels pour le mode démo)

| Secret | Description | Obligatoire | Exemple |
|--------|-------------|-------------|---------|
| `OPENROUTER_API_KEY` | Clé API OpenRouter pour Mistral AI | Non | `sk-or-v1-...` |
| `GOOGLE_PLACES_API_KEY` | Clé API Google Places | Non | `AIza...` |
| `RATP_API_KEY` | Clé API RATP (si disponible) | Non | `your_ratp_key` |
| `SECRET_KEY` | Clé secrète pour l'application | Oui | `your_secret_key_here` |

### 🐳 Secrets de Déploiement

| Secret | Description | Obligatoire | Exemple |
|--------|-------------|-------------|---------|
| `DOCKER_USERNAME` | Nom d'utilisateur Docker Hub | Non | `your_docker_username` |
| `DOCKER_PASSWORD` | Mot de passe Docker Hub | Non | `your_docker_password` |
| `DOCKER_TOKEN` | Token Docker Hub | Non | `dckr_pat_...` |

## 🛠️ Configuration des Secrets

### Méthode 1: Interface GitHub Web

1. **Aller dans le repository GitHub**
   ```
   https://github.com/[username]/baguette-metro
   ```

2. **Accéder aux paramètres**
   ```
   Settings → Secrets and variables → Actions
   ```

3. **Ajouter chaque secret**
   - Cliquer sur "New repository secret"
   - Nom: `OPENROUTER_API_KEY`
   - Valeur: `sk-or-v1-...`
   - Cliquer sur "Add secret"

### Méthode 2: GitHub CLI

```bash
# Configurer les secrets via CLI
gh secret set OPENROUTER_API_KEY --body "sk-or-v1-..."
gh secret set GOOGLE_PLACES_API_KEY --body "AIza..."
gh secret set SECRET_KEY --body "your_secret_key_here"

# Vérifier les secrets configurés
gh secret list
```

### Méthode 3: Script Automatique

```bash
# Utiliser le script de configuration
./scripts/setup_github_secrets.sh
```

## 🔒 Sécurité

### ✅ Bonnes Pratiques

- **Ne jamais** commiter les clés API dans le code
- **Utiliser** les secrets GitHub pour les déploiements
- **Roter** régulièrement les clés API
- **Limiter** les permissions des clés API
- **Monitorer** l'utilisation des clés

### 🚨 Sécurité des Clés API

#### Google Places API
```json
{
  "restrictions": {
    "api_targets": [
      "places.googleapis.com"
    ],
    "http_referrers": [
      "https://yourdomain.com/*"
    ]
  }
}
```

#### OpenRouter API
- Limiter par IP si possible
- Surveiller l'utilisation quotidienne
- Configurer des alertes de quota

## 🧪 Test des Secrets

### Vérification Locale

```bash
# Tester avec les secrets locaux
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

required_secrets = ['SECRET_KEY']
optional_secrets = ['OPENROUTER_API_KEY', 'GOOGLE_PLACES_API_KEY']

print('🔍 Vérification des secrets...')
for secret in required_secrets:
    if os.getenv(secret):
        print(f'✅ {secret}: Configuré')
    else:
        print(f'❌ {secret}: Manquant (OBLIGATOIRE)')

for secret in optional_secrets:
    if os.getenv(secret):
        print(f'✅ {secret}: Configuré')
    else:
        print(f'⚠️  {secret}: Non configuré (optionnel)')
"
```

### Vérification GitHub Actions

```yaml
# Dans .github/workflows/test-secrets.yml
name: Test Secrets
on: [push, pull_request]

jobs:
  test-secrets:
    runs-on: ubuntu-latest
    steps:
      - name: Test Secret Configuration
        run: |
          if [ -z "$SECRET_KEY" ]; then
            echo "❌ SECRET_KEY manquant"
            exit 1
          fi
          echo "✅ Secrets configurés correctement"
        env:
          SECRET_KEY: ${{ secrets.SECRET_KEY }}
```

## 🚀 Déploiement avec Secrets

### Variables d'Environnement dans Docker

```yaml
# docker-compose.yml
services:
  baguette-metro:
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - GOOGLE_PLACES_API_KEY=${GOOGLE_PLACES_API_KEY}
```

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
- name: Deploy to Production
  run: |
    docker-compose up -d
  env:
    SECRET_KEY: ${{ secrets.SECRET_KEY }}
    OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
    GOOGLE_PLACES_API_KEY: ${{ secrets.GOOGLE_PLACES_API_KEY }}
```

## 📞 Support

En cas de problème avec la configuration des secrets :

1. **Vérifier** la documentation GitHub : https://docs.github.com/en/actions/security-guides/encrypted-secrets
2. **Consulter** les logs GitHub Actions
3. **Tester** localement avec les variables d'environnement
4. **Contacter** l'équipe de développement

---

**⚠️ Important** : Les secrets sont sensibles. Ne les partagez jamais publiquement et supprimez-les immédiatement si compromis.
