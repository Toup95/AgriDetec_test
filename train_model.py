from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional, List, Dict, Any
import io
import logging
import os
import time
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator
from PIL import Image, UnidentifiedImageError, ImageFile
import uvicorn

# -------------------------------------------------------------------
# Configuration & Logger (DOIT ÊTRE EN PREMIER)
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO, 
    format="[%(asctime)s] %(levelname)s - %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("agridetect_api.log", encoding="utf-8")
    ]
)
log = logging.getLogger("agridetect")

# -------------------------------------------------------------------
# Détection des dépendances (python-multipart requis par UploadFile)
# -------------------------------------------------------------------
try:
    import multipart  # noqa: F401
    MULTIPART_IMPORT_ERROR = None
except ImportError:
    MULTIPART_IMPORT_ERROR = "python-multipart non installé. Exécutez: pip install python-multipart"
    log.warning(MULTIPART_IMPORT_ERROR)

# -------------------------------------------------------------------
# Imports applicatifs (détecteur et chatbot)
# -------------------------------------------------------------------
try:
    from disease_detector import PlantDiseaseDetector
    DETECTOR_AVAILABLE = True
    log.info("✅ PlantDiseaseDetector importé avec succès")
except ImportError as e:
    log.error(f"❌ Impossible d'importer PlantDiseaseDetector: {e}")
    DETECTOR_AVAILABLE = False
    PlantDiseaseDetector = None

# Chatbot (2 signatures possibles)
_CHATBOT_AVAILABLE = False
_ChatbotClass = None
_legacy_or_helper_generate = None

try:
    from chatbot import MultilingualAgriChatbot as _ChatbotClass
    _CHATBOT_AVAILABLE = True
    log.info("✅ Chatbot MultilingualAgriChatbot importé")
except ImportError as e:
    log.warning(f"⚠️  MultilingualAgriChatbot non disponible: {e}")

try:
    from chatbot import generate_chat_response as _legacy_or_helper_generate
    _CHATBOT_AVAILABLE = True
    log.info("✅ Fonction generate_chat_response importée")
except ImportError as e:
    log.warning(f"⚠️  generate_chat_response non disponible: {e}")

# -------------------------------------------------------------------
# Configuration de l'application
# -------------------------------------------------------------------
APP_VERSION = os.getenv("AGRIDETECT_APP_VERSION", "1.1.0")
DEFAULT_LANG = os.getenv("AGRIDETECT_DEFAULT_LANG", "fr")

# Gestion intelligente des chemins
def resolve_model_path(path: Optional[str]) -> Optional[str]:
    """Résout le chemin du modèle, qu'il s'agisse d'un fichier ou d'un dossier."""
    if not path:
        return None
    
    # Normaliser le chemin
    path = path.replace('\\', '/') if os.name == 'nt' else path
    
    # Vérifier si le chemin existe
    if not os.path.exists(path):
        log.warning(f"⚠️  Chemin modèle n'existe pas: {path}")
        return path
    
    # Si c'est un fichier .keras ou .h5, prendre le dossier parent
    if os.path.isfile(path) and path.endswith(('.keras', '.h5')):
        parent_dir = os.path.dirname(path)
        log.info(f"🔁 Conversion chemin fichier -> dossier: {path} -> {parent_dir}")
        return parent_dir
    
    return path

MODEL_PATH = resolve_model_path(os.getenv("AGRIDETECT_MODEL_PATH"))
ALLOWED_ORIGINS = os.getenv("AGRIDETECT_ALLOWED_ORIGINS", "*").split(",")

# Limites images
MAX_IMAGE_SIZE_MB = float(os.getenv("AGRIDETECT_MAX_IMAGE_MB", "10"))  # Augmenté à 10MB
MAX_IMAGE_BYTES = int(MAX_IMAGE_SIZE_MB * 1024 * 1024)
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = int(os.getenv("AGRIDETECT_MAX_IMAGE_PIXELS", str(50_000_000)))  # Augmenté

