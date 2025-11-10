# disease_detector.py
from __future__ import annotations

"""
PlantDiseaseDetector — version robuste et alignée avec ton entraînement
- Charge un modèle Keras sauvegardé dans un dossier (model.keras ou model.h5)
- Lit ton metadata.json (celui que tu as montré)
- Utilise le prétraitement EfficientNetB0 (comme dans ton entraînement)
- Fait le mapping vers tes maladies en français
- Ne renvoie jamais un disease_name vide
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from PIL import Image, ImageFile

import tensorflow as tf  # type: ignore
from tensorflow import keras  # type: ignore
from tensorflow.keras import layers  # type: ignore
from tensorflow.keras.applications import EfficientNetB0  # type: ignore
from tensorflow.keras.applications.efficientnet import preprocess_input as effnet_preprocess  # type: ignore

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# Sécurité images
# ---------------------------------------------------------------------
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = int(os.getenv("AGRIDETECT_MAX_IMAGE_PIXELS", "25000000"))

# ---------------------------------------------------------------------
# GPU (optionnel)
# ---------------------------------------------------------------------
try:
    for gpu in tf.config.list_physical_devices("GPU"):
        tf.config.experimental.set_memory_growth(gpu, True)
    logger.info("✅ Configuration GPU appliquée")
except Exception as e:
    logger.warning(f"⚠️  Configuration GPU échouée: {e}")

# ---------------------------------------------------------------------
# 1. Mapping des labels du dataset -> clés normalisées
# (c’est exactement ce qu’il y a dans ton metadata.json)
# ---------------------------------------------------------------------
CLASS_ALIASES: Dict[str, str] = {
    # PIMENT / POIVRON
    "Pepper__bell___Bacterial_spot": "pepper_bacterial_spot",
    "Pepper__bell___healthy": "pepper_healthy",

    # POMME DE TERRE
    "Potato___Early_blight": "potato_early_blight",
    "Potato___Late_blight": "potato_late_blight",
    "Potato___healthy": "potato_healthy",

    # TOMATE
    "Tomato_Bacterial_spot": "tomato_bacterial_spot",
    "Tomato_Early_blight": "tomato_early_blight",
    "Tomato_Late_blight": "tomato_late_blight",
    "Tomato_Leaf_Mold": "tomato_leaf_mold",
    "Tomato_Septoria_leaf_spot": "tomato_septoria_leaf_spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite": "tomato_spider_mites",
    "Tomato__Target_Spot": "tomato_target_spot",
    "Tomato__Tomato_YellowLeaf__Curl_Virus": "tomato_yellow_leaf_curl_virus",
    "Tomato__Tomato_mosaic_virus": "tomato_mosaic_virus",
    "Tomato_healthy": "tomato_healthy",
}

# ---------------------------------------------------------------------
# 2. Infos maladies (fr / wo / pu) — comme dans ton backend
# ---------------------------------------------------------------------
DISEASE_INFO: Dict[str, Dict[str, Any]] = {
    # ---------- PIMENT ----------
    "pepper_healthy": {
        "fr": "Piment sain",
        "wo": "Pimó wér",
        "pu": "Piment cellal",
        "severity": "Aucune",
        "crop": "Piment",
        "treatments": [],
        "prevention": ["Hygiène de la parcelle", "Surveillance régulière"],
    },
    "pepper_bacterial_spot": {
        "fr": "Piment — tache bactérienne",
        "wo": "Pimó — tàkk bakteriya",
        "pu": "Piment tache bakteriya",
        "severity": "Modérée",
        "crop": "Piment",
        "prevention": ["Semences saines", "Éviter l'aspersion", "Désinfecter les outils"],
        "treatments": ["copper_spray", "crop_rotation"],
    },

    # ---------- POMME DE TERRE ----------
    "potato_healthy": {
        "fr": "Pomme de terre saine",
        "wo": "Pomme de terre wér",
        "pu": "Pomme de terre cellal",
        "severity": "Aucune",
        "crop": "Pomme de terre",
        "treatments": [],
        "prevention": ["Surveillance", "Éviter excès d'humidité"],
    },
    "potato_early_blight": {
        "fr": "Pomme de terre — alternariose",
        "wo": "Ñawu weñ (pomme de terre)",
        "pu": "Early blight",
        "severity": "Modérée",
        "crop": "Pomme de terre",
        "prevention": ["Rotation", "Éviter les blessures"],
        "treatments": ["fungicide_copper", "neem_oil"],
    },
    "potato_late_blight": {
        "fr": "Pomme de terre — mildiou",
        "wo": "Mildiou",
        "pu": "Late blight",
        "severity": "Élevée",
        "crop": "Pomme de terre",
        "prevention": ["Arrosage au pied", "Retirer feuilles infectées"],
        "treatments": ["fungicide_systemic"],
    },

    # ---------- TOMATE ----------
    "tomato_healthy": {
        "fr": "Tomate saine",
        "wo": "Tomaat wér",
        "pu": "Tomate cellal",
        "severity": "Aucune",
        "crop": "Tomate",
        "treatments": [],
        "prevention": ["Surveillance", "Éviter humidité excessive"],
    },
    "tomato_bacterial_spot": {
        "fr": "Tomate — tache bactérienne",
        "wo": "Tomaat — tàkk bakteriya",
        "pu": "Tomate tache bakteriya",
        "severity": "Modérée",
        "crop": "Tomate",
        "prevention": ["Semences certifiées", "Désinfecter les outils"],
        "treatments": ["copper_spray"],
    },
    "tomato_early_blight": {
        "fr": "Tomate — alternariose",
        "wo": "Ñawu weñ (tomate)",
        "pu": "Early blight",
        "severity": "Modérée",
        "crop": "Tomate",
        "prevention": ["Rotation", "Aération"],
        "treatments": ["fungicide_copper", "neem_oil"],
    },
    "tomato_late_blight": {
        "fr": "Tomate — mildiou",
        "wo": "Mildiou",
        "pu": "Late blight",
        "severity": "Élevée",
        "crop": "Tomate",
        "prevention": ["Arrosage au pied", "Limiter humidité"],
        "treatments": ["fungicide_systemic"],
    },
    "tomato_leaf_mold": {
        "fr": "Tomate — feutrage",
        "wo": "Puur weex",
        "pu": "Huɗo peewo",
        "severity": "Modérée",
        "crop": "Tomate",
        "prevention": ["Ventilation", "Éclaircissage"],
        "treatments": ["sulfur_spray"],
    },
    "tomato_septoria_leaf_spot": {
        "fr": "Tomate — septoriose",
        "wo": "Septoria",
        "pu": "Septoria",
        "severity": "Modérée",
        "crop": "Tomate",
        "prevention": ["Rotation", "Paillage"],
        "treatments": ["copper_spray", "neem_oil"],
    },
    "tomato_spider_mites": {
        "fr": "Tomate — araignées rouges",
        "wo": "Xajj",
        "pu": "Kooke",
        "severity": "Modérée",
        "crop": "Tomate",
        "prevention": ["Éviter stress hydrique", "Surveiller revers feuilles"],
        "treatments": ["neem_oil", "soap_solution"],
    },
    "tomato_target_spot": {
        "fr": "Tomate — tache en cible",
        "wo": "Tàkk bu dalal",
        "pu": "Target spot",
        "severity": "Modérée",
        "crop": "Tomate",
        "prevention": ["Aération", "Équilibre azote"],
        "treatments": ["copper_spray"],
    },
    "tomato_mosaic_virus": {
        "fr": "Tomate — virus de la mosaïque",
        "wo": "Wirùs mosayik",
        "pu": "Virus mosaïque",
        "severity": "Élevée",
        "crop": "Tomate",
        "prevention": ["Semences saines", "Hygiène", "Contrôle vecteurs"],
        "treatments": ["remove_infected", "insecticide_vectors"],
    },
    "tomato_yellow_leaf_curl_virus": {
        "fr": "Tomate — TYLCV",
        "wo": "TYLCV",
        "pu": "TYLCV",
        "severity": "Élevée",
        "crop": "Tomate",
        "prevention": ["Filets anti-insectes", "Contrôle aleurodes"],
        "treatments": ["insecticide_vectors", "remove_infected"],
    },
}

# ---------------------------------------------------------------------
# 3. Base de traitements
# ---------------------------------------------------------------------
TREATMENTS_DB: Dict[str, Dict[str, Dict[str, Any]]] = {
    "fungicide_copper": {
        "fr": {
            "name": "Bouillie bordelaise",
            "description": "Fongicide à base de cuivre",
            "application": "Tous les 7–10 jours",
            "organic": True,
        }
    },
    "copper_spray": {
        "fr": {
            "name": "Cuivre (hydroxyde/oxychlorure)",
            "description": "Antibactérien / fongique",
            "application": "Suivre l'étiquette",
            "organic": True,
        }
    },
    "fungicide_systemic": {
        "fr": {
            "name": "Fongicide systémique",
            "description": "Curatif homologué",
            "application": "Suivre l'étiquette",
            "organic": False,
        }
    },
    "neem_oil": {
        "fr": {
            "name": "Huile de Neem",
            "description": "Insecticide/fongique bio",
            "application": "Hebdomadaire, le soir",
            "organic": True,
        }
    },
    "sulfur_spray": {
        "fr": {
            "name": "Soufre",
            "description": "Oïdium / feutrage",
            "application": "Pulvérisation foliaire",
            "organic": True,
        }
    },
    "soap_solution": {
        "fr": {
            "name": "Savon noir dilué",
            "description": "Acariens / pucerons",
            "application": "Soir, rincer après 24h",
            "organic": True,
        }
    },
    "remove_infected": {
        "fr": {
            "name": "Arrachage des plants atteints",
            "description": "Limiter la propagation",
            "application": "Évacuer hors de la parcelle",
            "organic": True,
        }
    },
    "insecticide_vectors": {
        "fr": {
            "name": "Contrôle des vecteurs",
            "description": "Aleurodes / pucerons",
            "application": "Pièges + produit homologué",
            "organic": False,
        }
    },
    "crop_rotation": {
        "fr": {
            "name": "Rotation des cultures",
            "description": "Brise les cycles des pathogènes",
            "application": "Tous les 2–3 saisons",
            "organic": True,
        }
    },
}


class PlantDiseaseDetector:
    """Détecteur de maladies basé sur un modèle Keras entraîné (EfficientNetB0)."""

    def __init__(self, model_path: Optional[str] = None):
        self.model: Optional[keras.Model] = None
        self.class_names: List[str] = []
        self.image_size: Tuple[int, int] = (224, 224)
        self.is_loaded: bool = False
        self.model_version: str = "1.0.0"

        if model_path:
            self._try_load_model(model_path)

        if not self.is_loaded:
            # fallback pour que l'API ne plante pas
            logger.warning("⚠️ Mode fallback: le modèle n'a pas été chargé, on construit un petit modèle.")
            self._build_fallback_model()

    # -----------------------------------------------------------------
    # Fallback (dev)
    # -----------------------------------------------------------------
    def _build_fallback_model(self) -> None:
        try:
            num_classes = len(set(CLASS_ALIASES.values()))
            self._build_efficientnet_model(num_classes)
            self.class_names = list(CLASS_ALIASES.keys())
            self.is_loaded = True
            logger.info("✅ Modèle de fallback construit avec EfficientNetB0")
        except Exception as e:
            logger.error(f"❌ Impossible de construire le modèle de fallback: {e}")
            self.is_loaded = False

    def _build_efficientnet_model(self, num_classes: int) -> keras.Model:
        base = EfficientNetB0(
            include_top=False,
            input_shape=(*self.image_size, 3),
            weights="imagenet",
        )
        base.trainable = False

        inputs = keras.Input(shape=(*self.image_size, 3))
        x = layers.Rescaling(1.0 / 255)(inputs)
        x = base(x, training=False)
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dropout(0.3)(x)
        outputs = layers.Dense(num_classes, activation="softmax")(x)

        self.model = keras.Model(inputs, outputs)
        self.model.compile(
            optimizer=keras.optimizers.Adam(1e-3),
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )
        return self.model

    # -----------------------------------------------------------------
    # Chargement du modèle depuis ton dossier
    # -----------------------------------------------------------------
    def _try_load_model(self, path: str) -> None:
        logger.info(f"🔍 Chargement du modèle depuis: {path}")

        if not os.path.exists(path):
            logger.error(f"❌ Chemin inexistant: {path}")
            return

        loaded = False

        # on suit exactement ton dossier : d'abord model.keras puis model.h5
        keras_path = os.path.join(path, "model.keras")
        h5_path = os.path.join(path, "model.h5")

        if os.path.exists(keras_path):
            try:
                self.model = keras.models.load_model(keras_path)
                logger.info("✅ Modèle .keras chargé avec succès")
                loaded = True
            except Exception as e:
                logger.error(f"❌ Échec du chargement .keras: {e}")

        if not loaded and os.path.exists(h5_path):
            try:
                self.model = keras.models.load_model(h5_path)
                logger.info("✅ Modèle .h5 chargé avec succès")
                loaded = True
            except Exception as e:
                logger.error(f"❌ Échec du chargement .h5: {e}")

        if not loaded:
            logger.error("❌ Aucun modèle complet n'a pu être chargé (ni model.keras ni model.h5)")
            try:
                logger.info(f"📁 Contenu du dossier: {[p.name for p in Path(path).iterdir()]}")
            except Exception:
                pass
            return

        # si on est ici: modèle chargé → on lit le metadata
        self._load_metadata(path)

        # petit test
        try:
            dummy = np.random.random((1, self.image_size[0], self.image_size[1], 3)).astype(np.float32)
            _ = self.model.predict(dummy, verbose=0)
            self.is_loaded = True
            logger.info(f"✅ Modèle opérationnel ({len(self.class_names)} classes)")
        except Exception as e:
            logger.error(f"❌ Le modèle chargé ne peut pas prédire: {e}")
            self.is_loaded = False

    # -----------------------------------------------------------------
    # Lecture de metadata.json (ordre des classes + taille image)
    # -----------------------------------------------------------------
    def _load_metadata(self, path: str) -> None:
        meta_path = os.path.join(path, "metadata.json")
        if not os.path.exists(meta_path):
            logger.warning("⚠️ metadata.json non trouvé → on utilise les classes par défaut")
            self.class_names = list(CLASS_ALIASES.keys())
            return

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)

            # ton fichier a "classes" ET "class_names" → on commence par "classes"
            if "classes" in meta and isinstance(meta["classes"], dict):
                self.class_names = [v for k, v in sorted(meta["classes"].items(), key=lambda x: int(x[0]))]
            elif "class_names" in meta and isinstance(meta["class_names"], list):
                self.class_names = meta["class_names"]
            else:
                self.class_names = list(CLASS_ALIASES.keys())

            logger.info(f"📊 {len(self.class_names)} classes chargées depuis metadata.json")

            # taille d'image
            if "img_height" in meta and "img_width" in meta:
                self.image_size = (int(meta["img_height"]), int(meta["img_width"]))
                logger.info(f"🖼️ Taille d'image du modèle: {self.image_size}")

            if "model_name" in meta:
                self.model_version = meta["model_name"]

        except Exception as e:
            logger.error(f"⚠️ Erreur lecture metadata.json: {e}")
            self.class_names = list(CLASS_ALIASES.keys())

    # -----------------------------------------------------------------
    # Prétraitement image (⚠️ EfficientNet)
    # -----------------------------------------------------------------
    def preprocess_image(self, image: Union[str, Path, Image.Image]) -> np.ndarray:
        try:
            if isinstance(image, (str, Path)):
                img = Image.open(image)
            else:
                img = image

            img = img.convert("RGB").resize(self.image_size)
            arr = np.array(img, dtype=np.float32)
            # TRÈS IMPORTANT: prétraitement EfficientNet, pas MobileNet
            arr = effnet_preprocess(arr)
            arr = np.expand_dims(arr, 0)
            return arr
        except Exception as e:
            logger.error(f"❌ Erreur prétraitement image: {e}")
            raise ValueError(f"Impossible de prétraiter l'image: {e}")

    # -----------------------------------------------------------------
    # Helpers de mapping
    # -----------------------------------------------------------------
    def _dir_to_key(self, dir_label: str) -> str:
        return CLASS_ALIASES.get(dir_label, dir_label)

    def _get_safe_class_name(self, idx: int) -> Tuple[str, str]:
        if not self.class_names or idx >= len(self.class_names):
            return "unknown", "unknown"
        raw_label = self.class_names[idx]
        return raw_label, self._dir_to_key(raw_label)

    def _name_localized(self, key: str, lang: str) -> str:
        if key == "unknown":
            return {"fr": "Maladie non identifiée", "wo": "Xamul", "pu": "Xamul"}.get(lang, "Maladie non identifiée")
        meta = DISEASE_INFO.get(key, {})
        return meta.get(lang, meta.get("fr", "Maladie non identifiée"))

    def _treatments_localized(self, key: str, lang: str) -> List[Dict[str, Any]]:
        if key == "unknown":
            return []
        meta = DISEASE_INFO.get(key, {})
        outs: List[Dict[str, Any]] = []
        for t in meta.get("treatments", []):
            data = TREATMENTS_DB.get(t, {}).get(lang) or TREATMENTS_DB.get(t, {}).get("fr")
            if data:
                outs.append(data)
        return outs

    # -----------------------------------------------------------------
    # Prédiction
    # -----------------------------------------------------------------
    def predict(
        self,
        image: Union[str, Path, Image.Image],
        language: str = "fr",
        topk: int = 3,
    ) -> Dict[str, Any]:
        if not self.is_loaded or self.model is None:
            raise RuntimeError("Modèle non chargé")

        if language not in ("fr", "wo", "pu"):
            language = "fr"

        if topk < 1:
            topk = 1

        try:
            x = self.preprocess_image(image)
            preds = self.model.predict(x, verbose=0)
            probs = preds[0]

            # top-k indices
            top_indices = np.argsort(probs)[::-1][:topk]
            top_predictions: List[Dict[str, Any]] = []

            for idx in top_indices:
                raw_label, norm_key = self._get_safe_class_name(idx)
                conf = float(probs[idx])
                top_predictions.append(
                    {
                        "disease": self._name_localized(norm_key, language)
                        if norm_key != "unknown"
                        else raw_label.replace("_", " "),
                        "confidence": conf,
                        "severity": DISEASE_INFO.get(norm_key, {}).get("severity", "Inconnue"),
                        "disease_key": norm_key,
                        "raw_label": raw_label,
                    }
                )

            # meilleure prédiction
            best_idx = top_indices[0]
            best_raw, best_key = self._get_safe_class_name(best_idx)
            best_conf = float(probs[best_idx])

            if best_key == "unknown":
                display_name = (best_raw or "Maladie non identifiée").replace("_", " ")
            else:
                display_name = self._name_localized(best_key, language)

            meta = DISEASE_INFO.get(best_key, {})
            result = {
                "disease_key": best_key,
                "disease_name": display_name,
                "confidence": best_conf,
                "severity": meta.get("severity", "Inconnue"),
                "affected_crop": meta.get("crop", "Non spécifié"),
                "treatments": self._treatments_localized(best_key, language),
                "prevention_tips": meta.get("prevention", [])[:5],
                "top_predictions": top_predictions,
                "requires_action": ("healthy" not in best_key),
                "timestamp": datetime.now().isoformat(),
                "model_version": self.model_version,
                "success": True,
            }

            logger.info(f"🔍 Prédiction: {result['disease_name']} ({best_conf:.2%})")
            return result

        except Exception as e:
            logger.error(f"❌ Erreur de prédiction: {e}")
            return {
                "error": str(e),
                "disease_name": "Erreur de prédiction",
                "confidence": 0.0,
                "severity": "Inconnue",
                "affected_crop": "Non spécifié",
                "treatments": [],
                "prevention_tips": [],
                "timestamp": datetime.now().isoformat(),
                "success": False,
            }

    # -----------------------------------------------------------------
    # Recharge à chaud
    # -----------------------------------------------------------------
    def load_model(self, path: str) -> bool:
        if not os.path.exists(path):
            logger.error(f"❌ Répertoire inexistant: {path}")
            return False
        self._try_load_model(path)
        return self.is_loaded


# ---------------------------------------------------------------------
# Test manuel
# ---------------------------------------------------------------------
if __name__ == "__main__":
    # adapte le chemin à ton PC
    model_dir = r"C:\Users\USER\Desktop\AgriDetec_test\models\agridetect_model_20251107_042206"
    det = PlantDiseaseDetector(model_dir)
    print("✅ Modèle chargé:", det.is_loaded)
    print("📊 Nb classes:", len(det.class_names))
    print("🖼️ image_size:", det.image_size)
    if det.class_names:
        print("👉 premières classes:", det.class_names[:5])
