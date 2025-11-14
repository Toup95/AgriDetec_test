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
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator
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
# Dépendance upload
# -------------------------------------------------------------------
try:
    import multipart  # noqa: F401
    MULTIPART_IMPORT_ERROR: Optional[str] = None
except ImportError:
    MULTIPART_IMPORT_ERROR = (
        "python-multipart non installé. Exécutez: pip install python-multipart"
    )
    log.warning(MULTIPART_IMPORT_ERROR)

# -------------------------------------------------------------------
# Imports applicatifs (détecteur + chatbot facultatif)
# -------------------------------------------------------------------
PlantDiseaseDetector = None
DETECTOR_AVAILABLE = False
try:
    from disease_detector import PlantDiseaseDetector  # type: ignore
    DETECTOR_AVAILABLE = True
    log.info("✅ PlantDiseaseDetector importé avec succès")
except Exception as e:
    log.error(f"❌ Impossible d'importer PlantDiseaseDetector: {e}")

# chatbot optionnel
_CHATBOT_AVAILABLE = False
_ChatbotClass = None
_generate_chat = None
try:
    from chatbot import MultilingualAgriChatbot  # type: ignore
    _ChatbotClass = MultilingualAgriChatbot
    _CHATBOT_AVAILABLE = True
    log.info("✅ Chatbot (classe) importé")
except Exception as e:
    log.warning(f"⚠️ Chatbot classe non disponible: {e}")

try:
    from chatbot import generate_chat_response  # type: ignore
    _generate_chat = generate_chat_response
    _CHATBOT_AVAILABLE = True
    log.info("✅ Chatbot (fonction) importé")
except Exception as e:
    log.warning(f"⚠️ Chatbot fonction non disponible: {e}")

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
APP_VERSION = os.getenv("AGRIDETECT_APP_VERSION", "1.1.0")
DEFAULT_LANG = os.getenv("AGRIDETECT_DEFAULT_LANG", "fr")
MODEL_PATH_ENV = os.getenv("AGRIDETECT_MODEL_PATH")
ALLOWED_ORIGINS = os.getenv("AGRIDETECT_ALLOWED_ORIGINS", "*").split(",")

MAX_IMAGE_SIZE_MB = float(os.getenv("AGRIDETECT_MAX_IMAGE_MB", "10"))
MAX_IMAGE_BYTES = int(MAX_IMAGE_SIZE_MB * 1024 * 1024)
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = int(os.getenv("AGRIDETECT_MAX_IMAGE_PIXELS", str(50_000_000)))

DETECTOR = None  # sera rempli dans lifespan
MODEL_LOAD_ERROR: Optional[str] = None
STARTUP_TIME = time.time()


