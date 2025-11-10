# 📱 AgriDetect - Guide de Développement Complet

## Table des matières
1. [Vue d'ensemble](#vue-densemble)
2. [Architecture technique](#architecture-technique)
3. [Installation et configuration](#installation-et-configuration)
4. [Développement](#développement)
5. [Déploiement](#déploiement)
6. [Tests](#tests)
7. [Maintenance](#maintenance)
8. [Roadmap](#roadmap)

---

## 🌍 Vue d'ensemble

### Description du projet
AgriDetect est une application mobile basée sur l'intelligence artificielle qui permet aux agriculteurs sénégalais de détecter précocement les maladies de leurs cultures. L'application utilise la vision par ordinateur pour analyser les photos de feuilles et propose des traitements adaptés dans trois langues locales.

### Objectifs principaux
- 🎯 Réduire les pertes agricoles de 30-40%
- 🌱 Améliorer la productivité des cultures
- 💬 Offrir une assistance multilingue (Français, Wolof, Pulaar)
- 🌿 Promouvoir les traitements biologiques
- 📊 Fournir des données analytiques pour l'agriculture

### Utilisateurs cibles
- Petits agriculteurs
- Coopératives agricoles
- Agents de vulgarisation agricole
- Organisations agricoles

---

## 🏗️ Architecture technique

### Stack technologique

#### Frontend Mobile
- **Framework**: React Native avec Expo
- **State Management**: Context API + Hooks
- **Navigation**: React Navigation
- **UI Components**: React Native Paper
- **Localisation**: i18n-js
- **Storage**: AsyncStorage

#### Backend API
- **Framework**: FastAPI (Python 3.10+)
- **Base de données**: PostgreSQL 15
- **Cache**: Redis
- **ORM**: SQLAlchemy
- **Authentication**: JWT

#### Intelligence Artificielle
- **Vision**: TensorFlow/Keras avec MobileNetV2
- **NLP**: LangChain + Transformers
- **Modèles**: CNN pour la détection, GPT pour le chatbot

#### Infrastructure
- **Conteneurisation**: Docker
- **Orchestration**: Docker Compose
- **Cloud**: AWS/GCP
- **CDN**: CloudFront/Cloud CDN
- **Monitoring**: Sentry + Prometheus

### Architecture des composants

```
┌─────────────────────────────────────────┐
│           Application Mobile            │
│         (React Native + Expo)           │
└────────────────┬───────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│            API Gateway                  │
│              (Nginx)                    │
└────────────────┬───────────────────────┘
                 │
        ┌────────┴────────┬──────────────┐
        ▼                 ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  FastAPI     │ │   ML Models   │ │    Redis     │
│   Backend    │ │  (TensorFlow) │ │    Cache     │
└──────┬───────┘ └──────────────┘ └──────────────┘
       │
       ▼
┌──────────────┐
│  PostgreSQL  │
│   Database   │
└──────────────┘
```

---

## 🚀 Installation et configuration

### Prérequis
- Node.js 18+ et npm/yarn
- Python 3.10+
- Docker et Docker Compose
- PostgreSQL 15
- Redis 7
- Git

### Installation locale

#### 1. Cloner le repository
```bash
git clone https://github.com/votre-org/agri-detect-app.git
cd agri-detect-app
```

#### 2. Backend - Installation
```bash
# Créer un environnement virtuel
cd backend
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Variables d'environnement
cp .env.example .env
# Éditer .env avec vos configurations

# Initialiser la base de données
alembic upgrade head

# Lancer le serveur de développement
uvicorn main:app --reload --port 8000
```

#### 3. Mobile - Installation
```bash
cd mobile
npm install
# ou
yarn install

# Configuration Expo
expo login

# Lancer l'application
npm start
# ou
expo start
```

#### 4. Docker - Installation complète
```bash
# À la racine du projet
docker-compose up -d

# Vérifier les services
docker-compose ps

# Voir les logs
docker-compose logs -f backend
```

### Configuration des variables d'environnement

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/agridetect
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# ML Models
MODEL_PATH=/app/data/models
UPLOAD_PATH=/app/data/uploads

# External APIs
OPENAI_API_KEY=your-openai-key
WEATHER_API_KEY=your-weather-api-key

# Firebase (Notifications)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=your-private-key

# Monitoring
SENTRY_DSN=your-sentry-dsn

# Environment
ENVIRONMENT=development
DEBUG=True
```

#### Mobile (config.js)
```javascript
export default {
  API_URL: process.env.API_URL || 'http://localhost:8000',
  GOOGLE_MAPS_API_KEY: 'your-key',
  SENTRY_DSN: 'your-sentry-dsn',
};
```

---

## 💻 Développement

### Structure du projet
```
agri-detect-app/
├── mobile/                 # Application React Native
│   ├── src/
│   │   ├── components/    # Composants réutilisables
│   │   ├── screens/       # Écrans de l'app
│   │   ├── services/      # Services API
│   │   ├── utils/         # Utilitaires
│   │   └── locales/       # Traductions
│   └── assets/            # Images, fonts
├── backend/               # API Backend
│   ├── api/              # Endpoints
│   ├── models/           # Modèles SQLAlchemy
│   ├── services/         # Logique métier
│   ├── ml/               # Services ML
│   └── utils/            # Utilitaires
├── ml-models/            # Modèles IA
│   ├── disease_detector/ # Détection des maladies
│   ├── chatbot/          # Assistant multilingue
│   └── training/         # Scripts d'entraînement
├── database/             # Scripts SQL
├── docs/                 # Documentation
├── tests/                # Tests
└── deployment/           # Configs déploiement
```

### Workflow de développement

#### 1. Créer une branche feature
```bash
git checkout -b feature/nom-feature
```

#### 2. Développement avec hot-reload
```bash
# Backend
uvicorn main:app --reload

# Mobile
expo start --clear
```

#### 3. Tests
```bash
# Backend
pytest tests/

# Mobile
npm test
```

#### 4. Commit et PR
```bash
git add .
git commit -m "feat: description de la feature"
git push origin feature/nom-feature
```

### Standards de code

#### Python (Backend)
- PEP 8 avec Black formatter
- Type hints obligatoires
- Docstrings pour toutes les fonctions
- Tests unitaires avec pytest

#### JavaScript (Mobile)
- ESLint + Prettier
- Functional components avec Hooks
- PropTypes ou TypeScript
- Tests avec Jest + Testing Library

### Endpoints API principaux

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/v1/detect-disease` | POST | Détection de maladie |
| `/api/v1/chat` | POST | Chat multilingue |
| `/api/v1/treatments/{disease_id}` | GET | Traitements pour une maladie |
| `/api/v1/user/profile` | GET/POST | Profil utilisateur |
| `/api/v1/diseases/common` | GET | Maladies communes |
| `/api/v1/statistics/dashboard` | GET | Statistiques |

---

## 🚢 Déploiement

### Déploiement avec Docker

#### Build des images
```bash
# Backend
docker build -t agridetect-backend .

# Push vers registry
docker tag agridetect-backend:latest your-registry/agridetect-backend:latest
docker push your-registry/agridetect-backend:latest
```

#### Déploiement sur AWS

1. **EC2 Instance**
```bash
# SSH vers l'instance
ssh -i key.pem ubuntu@your-instance

# Cloner et lancer
git clone repo-url
cd agri-detect-app
docker-compose up -d
```

2. **ECS avec Fargate**
- Créer task definition
- Configurer service ECS
- Setup Application Load Balancer

3. **RDS pour PostgreSQL**
- Instance db.t3.medium
- Multi-AZ pour la production
- Automated backups

### Déploiement Mobile

#### Android (Google Play)
```bash
# Build APK
expo build:android

# Build App Bundle
expo build:android -t app-bundle

# Upload vers Play Console
```

#### iOS (App Store)
```bash
# Build IPA
expo build:ios

# Upload avec Transporter
```

### CI/CD avec GitHub Actions

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # Deploy commands
```

---

## 🧪 Tests

### Tests Backend

#### Unit Tests
```python
# test_disease_detection.py
def test_detect_disease():
    response = client.post("/api/v1/detect-disease", files={"file": image})
    assert response.status_code == 200
    assert "disease_name" in response.json()
```

#### Integration Tests
```python
def test_full_detection_flow():
    # Upload image
    # Get detection
    # Get treatments
    # Save feedback
```

### Tests Mobile

#### Component Tests
```javascript
test('renders disease detection screen', () => {
  render(<DiseaseDetection />);
  expect(screen.getByText('Prendre une photo')).toBeTruthy();
});
```

#### E2E Tests avec Detox
```javascript
describe('Disease Detection Flow', () => {
  it('should detect disease from photo', async () => {
    await element(by.id('take-photo-btn')).tap();
    await element(by.id('analyze-btn')).tap();
    await expect(element(by.id('results'))).toBeVisible();
  });
});
```

### Performance Tests

```bash
# Load testing avec Locust
locust -f locustfile.py --host=http://localhost:8000
```

---

## 🔧 Maintenance

### Monitoring

#### Métriques à surveiller
- Temps de réponse API < 200ms
- Accuracy du modèle > 85%
- Uptime > 99.9%
- Utilisation CPU/RAM
- Taille de la base de données

#### Outils de monitoring
- **APM**: Sentry, New Relic
- **Logs**: ELK Stack
- **Métriques**: Prometheus + Grafana
- **Alertes**: PagerDuty

### Backup et récupération

#### Base de données
```bash
# Backup quotidien
pg_dump agridetect > backup_$(date +%Y%m%d).sql

# Restore
psql agridetect < backup_20240115.sql
```

#### Modèles ML
- Versionning avec DVC
- Stockage sur S3
- A/B testing pour nouveaux modèles

### Mise à jour des modèles

1. **Collecte de nouvelles données**
2. **Réentraînement**
```python
python train_model.py --data new_data/ --epochs 50
```
3. **Validation**
```python
python validate_model.py --model new_model.h5
```
4. **Déploiement progressif**

---

## 📈 Roadmap

### Phase 1 (Q1 2024) ✅
- [x] MVP avec détection de base
- [x] Support 3 langues
- [x] 5 maladies principales
- [x] Déploiement beta

### Phase 2 (Q2 2024) 🚧
- [ ] 15 nouvelles maladies
- [ ] Prédictions météo intégrées
- [ ] Mode hors ligne
- [ ] Marketplace de produits

### Phase 3 (Q3 2024) 📋
- [ ] IoT sensors integration
- [ ] Drone imagery support
- [ ] Community features
- [ ] Expert consultation

### Phase 4 (Q4 2024) 🔮
- [ ] Expansion régionale (Afrique de l'Ouest)
- [ ] AI yield prediction
- [ ] Blockchain traceability
- [ ] B2B platform

---

## 📞 Support et Contact

### Équipe de développement
- **Lead Developer**: [contact]
- **ML Engineer**: [contact]
- **Product Manager**: [contact]

### Ressources
- Documentation API: `/api/docs`
- Wiki: [lien wiki]
- Issues: GitHub Issues
- Slack: #agridetect-dev

### Contribution
1. Fork le projet
2. Créer une feature branch
3. Commit les changements
4. Push vers la branch
5. Ouvrir une Pull Request

### License
MIT License - voir LICENSE.md

---

## 🎯 KPIs et Métriques

### Métriques techniques
- **Accuracy de détection**: > 85%
- **Temps de réponse**: < 2s
- **Disponibilité**: 99.9%

### Métriques business
- **Utilisateurs actifs**: Objectif 10,000
- **Détections/jour**: > 1,000
- **Satisfaction utilisateur**: > 4.5/5

### Impact social
- **Réduction pertes**: 30-40%
- **Augmentation revenus**: 20-30%
- **Formations dispensées**: 500+

---

*Document maintenu par l'équipe AgriDetect - Dernière mise à jour: Janvier 2024*
