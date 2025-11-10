#!/bin/bash

# ========================================
# Script de Démarrage AgriDetect
# ========================================

echo "🌾 =========================================="
echo "   AgriDetect - Démarrage Automatique"
echo "========================================== 🌾"
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les étapes
function show_step() {
    echo -e "${BLUE}➤ $1${NC}"
}

function show_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

function show_error() {
    echo -e "${RED}✗ $1${NC}"
}

function show_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# ========================================
# Étape 1 : Vérifier Docker
# ========================================
show_step "Vérification de Docker..."

if ! command -v docker &> /dev/null; then
    show_error "Docker n'est pas installé ou n'est pas dans le PATH"
    echo "Veuillez installer Docker Desktop : https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! docker info &> /dev/null; then
    show_error "Docker n'est pas démarré"
    echo "Veuillez démarrer Docker Desktop"
    exit 1
fi

show_success "Docker est actif"
echo ""

# ========================================
# Étape 2 : Démarrer les services Docker
# ========================================
show_step "Démarrage des services Docker (PostgreSQL, Redis, PgAdmin)..."

docker-compose up -d

if [ $? -eq 0 ]; then
    show_success "Services Docker démarrés avec succès"
else
    show_error "Erreur lors du démarrage des services Docker"
    exit 1
fi

echo ""
show_step "Attente du démarrage de PostgreSQL..."
sleep 5
show_success "PostgreSQL prêt"
echo ""

# ========================================
# Étape 3 : Activer l'environnement virtuel Python
# ========================================
show_step "Activation de l'environnement virtuel Python..."

if [ ! -d "venv" ]; then
    show_warning "Environnement virtuel non trouvé. Création..."
    python -m venv venv
    show_success "Environnement virtuel créé"
fi

source venv/Scripts/activate
show_success "Environnement virtuel activé"
echo ""

# ========================================
# Étape 4 : Installer/Mettre à jour les dépendances
# ========================================
show_step "Vérification des dépendances Python..."

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    show_success "Dépendances installées/mises à jour"
else
    show_warning "Fichier requirements.txt non trouvé"
fi

echo ""

# ========================================
# Étape 5 : Lancer l'API FastAPI
# ========================================
show_step "Démarrage de l'API AgriDetect..."

# Lancer l'API en arrière-plan
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &
API_PID=$!

# Attendre que l'API démarre
echo "Attente du démarrage de l'API..."
sleep 3

# Vérifier si l'API est active
if ps -p $API_PID > /dev/null; then
    show_success "API démarrée avec succès (PID: $API_PID)"
else
    show_error "Erreur lors du démarrage de l'API"
    echo "Consultez le fichier api.log pour plus d'informations"
    exit 1
fi

echo ""

# ========================================
# Étape 6 : Ouvrir l'interface web
# ========================================
show_step "Préparation de l'interface web..."

# Vérifier si un serveur HTTP Python est déjà actif sur le port 3000
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    show_warning "Le port 3000 est déjà utilisé"
else
    # Démarrer un serveur HTTP simple
    if [ -d "web" ]; then
        cd web
        nohup python -m http.server 3000 > ../web.log 2>&1 &
        WEB_PID=$!
        cd ..
        show_success "Serveur web démarré (PID: $WEB_PID)"
    else
        show_warning "Dossier 'web' non trouvé. Ouvrez les fichiers HTML manuellement."
    fi
fi

echo ""

# ========================================
# Récapitulatif
# ========================================
echo "=========================================="
echo -e "${GREEN}✓ Tous les services sont démarrés !${NC}"
echo "=========================================="
echo ""
echo "📍 URLs d'accès :"
echo ""
echo "  🌐 Interface Web:"
echo -e "     ${BLUE}http://localhost:3000${NC} (si serveur web démarré)"
echo -e "     ou ouvrez directement: ${BLUE}index.html${NC}"
echo ""
echo "  🔧 API Backend (Swagger UI):"
echo -e "     ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo "  💾 PgAdmin (Base de données):"
echo -e "     ${BLUE}http://localhost:5050${NC}"
echo ""
echo "  📊 API Health Check:"
echo -e "     ${BLUE}http://localhost:8000/health${NC}"
echo ""
echo "=========================================="
echo "📝 Commandes utiles :"
echo ""
echo "  • Voir les logs de l'API:"
echo "    tail -f api.log"
echo ""
echo "  • Arrêter l'API:"
echo "    kill $API_PID"
echo ""
echo "  • Arrêter les services Docker:"
echo "    docker-compose down"
echo ""
echo "  • Voir les conteneurs actifs:"
echo "    docker ps"
echo ""
echo "=========================================="
echo ""
echo -e "${GREEN}🎉 AgriDetect est prêt à l'emploi !${NC}"
echo ""

# Sauvegarder les PIDs pour faciliter l'arrêt
echo $API_PID > .api.pid
if [ ! -z "$WEB_PID" ]; then
    echo $WEB_PID > .web.pid
fi