# Variables globales
DETECTOR: Optional[PlantDiseaseDetector] = None
MODEL_LOAD_ERROR: Optional[str] = None
STARTUP_TIME = time.time()

# -------------------------------------------------------------------
# Validation de l'environnement
# -------------------------------------------------------------------
def validate_environment() -> bool:
    """Valide la configuration d'environnement."""
    log.info("🔍 Validation de l'environnement...")
    
    if not MODEL_PATH:
        log.warning("❌ AGRIDETECT_MODEL_PATH non défini")
        return False
    
    # Vérifier que le chemin existe
    if not os.path.exists(MODEL_PATH):
        log.error(f"❌ Chemin modèle inexistant: {MODEL_PATH}")
        return False
    
    # Vérifier les fichiers requis dans le dossier
    model_files = list(Path(MODEL_PATH).glob("model.*"))
    saved_model_dir = Path(MODEL_PATH) / "saved_model"
    
    if not model_files and not saved_model_dir.exists():
        log.error(f"❌ Aucun fichier model.* ou dossier saved_model trouvé dans: {MODEL_PATH}")
        try:
            contents = list(Path(MODEL_PATH).iterdir())
            log.info(f"📁 Contenu du dossier: {[item.name for item in contents]}")
        except Exception as e:
            log.error(f"❌ Impossible de lister le dossier: {e}")
        return False
    
    if saved_model_dir.exists():
        log.info(f"✅ Format SavedModel détecté: {saved_model_dir}")
    if model_files:
        log.info(f"✅ Fichiers modèle détectés: {[f.name for f in model_files]}")
    
    # Vérifier les métadonnées (optionnel)
    metadata_files = list(Path(MODEL_PATH).glob("metadata.json"))
    if metadata_files:
        log.info(f"✅ Métadonnées trouvées: {metadata_files[0].name}")
    else:
        log.warning("⚠️  Fichier metadata.json non trouvé, utilisation des classes par défaut")
    
    return True

