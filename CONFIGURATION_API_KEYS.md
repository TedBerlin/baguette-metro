# 🔑 Configuration des Vraies Clés API

## 🚀 Guide Rapide - Baguette Metro

### ✅ **Étape 1 : Obtenir vos Clés API**

#### 🔑 **OpenRouter API Key** (Recommandé)
- **URL** : https://openrouter.ai/keys
- **Format** : `sk-or-v1-...`
- **Usage** : Claude 3.5 Sonnet pour l'assistant IA
- **Coût** : ~$0.003/1K tokens

#### 🔑 **OpenAI API Key** (Alternative)
- **URL** : https://platform.openai.com/api-keys
- **Format** : `sk-...`
- **Usage** : GPT-4o-mini pour l'assistant IA
- **Coût** : ~$0.00015/1K tokens

#### 🔑 **Google Places API Key** (Optionnel)
- **URL** : https://console.cloud.google.com/
- **Format** : `AIza...`
- **Usage** : Géolocalisation des boulangeries
- **Coût** : Gratuit jusqu'à 1000 requêtes/mois

#### 🔑 **RATP API Key** (Optionnel)
- **URL** : https://api.ratp.fr/
- **Format** : Variable
- **Usage** : Données temps réel RATP
- **Coût** : Variable selon le plan

---

### ✅ **Étape 2 : Configurer les Clés**

#### 📝 **Méthode 1 : Édition Manuelle**

1. **Ouvrez le fichier** `.streamlit/secrets.toml`
2. **Remplacez** les valeurs par vos vraies clés :

```toml
# OpenRouter API Key
OPENROUTER_API_KEY = "sk-or-v1-votre-vraie-cle-ici"

# OpenAI API Key
OPENAI_API_KEY = "sk-votre-vraie-cle-ici"

# Google Places API Key
GOOGLE_PLACES_API_KEY = "AIza-votre-vraie-cle-ici"

# RATP API Key
RATP_API_KEY = "votre-cle-ratp-ici"

# Secret Key
SECRET_KEY = "votre-cle-secrete-ici"
```

3. **Sauvegardez** le fichier

#### 📝 **Méthode 2 : Fichier .env**

1. **Ouvrez le fichier** `.env`
2. **Remplacez** les valeurs par vos vraies clés :

```env
OPENROUTER_API_KEY=sk-or-v1-votre-vraie-cle-ici
OPENAI_API_KEY=sk-votre-vraie-cle-ici
GOOGLE_PLACES_API_KEY=AIza-votre-vraie-cle-ici
RATP_API_KEY=votre-cle-ratp-ici
SECRET_KEY=votre-cle-secrete-ici
```

3. **Sauvegardez** le fichier

---

### ✅ **Étape 3 : Tester la Configuration**

#### 🧪 **Test Automatique**
```bash
python test_final_integration.py
```

#### 🧪 **Test Manuel**
1. **Redémarrez l'application** :
   ```bash
   python start_app.py
   ```

2. **Ouvrez l'interface** :
   ```
   http://localhost:8501
   ```

3. **Testez l'assistant IA** :
   - Posez une question en français
   - Vérifiez la réponse
   - Testez le multilingue (EN/JA)

---

### ✅ **Étape 4 : Validation**

#### 🎯 **Points de Contrôle**
- [ ] **Assistant IA répond** correctement
- [ ] **Multilingue fonctionne** (FR/EN/JA)
- [ ] **Calcul ETA** fonctionne
- [ ] **Réponses rapides** disponibles
- [ ] **Performance** < 2ms
- [ ] **Pas d'erreurs** dans les logs

#### 🔍 **Vérification des Logs**
```bash
# Vérifiez les logs de l'API
curl http://0.0.0.0:8000/health

# Vérifiez les logs de l'interface
curl http://localhost:8501
```

---

### ⚠️ **Sécurité**

#### 🔒 **Bonnes Pratiques**
- **Ne partagez jamais** vos clés API
- **Utilisez des variables d'environnement** en production
- **Limitez les permissions** des clés API
- **Surveillez l'utilisation** et les coûts
- **Faites des sauvegardes** de vos clés

#### 🚨 **En Cas de Problème**
1. **Vérifiez le format** des clés
2. **Testez les clés** individuellement
3. **Consultez les logs** d'erreur
4. **Vérifiez les quotas** et limites
5. **Contactez le support** si nécessaire

---

### 💰 **Coûts Estimés**

#### 📊 **Utilisation Typique**
- **1000 questions/jour** : ~$1-3/mois
- **10000 questions/jour** : ~$10-30/mois
- **100000 questions/jour** : ~$100-300/mois

#### 🎯 **Optimisation des Coûts**
- **Utilisez des réponses rapides** quand possible
- **Limitez la longueur** des réponses
- **Mettez en cache** les réponses fréquentes
- **Surveillez l'utilisation** en temps réel

---

### 🚀 **Lancement en Production**

#### ✅ **Checklist Finale**
- [ ] **Toutes les clés API** configurées
- [ ] **Tests de fonctionnalité** réussis
- [ ] **Performance** validée
- [ ] **Sécurité** vérifiée
- [ ] **Monitoring** en place
- [ ] **Backup** configuré

#### 🎉 **Prêt pour le Lancement !**
```bash
# Démarrage en production
python start_app.py --env production

# Ou avec Docker
docker-compose up -d
```

---

**Baguette Metro Team** - Guide de configuration API

*Dernière mise à jour : Août 2024*





