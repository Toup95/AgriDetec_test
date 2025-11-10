#!/bin/bash

# ========================================
# Script d'Arrêt AgriDetect
# ========================================

echo "🌾 =========================================="
echo "   AgriDetect - Arrêt des Services"
echo "========================================== 🌾"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function show_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

function show_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# ========================================
# Arrêter l'API
# ========================================
if [ -f ".api.pid" ]; then
    API_PID=$(cat .api.pid)
    if ps -p $API_PID > /dev/null 2>&1; then
        kill $API_PID
        show_success "API arrêtée (PID: $API_PID)"
    else
        show_warning "L'API n'était pas en cours d'exécution"
    fi
    rm .api.pid
else
    show_warning "Fichier PID de l'API non trouvé"
fi

# ========================================
# Arrêter le serveur web
# ========================================
if [ -f ".web.pid" ]; then
    WEB_PID=$(cat .web.pid)
    if ps -p $WEB_PID > /dev/null 2>&1; then
        kill $WEB_PID
        show_success "Serveur web arrêté (PID: $WEB_PID)"
    else
        show_warning "Le serveur web n'était pas en cours d'exécution"
    fi
    rm .web.pid
else
    show_warning "Fichier PID du serveur web non trouvé"
fi

# ========================================
# Arrêter les services Docker
# ========================================
echo ""
echo "Arrêt des services Docker..."
docker-compose down

if [ $? -eq 0 ]; then
    show_success "Services Docker arrêtés"
else
    show_warning "Erreur lors de l'arrêt des services Docker"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✓ Tous les services ont été arrêtés${NC}"
echo "=========================================="
echo ""
