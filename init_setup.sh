#!/bin/bash

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 AgriDetect - Initialisation${NC}"
echo "================================="
echo ""

# 1. Créer répertoires
echo -e "${BLUE}📁 Création répertoires...${NC}"
mkdir -p backend/routes
mkdir -p backend/models
mkdir -p backend/services
mkdir -p backend/tests
mkdir -p frontend
mkdir -p models
mkdir -p logs
mkdir -p uploads
echo -e "${GREEN}✅ Répertoires créés${NC}"
echo ""

# 2. Vérifier Docker
echo -e "${BLUE}🐳 Vérification Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas installé!${NC}"
    echo "Télécharge Docker: https://www.docker.com/products/docker-desktop"
    exit 1
fi
echo -e "${GREEN}✅ Docker trouvé${NC}"
echo ""

# 3. Arrêter les anciens conteneurs
echo -e "${BLUE}⏹️  Arrêt des anciens services...${NC}"
docker-compose down 2>/dev/null || true
sleep 2
echo -e "${GREEN}✅ Anciens services arrêtés${NC}"
echo ""

# 4. Lancer Docker services
echo -e "${BLUE}🐳 Démarrage PostgreSQL + Redis + PgAdmin...${NC}"
docker-compose up -d
echo "⏳ Attendre que PostgreSQL soit prêt... (15 secondes)"
sleep 15
echo -e "${GREEN}✅ Services lancés${NC}"
echo ""

# 5. Vérifier PostgreSQL
echo -e "${BLUE}🔍 Vérification PostgreSQL...${NC}"
docker exec agridetect_postgres pg_isready -U agridetect_user
echo -e "${GREEN}✅ PostgreSQL connecté${NC}"
echo ""

# 6. Python - Créer environnement virtuel
echo -e "${BLUE}🐍 Création environnement Python...${NC}"
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Environnement virtuel créé${NC}"
else
    echo -e "${YELLOW}ℹ️  Environnement virtuel existe déjà${NC}"
fi
echo ""

# 7. Installer dépendances
echo -e "${BLUE}📦 Installation dépendances Python...${NC}"
source venv/bin/activate
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r ../requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✅ Dépendances installées${NC}"
echo ""

# 8. Résumé
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ INITIALISATION COMPLÈTE!         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📍 Services en cours d'exécution:${NC}"
docker-compose ps
echo ""
echo -e "${YELLOW}🌐 URLs d'accès:${NC}"
echo "  • API: http://localhost:8000"
echo "  • Swagger UI: http://localhost:8000/docs"
echo "  • PgAdmin: http://localhost:5050"
echo "  • Redis: localhost:6379"
echo ""
echo -e "${YELLOW}▶️  Prochaine étape - Lancer l'API:${NC}"
echo ""
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo -e "${YELLOW}💡 Puis dans un autre terminal:${NC}"
echo "  curl http://localhost:8000/health"
echo ""