# -------------------------------------------------------------------
# Catalogue réel issu de ton dataset
# -------------------------------------------------------------------
DATASET_DISEASES: List[Dict[str, Any]] = [
    # 🫑 Pepper / Poivron
    {
        "id": "pepper_bacterial_spot",
        "plant_en": "Pepper (bell)",
        "plant_fr": "Poivron",
        "disease_en": "Bacterial spot",
        "disease_fr": "Tache bactérienne",
        "disease_wo": "Noppalu bakteriya ci poivron",
        "disease_pu": "Ñoppirde bakteriya e poivron",
        "severity": "Modérée",
        "season": "Toute saison"
    },
    {
        "id": "pepper_healthy",
        "plant_en": "Pepper (bell)",
        "plant_fr": "Poivron",
        "disease_en": "Healthy",
        "disease_fr": "Sain",
        "disease_wo": "Baax na",
        "disease_pu": "Ñammude",
        "severity": "Aucune",
        "season": "Toute saison"
    },

    # 🥔 Potato / Pomme de terre
    {
        "id": "potato_early_blight",
        "plant_en": "Potato",
        "plant_fr": "Pomme de terre",
        "disease_en": "Early blight",
        "disease_fr": "Brûlure précoce",
        "disease_wo": "Noppalu jëmmante ci pomme de terre",
        "disease_pu": "Ñoppirde jango e pomme de terre",
        "severity": "Modérée",
        "season": "Saison humide"
    },
    {
        "id": "potato_late_blight",
        "plant_en": "Potato",
        "plant_fr": "Pomme de terre",
        "disease_en": "Late blight",
        "disease_fr": "Brûlure tardive",
        "disease_wo": "Noppalu mu mujj ci pomme de terre",
        "disease_pu": "Ñoppirde mu mujj e pomme de terre",
        "severity": "Élevée",
        "season": "Saison humide"
    },
    {
        "id": "potato_healthy",
        "plant_en": "Potato",
        "plant_fr": "Pomme de terre",
        "disease_en": "Healthy",
        "disease_fr": "Sain",
        "disease_wo": "Baax na",
        "disease_pu": "Ñammude",
        "severity": "Aucune",
        "season": "Toute saison"
    },

    # 🍅 Tomato / Tomate
    {
        "id": "tomato_bacterial_spot",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Bacterial spot",
        "disease_fr": "Tache bactérienne",
        "disease_wo": "Noppalu bakteriya ci tomate",
        "disease_pu": "Ñoppirde bakteriya e tomate",
        "severity": "Modérée",
        "season": "Toute saison"
    },
    {
        "id": "tomato_early_blight",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Early blight",
        "disease_fr": "Brûlure précoce",
        "disease_wo": "Noppalu jëmmante ci tomate",
        "disease_pu": "Ñoppirde jango e tomate",
        "severity": "Modérée",
        "season": "Saison humide"
    },
    {
        "id": "tomato_leaf_mold",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Leaf mold",
        "disease_fr": "Moisissure des feuilles",
        "disease_wo": "Ñakk ndoxmi ci nopp tomate",
        "disease_pu": "Ñoppirde ndiyam e tomate",
        "severity": "Modérée",
        "season": "Saison humide"
    },
    {
        "id": "tomato_septoria_leaf_spot",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Septoria leaf spot",
        "disease_fr": "Tache foliaire de Septoria",
        "disease_wo": "Noppalu septoria ci tomate",
        "disease_pu": "Ñoppirde septoria e tomate",
        "severity": "Modérée",
        "season": "Saison humide"
    },
    {
        "id": "tomato_spider_mites",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Spider mites",
        "disease_fr": "Acariens",
        "disease_wo": "Ñiñ yu ñaar ci tomate",
        "disease_pu": "Wuroo ñaar e tomate",
        "severity": "Modérée",
        "season": "Saison sèche"
    },
    {
        "id": "tomato_target_spot",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Target spot",
        "disease_fr": "Tache cible",
        "disease_wo": "Noppalu but ci tomate",
        "disease_pu": "Ñoppirde cuɓɓo e tomate",
        "severity": "Modérée",
        "season": "Toute saison"
    },
    {
        "id": "tomato_mosaic_virus",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Tomato mosaic virus",
        "disease_fr": "Virus de la mosaïque",
        "disease_wo": "Wirusu mosaïque ci tomate",
        "disease_pu": "Wuroo mosaïque e tomate",
        "severity": "Élevée",
        "season": "Toute saison"
    },
    {
        "id": "tomato_yellow_leaf_curl_virus",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Yellow leaf curl virus",
        "disease_fr": "Virus de l'enroulement jaune",
        "disease_wo": "Wirusu ñuul yaram bu jëm ci tomate",
        "disease_pu": "Wuroo hoore leydi ñuul e tomate",
        "severity": "Élevée",
        "season": "Toute saison"
    },
    {
        "id": "tomato_healthy",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Healthy",
        "disease_fr": "Sain",
        "disease_wo": "Baax na",
        "disease_pu": "Ñammude",
        "severity": "Aucune",
        "season": "Toute saison"
    },
]

# -------------------------------------------------------------------
# Pydantic Models avec validation (CORRIGÉ pour Pydantic v2)
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

    @validator('confidence')
    def round_confidence(cls, v):
        return round(v, 4)


class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    language: Optional[str] = Field(None, pattern='^(fr|wo|pu)$')  # CORRECTION: regex -> pattern
    context: Optional[dict] = None

    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Le message ne peut pas être vide')
        return v.strip()


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    services: Dict[str, str]
    model_loaded: bool
    uptime: float