def resolve_model_path(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    if os.name == "nt":
        path = path.replace("\\", "/")
    if not os.path.exists(path):
        log.warning(f"⚠️ Chemin modèle inexistant: {path}")
        return path
    if os.path.isfile(path) and path.endswith((".keras", ".h5")):
        parent = os.path.dirname(path)
        log.info(f"🔁 Conversion fichier modèle -> dossier: {path} -> {parent}")
        return parent
    return path


MODEL_PATH = resolve_model_path(MODEL_PATH_ENV)

# -------------------------------------------------------------------
# Catalogue
# -------------------------------------------------------------------
DATASET_DISEASES: List[Dict[str, Any]] = [
    # Pepper
    {
        "id": "pepper_bacterial_spot",
        "plant_en": "Pepper (bell)",
        "plant_fr": "Poivron",
        "disease_en": "Bacterial spot",
        "disease_fr": "Tache bactérienne",
        "severity": "Modérée",
        "season": "Toute saison",
    },
    {
        "id": "pepper_healthy",
        "plant_en": "Pepper (bell)",
        "plant_fr": "Poivron",
        "disease_en": "Healthy",
        "disease_fr": "Sain",
        "severity": "Aucune",
        "season": "Toute saison",
    },
    # Potato
    {
        "id": "potato_early_blight",
        "plant_en": "Potato",
        "plant_fr": "Pomme de terre",
        "disease_en": "Early blight",
        "disease_fr": "Brûlure précoce",
        "severity": "Modérée",
        "season": "Saison humide",
    },
    {
        "id": "potato_late_blight",
        "plant_en": "Potato",
        "plant_fr": "Pomme de terre",
        "disease_en": "Late blight",
        "disease_fr": "Brûlure tardive",
        "severity": "Élevée",
        "season": "Saison humide",
    },
    {
        "id": "potato_healthy",
        "plant_en": "Potato",
        "plant_fr": "Pomme de terre",
        "disease_en": "Healthy",
        "disease_fr": "Sain",
        "severity": "Aucune",
        "season": "Toute saison",
    },
    # Tomato
    {
        "id": "tomato_bacterial_spot",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Bacterial spot",
        "disease_fr": "Tache bactérienne",
        "severity": "Modérée",
        "season": "Toute saison",
    },
    {
        "id": "tomato_early_blight",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Early blight",
        "disease_fr": "Brûlure précoce",
        "severity": "Modérée",
        "season": "Saison humide",
    },
    {
        "id": "tomato_leaf_mold",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Leaf mold",
        "disease_fr": "Moisissure des feuilles",
        "severity": "Modérée",
        "season": "Saison humide",
    },
    {
        "id": "tomato_septoria_leaf_spot",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Septoria leaf spot",
        "disease_fr": "Tache foliaire de Septoria",
        "severity": "Modérée",
        "season": "Saison humide",
    },
    {
        "id": "tomato_spider_mites",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Spider mites",
        "disease_fr": "Acariens",
        "severity": "Modérée",
        "season": "Saison sèche",
    },
    {
        "id": "tomato_target_spot",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Target spot",
        "disease_fr": "Tache cible",
        "severity": "Modérée",
        "season": "Toute saison",
    },
    {
        "id": "tomato_mosaic_virus",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Tomato mosaic virus",
        "disease_fr": "Virus de la mosaïque",
        "severity": "Élevée",
        "season": "Toute saison",
    },
    {
        "id": "tomato_yellow_leaf_curl_virus",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Yellow leaf curl virus",
        "disease_fr": "Virus de l'enroulement jaune",
        "severity": "Élevée",
        "season": "Toute saison",
    },
    {
        "id": "tomato_healthy",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Healthy",
        "disease_fr": "Sain",
        "severity": "Aucune",
        "season": "Toute saison",
    },
]

# -------------------------------------------------------------------
# Pydantic
# -------------------------------------------------------------------
class DiseaseDetectionResponse(BaseModel):
    disease_id: str
    disease_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    severity: str
    treatments: List[Dict[str, Any]]
    prevention_tips: List[str]
    affected_crop: str
    detection_date: datetime
    success: bool = True

    @validator("confidence")
    def round_confidence(cls, v: float) -> float:
        return round(v, 4)


class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    language: Optional[str] = Field(None, pattern="^(fr|wo|pu)$")
    context: Optional[Dict[str, Any]] = None

    @validator("message")
    def validate_message(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Le message ne peut pas être vide")
        return v.strip()


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    services: Dict[str, str]
    model_loaded: bool
    uptime: float


# -------------------------------------------------------------------
# Utils API
# -------------------------------------------------------------------
def validate_env() -> bool:
    if not MODEL_PATH:
        log.warning("❌ AGRIDETECT_MODEL_PATH non défini")
        return False
    if not os.path.exists(MODEL_PATH):
        log.error(f"❌ Chemin modèle inexistant: {MODEL_PATH}")
        return False
    model_files = list(Path(MODEL_PATH).glob("model.*"))
    saved_model_dir = Path(MODEL_PATH) / "saved_model"
    if not model_files and not saved_model_dir.exists():
        log.error("❌ Aucun fichier de modèle dans le dossier")
        return False
    return True


def _open_image_safe(contents: bytes) -> Image.Image:
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Fichier vide.")
    if len(contents) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=(
                f"Image trop lourde ({len(contents)/1024/1024:.1f} MB > {MAX_IMAGE_SIZE_MB} MB)."
            ),
        )
    try:
        im = Image.open(io.BytesIO(contents))
        im.load()
        if im.size[0] > 5000 or im.size[1] > 5000:
            raise HTTPException(
                status_code=400,
                detail="Image trop grande. Dimensions maximum: 5000x5000 pixels.",
            )
        return im.convert("RGB")
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="Format d'image non supporté. Utilisez JPEG, PNG ou WebP.",
        )
    except Image.DecompressionBombError:
        raise HTTPException(status_code=413, detail="Image trop grande (décompression bomb).")
    except Exception as e:
        log.error(f"Erreur traitement image: {e}")
        raise HTTPException(status_code=400, detail=f"Erreur lors du traitement de l'image: {e}")


