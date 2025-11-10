# 🌾 AgriDetect - Système de Détection Intelligent des Maladies des Cultures

![Version](https://img.shields.io/badge/version-1.0.0-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal)
![License](https://img.shields.io/badge/license-MIT-orange)

## 📖 Description

**AgriDetect** est une plateforme d'intelligence artificielle dédiée à la détection et au diagnostic des maladies des cultures agricoles. Le système utilise des modèles de deep learning avancés pour identifier avec précision les pathologies végétales à partir d'images et fournir des recommandations de traitement personnalisées.

### 🎯 Objectifs

- Détecter automatiquement les maladies des plantes par analyse d'images
- Fournir des recommandations de traitement adaptées
- Offrir une assistance en temps réel via un chatbot intelligent
- Centraliser les données sur les maladies agricoles courantes
- Faciliter l'accès aux bonnes pratiques agricoles

## ✨ Fonctionnalités Principales

### 🔍 Détection de Maladies
- Upload d'images de plantes malades
- Analyse par intelligence artificielle
- Identification de la maladie avec niveau de confiance
- Évaluation de la sévérité
- Recommandations de traitement (biologiques et chimiques)
- Conseils de prévention

### 💬 Chatbot Agricole
- Assistant intelligent disponible 24/7
- Réponses en français
- Suggestions contextuelles
- Base de connaissances agricoles complète

### 📊 Tableau de Bord
- Statistiques en temps réel
- Maladies les plus détectées
- Taux de réussite du système
- Liste des maladies courantes par région

### 👤 Gestion des Profils
- Création de profils utilisateurs
- Historique des détections
- Personnalisation des recommandations

## 🏗️ Architecture Technique

### Backend
- **Framework**: FastAPI (Python)
- **Base de données**: PostgreSQL
- **Cache**: Redis
- **IA/ML**: TensorFlow / PyTorch
- **Conteneurisation**: Docker & Docker Compose

### Frontend
- **HTML5** - Structure
- **CSS3** - Design responsive avec variables CSS
- **JavaScript** (Vanilla ES6+) - Logique et interactions
- **Fetch API** - Communication avec le backend

### Infrastructure
- **Serveur Web**: Uvicorn (ASGI)
- **Documentation API**: Swagger UI / ReDoc
- **Gestion BDD**: PgAdmin

## 📦 Installation

### Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- **Docker Desktop** (avec Docker Compose)
- **Python 3.8+**
- **Git Bash** (pour Windows)
- **Navigateur web moderne** (Chrome, Firefox, Safari, Edge)

### Installation Automatique (Recommandée)

1. **Cloner le projet**
```bash
git clone https://github.com/votre-repo/agridetect.git
cd agridetect
```

2. **Lancer le script d'installation**
```bash
chmod +x init_setup.sh
./init_setup.sh
```

Ce script va :
- ✅ Vérifier Docker
- ✅ Créer les répertoires nécessaires
- ✅ Arrêter les anciens services
- ✅ Démarrer PostgreSQL, Redis et PgAdmin
- ✅ Créer l'environnement virtuel Python
- ✅ Installer les dépendances

### Installation Manuelle

#### Étape 1 : Services Docker

```bash
# Démarrer les services
docker-compose up -d

# Vérifier que les conteneurs sont actifs
docker ps
```

#### Étape 2 : Environnement Python

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement (Windows/Git Bash)
source venv/Scripts/activate

# Installer les dépendances
pip install -r requirements.txt
```

#### Étape 3 : Lancer l'API

```bash
# Lancer le serveur
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🚀 Utilisation

### Démarrage Rapide

**Option 1 : Script automatique**
```bash
./start_agridetect.sh
```

**Option 2 : Manuelle**
```bash
# Terminal 1 : Lancer l'API
source venv/Scripts/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 : Serveur web (optionnel)
cd web
python -m http.server 3000
```

### Accès aux Services

| Service | URL | Description |
|---------|-----|-------------|
| **Interface Web** | http://localhost:3000 | Interface utilisateur principale |
| **API Documentation** | http://localhost:8000/docs | Swagger UI interactive |
| **API Alternative** | http://localhost:8000/redoc | Documentation ReDoc |
| **Health Check** | http://localhost:8000/health | Vérification de santé |
| **PgAdmin** | http://localhost:5050 | Gestion PostgreSQL |

## 📱 Guide d'Utilisation

### 1. Détection de Maladie

1. Ouvrez `index.html` ou allez sur http://localhost:3000
2. Cliquez sur "Choisir une image" ou glissez-déposez une photo
3. Sélectionnez une image de plante malade
4. Cliquez sur "Analyser"
5. Consultez les résultats :
   - Nom de la maladie détectée
   - Niveau de confiance (%)
   - Sévérité (faible, modérée, élevée)
   - Culture affectée
   - Traitements recommandés
   - Conseils de prévention

### 2. Chatbot

1. Ouvrez `chat.html`
2. Tapez votre question dans le champ de texte
3. Appuyez sur Entrée ou cliquez sur "Envoyer"
4. Le bot répond instantanément
5. Utilisez les suggestions pour explorer d'autres questions

**Exemples de questions :**
- "Comment traiter le mildiou sur la tomate ?"
- "Quels sont les symptômes de l'oïdium ?"
- "Comment prévenir les maladies fongiques ?"

### 3. Dashboard

1. Ouvrez `dashboard.html`
2. Consultez les statistiques :
   - Nombre total de détections
   - Utilisateurs actifs
   - Types de maladies
   - Taux de réussite
3. Explorez les maladies courantes
4. Visualisez les graphiques

## 🧪 Tests

### Tester l'API avec Swagger UI

1. Ouvrez http://localhost:8000/docs
2. Cliquez sur un endpoint
3. Cliquez sur "Try it out"
4. Entrez les paramètres nécessaires
5. Cliquez sur "Execute"
6. Consultez la réponse

### Tester avec cURL

```bash
# Health Check
curl http://localhost:8000/health

# Détection de maladie
curl -X POST "http://localhost:8000/api/v1/detect-disease" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/chemin/vers/image.jpg"

# Chat
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"message":"Comment traiter le mildiou?","session_id":"test-123"}'
```

## 📁 Structure du Projet

```
AgriDetect/
├── main.py                 # Point d'entrée de l'API
├── requirements.txt        # Dépendances Python
├── docker-compose.yml      # Configuration Docker
├── init_setup.sh          # Script d'installation
├── start_agridetect.sh    # Script de démarrage
├── stop_agridetect.sh     # Script d'arrêt
│
├── app/                    # Code source de l'application
│   ├── __init__.py
│   ├── models/            # Modèles de données
│   ├── routes/            # Routes API
│   ├── services/          # Logique métier
│   └── utils/             # Utilitaires
│
├── web/                    # Interface web
│   ├── index.html         # Page détection
│   ├── chat.html          # Page chat
│   ├── dashboard.html     # Page statistiques
│   ├── style.css          # Styles
│   └── app.js             # Logique JavaScript
│
├── data/                   # Données
│   ├── postgres/          # Données PostgreSQL
│   └── redis/             # Données Redis
│
└── docs/                   # Documentation
    ├── README.md          # Documentation principale
    ├── README_WEB.md      # Documentation interface web
    └── API.md             # Documentation API
```

## 🔧 Configuration

### Variables d'Environnement

Créez un fichier `.env` à la racine :

```env
# Database
POSTGRES_USER=agridetect
POSTGRES_PASSWORD=password123
POSTGRES_DB=agridetect_db
DATABASE_URL=postgresql://agridetect:password123@localhost:5432/agridetect_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# API
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=votre-cle-secrete-ici

# PgAdmin
PGADMIN_DEFAULT_EMAIL=admin@agridetect.com
PGADMIN_DEFAULT_PASSWORD=admin123
```

### Configuration Docker Compose

Le fichier `docker-compose.yml` configure :
- PostgreSQL (port 5432)
- Redis (port 6379)
- PgAdmin (port 5050)

## 🐛 Dépannage

### Problème : Docker n'est pas disponible

**Solution :**
- Installez Docker Desktop
- Démarrez Docker Desktop
- Vérifiez avec `docker --version`

### Problème : Port déjà utilisé

**Solution :**
```bash
# Identifier le processus
lsof -i :8000

# Arrêter le processus
kill -9 <PID>
```

### Problème : Erreur de connexion à l'API

**Solution :**
1. Vérifiez que l'API est lancée
2. Vérifiez l'URL dans `app.js`
3. Consultez les logs : `tail -f api.log`

### Problème : Les dépendances Python ne s'installent pas

**Solution :**
```bash
# Mettre à jour pip
python -m pip install --upgrade pip

# Installer avec des flags spécifiques
pip install -r requirements.txt --break-system-packages
```

## 📊 API Endpoints

### Détection

- `POST /api/v1/detect-disease` - Détecter une maladie
- `GET /api/v1/diseases/common` - Liste des maladies courantes
- `GET /api/v1/treatments/{disease_id}` - Traitements pour une maladie

### Chat

- `POST /api/v1/chat` - Envoyer un message au bot

### Analyse

- `POST /api/v1/analyze-crop` - Analyser une culture

### Statistiques

- `GET /api/v1/statistics/dashboard` - Statistiques générales

### Utilisateur

- `POST /api/v1/user/profile` - Créer un profil
- `GET /api/v1/user/profile/{user_id}` - Obtenir un profil

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créez une branche (`git checkout -b feature/NouvelleFonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/NouvelleFonctionnalite`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Auteurs

**Projet de Fin d'Étude - 2025**
- Cours DIT / Développement d'Applications

## 📞 Support

Pour toute question ou problème :
- 📧 Email : support@agridetect.com
- 📚 Documentation : http://localhost:8000/docs
- 🐛 Issues : [GitHub Issues](https://github.com/votre-repo/agridetect/issues)

## 🙏 Remerciements

- TensorFlow / PyTorch pour les modèles d'IA
- FastAPI pour le framework backend
- Docker pour la conteneurisation
- La communauté open-source

---

**Made with 💚 for Agriculture**

🌾 AgriDetect v1.0.0 - Protéger les cultures, nourrir le monde
#   A g r i D e t e c _ t e s t  
 