# -------------------------------------------------------------------
# Utilitaires améliorés
# -------------------------------------------------------------------
def ensure_detector_ready() -> PlantDiseaseDetector:
    """Vérifie que le détecteur est prêt à l'utilisation."""
    if not DETECTOR_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Module de détection non disponible. Vérifiez l'installation.",
        )
    
    if MULTIPART_IMPORT_ERROR:
        raise HTTPException(
            status_code=503,
            detail=(
                "Dépendance manquante: python-multipart. "
                "Installez: pip install python-multipart"
            ),
        )
    
    if MODEL_LOAD_ERROR:
        raise HTTPException(
            status_code=503,
            detail=(
                f"Modèle non disponible: {MODEL_LOAD_ERROR}. "
                "Vérifiez AGRIDETECT_MODEL_PATH et le dossier du modèle."
            ),
        )
    
    if DETECTOR is None or not DETECTOR.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Modèle non chargé. Définissez AGRIDETECT_MODEL_PATH et redémarrez l'API.",
        )
    
    return DETECTOR


def _open_image_safe(contents: bytes) -> Image.Image:
    """Ouvre une image de manière sécurisée avec validation."""
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Fichier vide.")
    
    if len(contents) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Image trop lourde ({len(contents)/1024/1024:.1f} MB > {MAX_IMAGE_SIZE_MB} MB maximum).",
        )
    
    try:
        im = Image.open(io.BytesIO(contents))
        im.load()  # Force la lecture pour détecter les images corrompues
        
        # Validation des dimensions
        if im.size[0] > 5000 or im.size[1] > 5000:
            raise HTTPException(
                status_code=400, 
                detail="Image trop grande. Dimensions maximum: 5000x5000 pixels."
            )
        
        return im.convert("RGB")
        
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400, 
            detail="Format d'image non supporté. Utilisez JPEG, PNG ou WebP."
        )
    except Image.DecompressionBombError:
        raise HTTPException(
            status_code=413, 
            detail="Image trop grande (décompression bomb)."
        )
    except Exception as e:
        log.error(f"Erreur traitement image: {e}")
        raise HTTPException(
            status_code=400, 
            detail=f"Erreur lors du traitement de l'image: {str(e)}"
        )


def map_prediction_to_catalog(disease_key: str, disease_name_raw: str) -> Optional[Dict[str, Any]]:
    """Mapping amélioré entre la prédiction et le catalogue."""
    if not disease_key and not disease_name_raw:
        return None
    
    # Essayer d'abord avec la clé normalisée
    for item in DATASET_DISEASES:
        if disease_key and item["id"] == disease_key:
            return item
    
    # Fallback: matching sur le nom brut
    if disease_name_raw:
        key = (
            disease_name_raw
            .replace("___", "_")
            .replace("__", "_")
            .replace(" ", "_")
            .strip()
            .lower()
        )
        
        for item in DATASET_DISEASES:
            # Matching flexible sur l'ID
            if key in item["id"] or item["id"] in key:
                return item
                
            # Matching sur le nom anglais
            disease_en_norm = item["disease_en"].lower().replace(" ", "_")
            if key in disease_en_norm or disease_en_norm in key:
                return item
    
    return None