def map_prediction_to_catalog(disease_key: str, disease_name_raw: str) -> Optional[Dict[str, Any]]:
    if not disease_key and not disease_name_raw:
        return None
    for item in DATASET_DISEASES:
        if disease_key and item["id"] == disease_key:
            return item
    if disease_name_raw:
        key = (
            disease_name_raw.replace("___", "_")
            .replace("__", "_")
            .replace(" ", "_")
            .strip()
            .lower()
        )
        for item in DATASET_DISEASES:
            if key in item["id"] or item["id"] in key:
                return item
            disease_en_norm = item["disease_en"].lower().replace(" ", "_")
            if key in disease_en_norm or disease_en_norm in key:
                return item
    return None


class _ChatAdapter:
    def __init__(self):
        self._bot = _ChatbotClass() if _ChatbotClass else None
        self._has = _CHATBOT_AVAILABLE

    def is_available(self) -> bool:
        return self._has

    def reply(
        self,
        message: str,
        session_id: str,
        language: Optional[str],
        context: Optional[Dict[str, Any]],
    ):
        if not self._has:
            raise HTTPException(status_code=501, detail="Service chatbot non disponible.")
        try:
            if self._bot is not None and _generate_chat is not None:
                return _generate_chat(
                    self._bot,
                    message=message,
                    session_id=session_id,
                    language=language,
                    extra_context=context or {},
                )
            if _generate_chat is not None:
                if language in ("fr", "wo", "pu") and not message.strip().startswith("/lang"):
                    message = f"/lang {language}\n{message}"
                resp_text = _generate_chat(session_id=session_id, user_message=message)
                return {
                    "response": resp_text,
                    "language": language or DEFAULT_LANG,
                    "intent": "general",
                    "suggestions": [],
                    "context": {"topic": "general", **(context or {})},
                    "timestamp": datetime.now().isoformat(),
                }
        except Exception as e:
            log.exception("Erreur dans le chatbot")
            raise HTTPException(status_code=500, detail=f"Erreur du chatbot: {e}")
        raise HTTPException(status_code=500, detail="Configuration chatbot incompatible.")


_CHAT = _ChatAdapter()

# -------------------------------------------------------------------
# Lifespan
# -------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global DETECTOR, MODEL_LOAD_ERROR

    log.info("🚀 Démarrage de l'API AgriDetect...")
    if not validate_env():
        MODEL_LOAD_ERROR = "Environnement invalide"
    elif not DETECTOR_AVAILABLE:
        MODEL_LOAD_ERROR = "Module de détection non disponible"
    else:
        try:
            log.info(f"🔍 Chargement du modèle depuis: {MODEL_PATH}")
            DETECTOR = PlantDiseaseDetector(model_path=MODEL_PATH)  # type: ignore
            if getattr(DETECTOR, "is_loaded", False):
                MODEL_LOAD_ERROR = None
                log.info("✅ Modèle chargé et opérationnel")
            else:
                MODEL_LOAD_ERROR = "Modèle non chargé (is_loaded=False)"
                log.error("❌ Modèle non chargé")
        except Exception as e:
            MODEL_LOAD_ERROR = f"Erreur lors du chargement: {e}"
            log.exception("❌ Erreur lors du chargement du modèle")

    try:
        yield
    finally:
        log.info("🧹 Arrêt de l'API AgriDetect...")


