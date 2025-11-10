from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional, List, Dict, Any
import io
import logging
import os
import time
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from PIL import Image, UnidentifiedImageError, ImageFile
import uvicorn

# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("agridetect_api.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("agridetect")

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
APP_VERSION = os.getenv("AGRIDETECT_APP_VERSION", "1.2.0")
DEFAULT_LANG = os.getenv("AGRIDETECT_DEFAULT_LANG", "fr")
MODEL_PATH_ENV = os.getenv("AGRIDETECT_MODEL_PATH")
ALLOWED_ORIGINS = os.getenv("AGRIDETECT_ALLOWED_ORIGINS", "*").split(",")

MAX_IMAGE_SIZE_MB = float(os.getenv("AGRIDETECT_MAX_IMAGE_MB", "10"))
MAX_IMAGE_BYTES = int(MAX_IMAGE_SIZE_MB * 1024 * 1024)
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = int(os.getenv("AGRIDETECT_MAX_IMAGE_PIXELS", str(50_000_000)))

DETECTOR = None
MODEL_LOAD_ERROR: Optional[str] = None
STARTUP_TIME = time.time()

# -------------------------------------------------------------------
# Importer le chatbot
# -------------------------------------------------------------------
_CHATBOT_AVAILABLE = False
try:
    from chatbot import generate_chat_response
    _CHATBOT_AVAILABLE = True
    log.info("✅ Chatbot importé avec succès")
except Exception as e:
    log.error(f"❌ Erreur import chatbot: {e}")
    def generate_chat_response(session_id: str, user_message: str, lang: str = "fr") -> str:
        return "Chatbot non disponible. Veuillez réessayer plus tard."

# -------------------------------------------------------------------
# Base de données des maladies
# -------------------------------------------------------------------
COMMON_DISEASES = [
    {
        "id": "tomato_bacterial_spot",
        "name_fr": "Tomate - Tache bactérienne",
        "name_en": "Tomato - Bacterial Spot",
        "symptoms_fr": ["Petites lésions sombres", "Perforations possibles"],
        "treatment_fr": ["Cuivre en préventif", "Enlever parties atteintes"],
        "severity": "Modérée",
        "season": "Toute saison"
    },
    {
        "id": "tomato_early_blight",
        "name_fr": "Tomate - Brûlure précoce",
        "name_en": "Tomato - Early Blight",
        "symptoms_fr": ["Cercles concentriques bruns", "Jaunissement", "Chute des feuilles"],
        "treatment_fr": ["Fongicide foliaire approprié", "Rotation des cultures"],
        "severity": "Modérée",
        "season": "Saison humide"
    },
    {
        "id": "tomato_late_blight",
        "name_fr": "Tomate - Brûlure tardive (mildiou)",
        "name_en": "Tomato - Late Blight",
        "symptoms_fr": ["Taches huileuses puis brunes", "Duvet blanc dessous"],
        "treatment_fr": ["Fongicide anti-mildiou", "Enlever feuilles très atteintes"],
        "severity": "Élevée",
        "season": "Saison humide"
    },
    {
        "id": "tomato_spider_mites",
        "name_fr": "Tomate - Acariens",
        "name_en": "Tomato - Spider Mites",
        "symptoms_fr": ["Feuilles piquetées", "Jaunissement progressif"],
        "treatment_fr": ["Savon ou huile de neem"],
        "severity": "Modérée",
        "season": "Saison sèche"
    },
    {
        "id": "tomato_mosaic_virus",
        "name_fr": "Tomate - Virus de la mosaïque",
        "name_en": "Tomato - Mosaic Virus",
        "symptoms_fr": ["Mosaïque sur feuilles et fruits"],
        "treatment_fr": ["Éliminer les plantes infectées"],
        "severity": "Élevée",
        "season": "Toute saison"
    },
    {
        "id": "potato_early_blight",
        "name_fr": "Pomme de terre - Brûlure précoce",
        "name_en": "Potato - Early Blight",
        "symptoms_fr": ["Taches brunes concentriques", "Jaunissement périphérique"],
        "treatment_fr": ["Fongicide préventif", "Rotation des cultures"],
        "severity": "Modérée",
        "season": "Saison humide"
    },
    {
        "id": "potato_late_blight",
        "name_fr": "Pomme de terre - Brûlure tardive",
        "name_en": "Potato - Late Blight",
        "symptoms_fr": ["Taches vert sombre puis brunes", "Feutrage blanc dessous"],
        "treatment_fr": ["Fongicides anti-mildiou"],
        "severity": "Élevée",
        "season": "Saison humide"
    },
    {
        "id": "pepper_bacterial_spot",
        "name_fr": "Poivron - Tache bactérienne",
        "name_en": "Pepper - Bacterial Spot",
        "symptoms_fr": ["Petites taches sombres", "Perforations possibles"],
        "treatment_fr": ["Traitement cuivre en préventif"],
        "severity": "Modérée",
        "season": "Toute saison"
    },
]