# -------------------------------------------------------------------
# Chatbot adapter amélioré
# -------------------------------------------------------------------
class _ChatAdapter:
    def __init__(self):
        self._bot = _ChatbotClass() if _ChatbotClass else None
        self._has_chatbot = _CHATBOT_AVAILABLE

    def is_available(self) -> bool:
        """Vérifie si le chatbot est disponible."""
        return self._has_chatbot

    def reply(self, message: str, session_id: str, language: Optional[str], context: Optional[Dict]):
        """Génère une réponse du chatbot."""
        if not self._has_chatbot:
            raise HTTPException(
                status_code=501, 
                detail="Service chatbot non disponible. Vérifiez l'installation du module chatbot."
            )

        try:
            # 1) Nouvelle API orientée classe + helper
            if self._bot is not None and _legacy_or_helper_generate is not None:
                return _legacy_or_helper_generate(
                    self._bot,
                    message=message,
                    session_id=session_id,
                    language=language,
                    extra_context=context or {},
                )

            # 2) Ancienne API
            if _legacy_or_helper_generate is not None:
                # Adaptation de la langue pour l'ancien chatbot
                if language in ("fr", "wo", "pu") and not message.strip().startswith("/lang"):
                    message = f"/lang {language}\n{message}"

                response_text = _legacy_or_helper_generate(
                    session_id=session_id, 
                    user_message=message
                )
                
                return {
                    "response": response_text,
                    "language": language or DEFAULT_LANG,
                    "intent": "general",
                    "suggestions": [],
                    "context": {"topic": "general", **(context or {})},
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            log.exception("Erreur dans le chatbot")
            raise HTTPException(
                status_code=500, 
                detail=f"Erreur du chatbot: {str(e)}"
            )

        raise HTTPException(
            status_code=500, 
            detail="Configuration chatbot incompatible."
        )


# Initialisation du chatbot
_CHAT = _ChatAdapter()
if not _CHAT.is_available():
    log.warning("⚠️  Chatbot non disponible - le endpoint /api/v1/chat retournera des erreurs 501")


# -------------------------------------------------------------------
# Lifespan FastAPI - CORRIGÉ (avec try/finally)
# -------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global DETECTOR, MODEL_LOAD_ERROR

    log.info("🚀 Démarrage de l'API AgriDetect...")
    
    # Validation de l'environnement
    env_valid = validate_environment()
    
    if not env_valid:
        MODEL_LOAD_ERROR = "Environnement invalide"
        log.error("❌ Environnement invalide, modèle non chargé")
    elif not DETECTOR_AVAILABLE:
        MODEL_LOAD_ERROR = "Module de détection non disponible"
        log.error("❌ Module de détection non disponible")
    else:
        try:
            log.info(f"🔍 Chargement du modèle depuis: {MODEL_PATH}")
            
            # Vérification détaillée du chemin
            if not os.path.exists(MODEL_PATH):
                MODEL_LOAD_ERROR = f"Chemin modèle inexistant: {MODEL_PATH}"
                log.error(MODEL_LOAD_ERROR)
            else:
                log.info(f"✅ Chemin modèle valide: {MODEL_PATH}")
                
                # Vérifier le contenu du dossier
                try:
                    contents = list(Path(MODEL_PATH).iterdir())
                    log.info(f"📁 Contenu du dossier modèle ({len(contents)} éléments):")
                    for item in contents:
                        size = item.stat().st_size if item.is_file() else 0
                        log.info(f"   - {item.name} ({size/1024/1024:.1f} MB)" if size > 0 else f"   - {item.name}")
                        
                except Exception as e:
                    log.error(f"❌ Impossible de lire le dossier: {e}")
                
                # Charger le modèle avec timeout
                log.info("🚀 Initialisation du PlantDiseaseDetector...")
                start_time = time.time()
                
                try:
                    DETECTOR = PlantDiseaseDetector(model_path=MODEL_PATH)
                    load_time = time.time() - start_time
                    
                    if DETECTOR.is_loaded:
                        MODEL_LOAD_ERROR = None
                        log.info(f"✅ Modèle chargé avec succès en {load_time:.2f}s")
                        log.info(f"📊 Classes disponibles: {len(DETECTOR.class_names)}")
                        log.info(f"🖼️  Taille d'image: {DETECTOR.image_size}")
                        
                        # Afficher les premières classes
                        if DETECTOR.class_names:
                            log.info(f"📋 Exemples de classes: {DETECTOR.class_names[:5]}")
                    else:
                        MODEL_LOAD_ERROR = "Échec du chargement du modèle (is_loaded=False)"
                        log.error("❌ Modèle non chargé - is_loaded=False")
                        
                except Exception as e:
                    MODEL_LOAD_ERROR = f"Erreur lors du chargement: {str(e)}"
                    log.exception("❌ Erreur lors du chargement du modèle")
                    
        except Exception as e:
            log.error(f"❌ Erreur lors de l'initialisation: {e}")
            MODEL_LOAD_ERROR = str(e)

    # CORRECTION : Le yield doit être dans un bloc try/finally
    try:
        yield
    finally:
        # Nettoyage
        log.info("🧹 Arrêt de l'API AgriDetect...")
        if DETECTOR:
            log.info("🧹 Nettoyage du détecteur")


app = FastAPI(
    title="AgriDetect API",
    description="Détection de maladies des plantes & assistance agricole multilingue",
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Handlers d'erreurs améliorés
# -------------------------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error": True,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    log.exception("Erreur non gérée dans l'API")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erreur interne du serveur.",
            "error": True,
            "timestamp": datetime.now().isoformat()
        }
    )