app = FastAPI(
    title="AgriDetect API",
    description="Détection de maladies des plantes & assistance agricole multilingue",
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
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
# Handlers d'erreurs
# -------------------------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error": True, "timestamp": datetime.now().isoformat()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    log.exception("Erreur non gérée")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur.", "error": True, "timestamp": datetime.now().isoformat()},
    )


# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------
@app.get("/", tags=["root"])
async def root():
    return {
        "message": "🌾 Bienvenue sur AgriDetect API",
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
        "services": {
            "model_loaded": DETECTOR is not None and getattr(DETECTOR, "is_loaded", False),
            "chatbot_available": _CHAT.is_available(),
        },
    }


@app.post("/api/v1/detect-disease", response_model=DiseaseDetectionResponse, tags=["detection"])
async def detect_disease(
    file: UploadFile = File(..., description="Image de la plante à analyser"),
    crop_type: Optional[str] = None,
    language: Optional[str] = DEFAULT_LANG,
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Le fichier doit être une image. Type reçu: {file.content_type}",
        )

    if language not in ("fr", "wo", "pu"):
        language = DEFAULT_LANG

    if MULTIPART_IMPORT_ERROR:
        raise HTTPException(status_code=503, detail=MULTIPART_IMPORT_ERROR)

    if MODEL_LOAD_ERROR:
        raise HTTPException(
            status_code=503,
            detail=f"Modèle non disponible: {MODEL_LOAD_ERROR}",
        )

    if DETECTOR is None or not getattr(DETECTOR, "is_loaded", False):
        raise HTTPException(status_code=503, detail="Modèle non chargé côté serveur.")

    contents = await file.read()
    image = _open_image_safe(contents)

    start = time.time()
    result = DETECTOR.predict(image, language=language)  # type: ignore
    duration = time.time() - start
    log.info(
        f"🔍 Prédiction en {duration:.2f}s: {result.get('disease_name', 'Inconnu')} "
        f"({result.get('confidence', 0):.1%})"
    )

    if "error" in result:
      # on remonte une vraie erreur au frontend
      raise HTTPException(status_code=500, detail=result["error"])

    disease_key = result.get("disease_key", "")
    disease_name_raw = result.get("disease_name", "")

    catalog_match = map_prediction_to_catalog(disease_key, disease_name_raw)

    affected_crop_final = crop_type or result.get("affected_crop", "Non spécifié")
    if catalog_match:
        affected_crop_final = catalog_match["plant_fr"]

    return DiseaseDetectionResponse(
        disease_id=disease_key or "unknown",
        disease_name=(
            catalog_match["disease_fr"]
            if catalog_match
            else disease_name_raw or "Maladie non identifiée"
        ),
        confidence=float(result.get("confidence", 0.0)),
        severity=result.get("severity", "Inconnue"),
        treatments=list(result.get("treatments", [])),
        prevention_tips=list(result.get("prevention_tips", [])),
        affected_crop=affected_crop_final,
        detection_date=datetime.now(),
        success=result.get("success", True),
    )


@app.post("/api/v1/chat", tags=["chat"])
async def chat_with_bot(message: ChatMessage):
    session_id = (message.context or {}).get("session_id", "default")
    lang = message.language or DEFAULT_LANG

    log.info(f"💬 Chat ({lang}) session={session_id} msg={message.message[:80]}...")

    reply = _CHAT.reply(
        message=message.message,
        session_id=session_id,
        language=lang,
        context=message.context,
    )

    if isinstance(reply, dict):
        resp = reply
    else:
        resp = {"response": str(reply), "language": lang, "suggestions": []}

    resp.update(
        {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "success": True,
        }
    )
    return resp