# -------------------------------------------------------------------
# Modèles Pydantic
# -------------------------------------------------------------------
class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    language: Optional[str] = "fr"
    context: Optional[Dict[str, Any]] = None

    class Config:
        protected_namespaces = ()


class DiseaseDetectionResponse(BaseModel):
    disease_id: str
    disease_name: str
    confidence: float = Field(..., ge=0, le=1)
    severity: str
    treatments: List[str]
    prevention_tips: List[str]
    affected_crop: str
    detection_date: datetime
    success: bool = True

    class Config:
        protected_namespaces = ()


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    services: Dict[str, str]
    model_loaded: bool
    uptime: float

    class Config:
        protected_namespaces = ()


# -------------------------------------------------------------------
# Lifespan
# -------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info(f"🚀 Démarrage AgriDetect v{APP_VERSION}")
    log.info(f"✅ Chatbot disponible: {_CHATBOT_AVAILABLE}")
    yield
    log.info("🛑 Arrêt du serveur")


# -------------------------------------------------------------------
# Application FastAPI
# -------------------------------------------------------------------
app = FastAPI(
    title="AgriDetect API",
    description="API pour la détection de maladies des plantes avec IA",
    version=APP_VERSION,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------
@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Bienvenue sur AgriDetect API",
        "version": APP_VERSION,
        "status": "operational",
        "endpoints": {
            "detection": "/api/v1/detect-disease",
            "chat": "/api/v1/chat",
            "diseases": "/api/v1/diseases/common",
            "stats": "/api/v1/statistics/dashboard",
            "health": "/health",
            "docs": "/docs",
        },
        "services": {"model_loaded": False, "chatbot_available": _CHATBOT_AVAILABLE},
    }