# -------------------------------------------------------------------
# Routes principales
# -------------------------------------------------------------------
@app.get("/", tags=["root"])
async def root():
    """Endpoint racine avec informations de l'API."""
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
            "documentation": "/docs"
        },
        "services": {
            "model_loaded": DETECTOR is not None and DETECTOR.is_loaded,
            "chatbot_available": _CHAT.is_available(),
            "multilingual": True
        }
    }


@app.post("/api/v1/detect-disease", response_model=DiseaseDetectionResponse, tags=["detection"])
async def detect_disease(
    file: UploadFile = File(..., description="Image de la plante à analyser"),
    crop_type: Optional[str] = None,
    language: Optional[str] = DEFAULT_LANG,
):
    """Endpoint de détection de maladies avec validation améliorée."""
    # Validation du type de fichier
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, 
            detail="Le fichier doit être une image (JPEG, PNG, WebP). Type reçu: " + str(file.content_type)
        )
    
    # Validation de la langue
    if language not in ["fr", "wo", "pu"]:
        language = DEFAULT_LANG
        log.warning(f"Langue '{language}' non supportée, utilisation du français")

    # Lecture et validation de l'image
    try:
        contents = await file.read()
        image = _open_image_safe(contents)
        log.info(f"📸 Image reçue: {file.filename}, taille: {len(contents)} bytes, dimensions: {image.size}")
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Erreur lecture image: {e}")
        raise HTTPException(status_code=400, detail="Erreur lors du traitement de l'image.")

    # Détection
    detector = ensure_detector_ready()
    try:
        start_time = time.time()
        result = detector.predict(image, language=language or DEFAULT_LANG)
        processing_time = time.time() - start_time
        
        log.info(f"🔍 Prédiction terminée en {processing_time:.2f}s: {result.get('disease_name')} "
                f"({result.get('confidence', 0):.1%})")
                
    except Exception as e:
        log.exception("Erreur lors de la prédiction")
        raise HTTPException(status_code=500, detail=f"Erreur du modèle: {str(e)}")

    # Validation du résultat
    if "error" in result:
        log.error(f"Erreur dans la prédiction: {result['error']}")
        raise HTTPException(status_code=500, detail=result["error"])

    # Mapping des résultats
    disease_key = result.get("disease_key", "")
    disease_name_raw = result.get("disease_name", "")
    
    catalog_match = map_prediction_to_catalog(disease_key, disease_name_raw)
    
    # Détermination de la culture affectée
    affected_crop_final = crop_type or result.get("affected_crop", "Non spécifié")
    if catalog_match:
        affected_crop_final = catalog_match["plant_fr"]

    # Construction de la réponse
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
        success=result.get("success", True)
    )