@app.get("/api/v1/diseases/common", tags=["catalogue"])
async def get_common_diseases(crop_type: Optional[str] = None):
    if not crop_type:
        return {
            "diseases": DATASET_DISEASES,
            "total": len(DATASET_DISEASES),
            "crops": ["Tomate", "Pomme de terre", "Poivron"],
        }

    norm = crop_type.strip().lower()
    aliases = {
        "tomate": ["tomate", "tomato"],
        "pomme de terre": ["pomme de terre", "potato"],
        "poivron": ["poivron", "pepper", "bell pepper", "pepper (bell)"],
    }

    target_aliases = None
    for key, vals in aliases.items():
        if norm in [v.lower() for v in vals]:
            target_aliases = vals
            break

    if not target_aliases:
        return {"diseases": [], "total": 0, "filter": crop_type}

    filtered = [
        d
        for d in DATASET_DISEASES
        if d["plant_en"].lower() in [v.lower() for v in target_aliases]
        or d["plant_fr"].lower() in [v.lower() for v in target_aliases]
    ]

    return {
        "diseases": filtered,
        "total": len(filtered),
        "filter": crop_type,
        "crop_normalized": target_aliases[0],
    }


@app.get("/api/v1/statistics/dashboard", tags=["statistiques"])
async def get_dashboard_stats():
    total_diseases = len(DATASET_DISEASES)
    return {
        "total_detections": 1543,
        "diseases_detected": total_diseases,   # = types de maladies
        "success_rate": 95.8,
        "active_users": 342,
        "crops_monitored": ["Tomate", "Pomme de terre", "Poivron"],

        # 👉 ce bloc manquait : c’est pour “Maladies courantes”
        "common_diseases": [
            {"name": "Tomate — mildiou", "count": 320},
            {"name": "Tomate — tache bactérienne", "count": 156},
            {"name": "Tomate — septoriose", "count": 121},
            {"name": "Pomme de terre — mildiou", "count": 103},
            {"name": "Poivron — tache bactérienne", "count": 74},
        ],

        # 👉 ça c’est ta colonne de droite
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
    model_status = (
        "loaded" if (DETECTOR is not None and getattr(DETECTOR, "is_loaded", False)) else "error"
    )
    chatbot_status = "available" if _CHAT.is_available() else "unavailable"
    overall_status = "healthy" if model_status == "loaded" else "degraded"
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now().isoformat(),
        version=APP_VERSION,
        services={
            "model": model_status,
            "chatbot": chatbot_status,
            "api": "running",
            "database": "in_memory",
        },
        model_loaded=DETECTOR is not None and getattr(DETECTOR, "is_loaded", False),
        uptime=time.time() - STARTUP_TIME,
    )


@app.get("/health/live", tags=["santé"])
async def live():
    return {"status": "alive", "timestamp": datetime.now().isoformat(), "uptime": time.time() - STARTUP_TIME}


@app.get("/health/ready", tags=["santé"])
async def ready():
    model_ready = DETECTOR is not None and getattr(DETECTOR, "is_loaded", False) and MODEL_LOAD_ERROR is None
    payload = {
        "status": "ready" if model_ready else "not-ready",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": model_ready,
        "model_error": MODEL_LOAD_ERROR,
        "chatbot_available": _CHAT.is_available(),
        "services_ready": {
            "model": model_ready,
            "chatbot": _CHAT.is_available(),
            "api": True,
        },
    }
    if not model_ready:
        return JSONResponse(status_code=503, content=payload)
    return payload


# -------------------------------------------------------------------
# Routes pour servir les fichiers HTML statiques
# -------------------------------------------------------------------
@app.get("/chat.html")
async def serve_chat():
    """Servir la page du chatbot"""
    return FileResponse("chat.html")

@app.get("/dashboard.html")
async def serve_dashboard():
    """Servir la page du dashboard"""
    return FileResponse("dashboard.html")

@app.get("/index.html")
async def serve_index():
    """Servir la page d'accueil"""
    return FileResponse("index.html")


# -------------------------------------------------------------------
# Servir tous les fichiers statiques (CSS, JS, images, etc.)
# IMPORTANT : Cette ligne DOIT être en dernier pour ne pas intercepter les routes API
# -------------------------------------------------------------------
try:
    app.mount("/", StaticFiles(directory=".", html=True), name="static")
except Exception as e:
    log.warning(f"⚠️ Impossible de monter les fichiers statiques: {e}")


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