@app.post("/api/v1/detect-disease", response_model=DiseaseDetectionResponse, tags=["detection"])
async def detect_disease(
    file: UploadFile = File(..., description="Image de la plante à analyser"),
    crop_type: Optional[str] = None,
    language: Optional[str] = DEFAULT_LANG,
):
    """Endpoint de détection de maladie (version démo)"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail=f"Le fichier doit être une image. Type reçu: {file.content_type}")
    
    return DiseaseDetectionResponse(
        disease_id="tomato_early_blight",
        disease_name="Brûlure précoce",
        confidence=0.89,
        severity="Modérée",
        treatments=["Appliquer un fongicide cuivre", "Enlever les feuilles infectées", "Améliorer la circulation d'air"],
        prevention_tips=["Maintenir l'humidité modérée", "Espacer les plantes", "Arroser à la base"],
        affected_crop="Tomate",
        detection_date=datetime.now(),
        success=True,
    )


@app.post("/api/v1/chat", tags=["chat"])
async def chat_with_bot(message: ChatMessage):
    """Endpoint de chat - utilise le chatbot.py pour les réponses"""
    session_id = (message.context or {}).get("session_id", "default")
    lang = message.language or DEFAULT_LANG
    user_msg = message.message.strip()

    log.info(f"💬 Chat request: session={session_id}, lang={lang}, msg={user_msg[:80]}...")

    try:
        response = generate_chat_response(session_id, user_msg, lang)
        log.info(f"✅ Chatbot response: {response[:100]}...")
    except Exception as e:
        log.error(f"❌ Erreur chatbot: {e}", exc_info=True)
        response = f"Erreur lors du traitement: {str(e)}"

    return {
        "response": response,
        "language": lang,
        "suggestions": ["Détécter une maladie", "Conseils de prévention", "Liste des maladies"],
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "success": True,
    }


@app.get("/api/v1/diseases/common", tags=["catalogue"])
async def get_common_diseases(language: Optional[str] = "fr"):
    """Récupérer les maladies courantes"""
    lang = language.lower() if language else "fr"
    
    diseases = []
    for disease in COMMON_DISEASES:
        name_key = f"name_{lang}" if f"name_{lang}" in disease else "name_fr"
        symptoms_key = f"symptoms_{lang}" if f"symptoms_{lang}" in disease else "symptoms_fr"
        treatment_key = f"treatment_{lang}" if f"treatment_{lang}" in disease else "treatment_fr"
        
        diseases.append({
            "id": disease["id"],
            "name": disease.get(name_key, disease["name_fr"]),
            "symptoms": disease.get(symptoms_key, disease["symptoms_fr"]),
            "treatment": disease.get(treatment_key, disease["treatment_fr"]),
            "severity": disease["severity"],
            "season": disease["season"]
        })
    
    return {
        "diseases": diseases,
        "total": len(diseases),
        "language": lang
    }


@app.get("/api/v1/statistics/dashboard", tags=["statistiques"])
async def get_dashboard_stats():
    """Récupérer les statistiques du tableau de bord"""
    return {
        "total_detections": 1543,
        "diseases_detected": len(COMMON_DISEASES),
        "success_rate": 95.8,
        "active_users": 342,
        "crops_monitored": ["Tomate", "Pomme de terre", "Poivron"],
        "top_diseases": [
            {"name": "Tache bactérienne", "count": 156, "crop": "Tomate/Poivron"},
            {"name": "Brûlure précoce", "count": 124, "crop": "Tomate/Pomme de terre"},
            {"name": "Brûlure tardive", "count": 103, "crop": "Tomate/Pomme de terre"},
            {"name": "Acariens", "count": 89, "crop": "Tomate"},
            {"name": "Virus mosaïque", "count": 76, "crop": "Tomate"},
        ],
        "period": "30 derniers jours",
        "model_accuracy": 95.8,
        "model_precision": 97.5,
    }


@app.get("/health", response_model=HealthResponse, tags=["santé"])
async def health():
    """Endpoint de santé"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version=APP_VERSION,
        services={"model": "not_loaded", "chatbot": "available" if _CHATBOT_AVAILABLE else "unavailable", "api": "running", "database": "in_memory"},
        model_loaded=False,
        uptime=time.time() - STARTUP_TIME,
    )


@app.get("/health/live", tags=["santé"])
async def live():
    """Endpoint de vérification de vie"""
    return {"status": "alive", "timestamp": datetime.now().isoformat(), "uptime": time.time() - STARTUP_TIME}


@app.get("/health/ready", tags=["santé"])
async def ready():
    """Endpoint de vérification de disponibilité"""
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": False,
        "model_error": "Modèle non chargé (version démo)",
        "chatbot_available": _CHATBOT_AVAILABLE,
        "services_ready": {"model": False, "chatbot": _CHATBOT_AVAILABLE, "api": True},
    }


# -------------------------------------------------------------------
# Entrypoint
# -------------------------------------------------------------------
if __name__ == "__main__":
    log.info(f"🚀 Démarrage du serveur AgriDetect v{APP_VERSION}")
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "false").lower() == "true",
        log_level="info",
        access_log=True,
    )