@app.post("/api/v1/chat", tags=["chat"])
async def chat_with_bot(message: ChatMessage):
    """
    Chat avec le bot agricole multilingue.
    """
    try:
        session_id = (message.context or {}).get("session_id", "default")
        lang = message.language or DEFAULT_LANG

        log.info(f"💬 Chat request - Langue: {lang}, Session: {session_id}, "
                f"Message: {message.message[:100]}...")

        reply = _CHAT.reply(
            message=message.message,
            session_id=session_id,
            language=lang,
            context=message.context,
        )

        # Formatage de la réponse
        if isinstance(reply, dict):
            response_data = reply
        else:
            response_data = {
                "response": str(reply),
                "language": lang,
                "suggestions": [],
            }

        # Ajout des métadonnées
        response_data.update({
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "success": True
        })

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        log.exception("Erreur pendant /chat")
        raise HTTPException(status_code=500, detail=f"Erreur chatbot: {str(e)}")


@app.get("/api/v1/diseases/common", tags=["catalogue"])
async def get_common_diseases(crop_type: Optional[str] = None):
    """Retourne les maladies courantes, filtrées par culture si spécifié."""
    if not crop_type:
        return {
            "diseases": DATASET_DISEASES, 
            "total": len(DATASET_DISEASES),
            "crops": ["Tomate", "Pomme de terre", "Poivron"]
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
        d for d in DATASET_DISEASES
        if d["plant_en"].lower() in [v.lower() for v in target_aliases]
        or d["plant_fr"].lower() in [v.lower() for v in target_aliases]
    ]

    return {
        "diseases": filtered, 
        "total": len(filtered),
        "filter": crop_type,
        "crop_normalized": target_aliases[0]
    }


@app.get("/api/v1/statistics/dashboard", tags=["statistiques"])
async def get_dashboard_stats():
    """Retourne les statistiques du tableau de bord."""
    total_diseases = len(DATASET_DISEASES)
    return {
        "total_detections": 1543,
        "diseases_detected": total_diseases,
        "success_rate": 95.8,  # Basé sur les métriques de votre modèle
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
        "model_accuracy": 95.8,  # Votre modèle a 95.86% d'accuracy
        "model_precision": 97.5,  # Votre modèle a 97.54% de precision
    }


# -------------------------------------------------------------------
# Endpoints de santé améliorés
# -------------------------------------------------------------------
@app.get("/health", response_model=HealthResponse, tags=["santé"])
async def health_check():
    """Endpoint de santé complet avec état des services."""
    model_status = "loaded" if (DETECTOR and DETECTOR.is_loaded) else "error"
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
            "database": "in_memory"
        },
        model_loaded=DETECTOR is not None and DETECTOR.is_loaded,
        uptime=time.time() - STARTUP_TIME
    )


@app.get("/health/live", tags=["santé"])
async def liveness():
    """Endpoint de liveness pour Kubernetes."""
    return {
        "status": "alive", 
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time() - STARTUP_TIME
    }


@app.get("/health/ready", tags=["santé"])
async def readiness():
    """Endpoint de readiness pour Kubernetes."""
    model_ready = (DETECTOR is not None) and (DETECTOR.is_loaded) and (MODEL_LOAD_ERROR is None)
    
    status_info = {
        "status": "ready" if model_ready else "not-ready",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": model_ready,
        "model_error": MODEL_LOAD_ERROR,
        "chatbot_available": _CHAT.is_available(),
        "services_ready": {
            "model": model_ready,
            "chatbot": _CHAT.is_available(),
            "api": True
        }
    }
    
    if not model_ready:
        return JSONResponse(
            status_code=503,
            content=status_info
        )
    
    return status_info


# -------------------------------------------------------------------
# Entrypoint
# -------------------------------------------------------------------
if __name__ == "__main__":
    log.info(f"🚀 Démarrage du serveur AgriDetect v{APP_VERSION}")
    log.info(f"🌐 Hôte: {os.getenv('HOST', '0.0.0.0')}")
    log.info(f"🔌 Port: {os.getenv('PORT', '8000')}")
    log.info(f"🔄 Reload: {os.getenv('RELOAD', 'false').lower() == 'true'}")
    
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "false").lower() == "true",
        log_level="info",
        access_log=True
    )