"""
model_predictor.py
Module de prédiction pour AgriDetect, adapté aux plantes/maladies réelles du dataset.
- Charge le modèle TF/Keras
- Lit metadata.json pour les labels
- Fait le mapping vers ton catalogue (maïs, tomate, pomme de terre, poivron/piment)
- Retourne le nom de maladie dans la langue demandée (fr / en / wo / pu)
"""

from __future__ import annotations

import os
import json
from typing import Dict, List, Tuple, Optional, Union

import numpy as np
from PIL import Image
import tensorflow as tf

PathLike = Union[str, os.PathLike]
ImageLike = Union[Image.Image, PathLike]


# ---------------------------------------------------------
# Catalogue réel (mêmes données que dans ton main.py)
# ---------------------------------------------------------
DATASET_DISEASES: List[Dict[str, str]] = [
    # 🌽 Corn / Maïs
    {
        "id": "corn_cercospora",
        "plant_en": "Corn (maize)",
        "plant_fr": "Maïs",
        "disease_en": "Cercospora leaf spot (Gray leaf spot)",
        "disease_fr": "Tache foliaire de la cercospora (tache grise)",
        "disease_wo": "Noppalu xeeru cercospora",
        "disease_pu": "Ñoppirde cercospora",
    },
    {
        "id": "corn_common_rust",
        "plant_en": "Corn (maize)",
        "plant_fr": "Maïs",
        "disease_en": "Common rust",
        "disease_fr": "Rouille commune",
        "disease_wo": "Ñakk ndoxmi ci mais",
        "disease_pu": "Ñoppirde ndiyam e mais",
    },
    {
        "id": "corn_northern_leaf_blight",
        "plant_en": "Corn (maize)",
        "plant_fr": "Maïs",
        "disease_en": "Northern leaf blight",
        "disease_fr": "Brûlure du feuillage nordique",
        "disease_wo": "Noppalu ñor ci mais",
        "disease_pu": "Ñoppirde gannal e mais",
    },
    {
        "id": "corn_healthy",
        "plant_en": "Corn (maize)",
        "plant_fr": "Maïs",
        "disease_en": "Healthy",
        "disease_fr": "Sain",
        "disease_wo": "Baax na",
        "disease_pu": "Ñammude",
    },

    # 🫑 Pepper / Poivron
    {
        "id": "pepper_bacterial_spot",
        "plant_en": "Pepper (bell)",
        "plant_fr": "Poivron",
        "disease_en": "Bacterial spot",
        "disease_fr": "Tache bactérienne",
        "disease_wo": "Noppalu bakteriya ci poivron",
        "disease_pu": "Ñoppirde bakteriya e poivron",
    },
    {
        "id": "pepper_healthy",
        "plant_en": "Pepper (bell)",
        "plant_fr": "Poivron",
        "disease_en": "Healthy",
        "disease_fr": "Sain",
        "disease_wo": "Baax na",
        "disease_pu": "Ñammude",
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
    },
    {
        "id": "potato_late_blight",
        "plant_en": "Potato",
        "plant_fr": "Pomme de terre",
        "disease_en": "Late blight",
        "disease_fr": "Brûlure tardive",
        "disease_wo": "Noppalu mu mujj ci pomme de terre",
        "disease_pu": "Ñoppirde mu mujj e pomme de terre",
    },
    {
        "id": "potato_healthy",
        "plant_en": "Potato",
        "plant_fr": "Pomme de terre",
        "disease_en": "Healthy",
        "disease_fr": "Sain",
        "disease_wo": "Baax na",
        "disease_pu": "Ñammude",
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
    },
    {
        "id": "tomato_early_blight",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Early blight",
        "disease_fr": "Brûlure précoce",
        "disease_wo": "Noppalu jëmmante ci tomate",
        "disease_pu": "Ñoppirde jango e tomate",
    },
    {
        "id": "tomato_late_blight",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Late blight",
        "disease_fr": "Brûlure tardive",
        "disease_wo": "Noppalu mu mujj ci tomate",
        "disease_pu": "Ñoppirde mu mujj e tomate",
    },
    {
        "id": "tomato_septoria_leaf_spot",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Septoria leaf spot",
        "disease_fr": "Tache foliaire de Septoria",
        "disease_wo": "Noppalu septoria ci tomate",
        "disease_pu": "Ñoppirde septoria e tomate",
    },
    {
        "id": "tomato_leaf_mold",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Leaf mold",
        "disease_fr": "Moisissure des feuilles",
        "disease_wo": "Ñakk ndoxmi ci nopp tomate",
        "disease_pu": "Ñoppirde ndiyam e tomate",
    },
    {
        "id": "tomato_spider_mites",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Spider mites (Two-spotted spider mite)",
        "disease_fr": "Acariens (tétranyque à deux points)",
        "disease_wo": "Ñiñ yu ñaar ci tomate",
        "disease_pu": "Wuroo ñaar e tomate",
    },
    {
        "id": "tomato_target_spot",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Target spot",
        "disease_fr": "Tache cible",
        "disease_wo": "Noppalu but ci tomate",
        "disease_pu": "Ñoppirde cuɓɓo e tomate",
    },
    {
        "id": "tomato_mosaic_virus",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Tomato mosaic virus",
        "disease_fr": "Virus de la mosaïque de la tomate",
        "disease_wo": "Wirusu mosaïque ci tomate",
        "disease_pu": "Wuroo mosaïque e tomate",
    },
    {
        "id": "tomato_yellow_leaf_curl_virus",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Tomato yellow leaf curl virus",
        "disease_fr": "Virus de l’enroulement jaune de la tomate",
        "disease_wo": "Wirusu ñuul yaram bu jëm ci tomate",
        "disease_pu": "Wuroo hoore leydi ñuul e tomate",
    },
    {
        "id": "tomato_healthy",
        "plant_en": "Tomato",
        "plant_fr": "Tomate",
        "disease_en": "Healthy",
        "disease_fr": "Sain",
        "disease_wo": "Baax na",
        "disease_pu": "Ñammude",
    },
]


def _norm(s: str) -> str:
    return s.strip().lower().replace("_", " ").replace("-", " ")


class PlantDiseaseDetector:
    """
    Version alignée avec ton API:
    - .predict(image, language=...) -> dict complet
    """

    def __init__(self, model_path: str, verbose: bool = True):
        self.model_path = model_path
        self.model: Optional[tf.keras.Model] = None
        self.metadata: Dict = {}
        self.class_names: Dict[int, str] = {}
        self.input_size: Tuple[int, int] = (224, 224)
        self.verbose = verbose

        self._load_model()
        self._load_metadata()
        self._infer_input_size_if_needed()

    # -------------------- chargement --------------------
    def _load_model(self) -> None:
        keras_file = os.path.join(self.model_path, "model.keras")
        h5_file = os.path.join(self.model_path, "model.h5")
        savedmodel_dir = os.path.join(self.model_path, "saved_model")

        if os.path.exists(keras_file):
            self.model = tf.keras.models.load_model(keras_file)
            src = keras_file
        elif os.path.exists(h5_file):
            self.model = tf.keras.models.load_model(h5_file)
            src = h5_file
        elif os.path.exists(savedmodel_dir):
            self.model = tf.keras.models.load_model(savedmodel_dir)
            src = savedmodel_dir
        else:
            raise FileNotFoundError(
                f"Aucun modèle trouvé dans {self.model_path} (model.keras, model.h5 ou saved_model/ attendus)"
            )

        if self.verbose:
            print(f"✓ Modèle chargé depuis: {src}")

    def _load_metadata(self) -> None:
        metadata_file = os.path.join(self.model_path, "metadata.json")
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f) or {}
                classes = self.metadata.get("classes") or {}
                if isinstance(classes, dict):
                    self.class_names = {int(k): v for k, v in classes.items()}
                elif isinstance(classes, list):
                    self.class_names = {i: name for i, name in enumerate(classes)}
                if self.verbose:
                    print(f"✓ Métadonnées chargées ({len(self.class_names)} classes)")
            except Exception as e:
                if self.verbose:
                    print(f"⚠ Impossible de lire metadata.json: {e}")
        else:
            if self.verbose:
                print("⚠ Pas de metadata.json, utilisation des labels internes du modèle")

    def _infer_input_size_if_needed(self) -> None:
        h = self.metadata.get("img_height")
        w = self.metadata.get("img_width")
        if isinstance(h, int) and isinstance(w, int) and h > 0 and w > 0:
            self.input_size = (h, w)
            return

        try:
            ishape = getattr(self.model, "input_shape", None)
            if ishape is not None:
                first = ishape[0] if isinstance(ishape, list) else ishape
                if len(first) >= 3:
                    H = first[-3] or 224
                    W = first[-2] or 224
                    self.input_size = (int(H), int(W))
                    if self.verbose:
                        print(f"ℹ Taille d'entrée déduite: {self.input_size}")
                    return
        except Exception:
            pass

        self.input_size = (224, 224)
        if self.verbose:
            print(f"ℹ Taille d'entrée par défaut: {self.input_size}")

    # -------------------- prétraitement --------------------
    def _ensure_pil(self, image: ImageLike) -> Image.Image:
        if isinstance(image, Image.Image):
            img = image
        else:
            img = Image.open(image)

        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        elif img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (0, 0, 0))
            bg.paste(img, mask=img.split()[-1])
            img = bg
        return img

    def preprocess_image(self, image: ImageLike) -> np.ndarray:
        img = self._ensure_pil(image)
        h, w = self.input_size
        img = img.resize((w, h), Image.BILINEAR)

        arr = np.asarray(img).astype("float32")
        if arr.ndim == 2:
            arr = np.stack([arr] * 3, axis=-1)
        if arr.shape[-1] == 4:
            arr = arr[..., :3]

        arr /= 255.0
        arr = np.expand_dims(arr, axis=0)
        return arr

    # -------------------- prédiction brute --------------------
    def _to_probabilities(self, preds: np.ndarray) -> np.ndarray:
        preds = preds.astype("float32")
        sums = preds.sum(axis=-1, keepdims=True)
        if np.all((preds >= -1e-6) & (preds <= 1.0 + 1e-6)) and np.all(np.abs(sums - 1.0) < 1e-3):
            return preds
        e = np.exp(preds - np.max(preds, axis=-1, keepdims=True))
        return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-8, None)

    def _predict_topk(self, image: ImageLike, top_k: int = 3) -> List[Dict]:
        batch = self.preprocess_image(image)
        raw = self.model.predict(batch, verbose=0)
        if isinstance(raw, list):
            raw = raw[0]
        raw = np.squeeze(raw)
        probs = self._to_probabilities(raw)

        k = int(max(1, min(top_k, probs.shape[-1])))
        top_idx = np.argsort(probs)[-k:][::-1]

        results = []
        for idx in top_idx:
            name = self.class_names.get(int(idx), f"class_{int(idx)}")
            results.append(
                {
                    "disease_id": f"disease_{int(idx)}",
                    "disease_name": name,
                    "confidence": float(probs[idx]),
                }
            )
        return results

    # -------------------- mapping vers ton catalogue --------------------
    def _match_catalog(self, model_label: str) -> Optional[Dict[str, str]]:
        """
        Essaie de faire correspondre le label du modèle avec une entrée du dataset.
        On compare surtout avec disease_en et un peu avec disease_fr.
        """
        if not model_label:
            return None

        key = _norm(model_label)

        # 1. correspondance stricte / partielle sur disease_en
        for item in DATASET_DISEASES:
            if key == _norm(item["disease_en"]) or _norm(item["disease_en"]) in key or key in _norm(item["disease_en"]):
                return item

        # 2. tentative côté français
        for item in DATASET_DISEASES:
            if key == _norm(item["disease_fr"]) or _norm(item["disease_fr"]) in key or key in _norm(item["disease_fr"]):
                return item

        return None

    # -------------------- API publique --------------------
    def predict(self, image: ImageLike, language: Optional[str] = None) -> Dict:
        """
        Appelée par /api/v1/detect-disease dans ton main.py
        """
        return self.detect_disease(image, language=language or "fr")

    def detect_disease(
        self,
        image: ImageLike,
        language: str = "fr",
        confidence_threshold: float = 0.7,
    ) -> Dict:
        preds = self._predict_topk(image, top_k=3)
        best = preds[0]
        confidence = float(best["confidence"])

        # niveau de sévérité basique
        if confidence >= 0.9:
            severity = "Élevée"
        elif confidence >= 0.7:
            severity = "Modérée"
        else:
            severity = "Faible"

        # on tente de faire correspondre la prédiction au catalogue réel
        catalog_entry = self._match_catalog(best["disease_name"])

        # pas assez sûr → on renvoie "Inconnu"
        if confidence < confidence_threshold and not catalog_entry:
            return {
                "disease_id": "disease_unknown",
                "disease_name": "Inconnu",
                "confidence": confidence,
                "severity": "Faible",
                "treatments": [
                    "Refaites une photo plus nette.",
                    "Évitez les ombres / contre-jour.",
                ],
                "prevention_tips": [
                    "Surveillez régulièrement vos plants.",
                    "Évitez l’humidité foliaire prolongée.",
                ],
                "affected_crop": "Non spécifié",
                "alternative_diagnoses": preds,
            }

        # si on a un match catalogue, on choisit le nom selon la langue
        if catalog_entry:
            if language == "wo":
                disease_name = catalog_entry["disease_wo"]
            elif language in ("pu", "pulaar"):
                disease_name = catalog_entry["disease_pu"]
            elif language == "en":
                disease_name = catalog_entry["disease_en"]
            else:
                disease_name = catalog_entry["disease_fr"]

            affected_crop = catalog_entry["plant_fr"]
        else:
            # pas trouvé dans le catalogue : on garde le nom du modèle
            disease_name = best["disease_name"]
            affected_crop = self._guess_crop_from_label(disease_name)

        return {
            "disease_id": catalog_entry["id"] if catalog_entry else best["disease_id"],
            "disease_name": disease_name,
            "confidence": confidence,
            "severity": severity,
            "treatments": self._get_treatments(disease_name),
            "prevention_tips": self._get_prevention_tips(disease_name),
            "affected_crop": affected_crop,
            "alternative_diagnoses": preds[1:],
        }

    # -------------------- connaissances basiques --------------------
    def _get_treatments(self, disease_name: str) -> List[Union[Dict, str]]:
        name = (disease_name or "").lower()

        if "bactér" in name or "bacterial" in name:
            return [
                {
                    "name": "Élimination des feuilles très atteintes",
                    "description": "Couper et détruire les parties malades pour limiter la propagation.",
                    "organic": True,
                },
                {
                    "name": "Traitement à base de cuivre",
                    "description": "Utiliser un produit cuprique homologué, suivant l’étiquette.",
                    "organic": True,
                },
            ]

        if "mildiou" in name or "late blight" in name or "early blight" in name or "brûlure" in name:
            return [
                {
                    "name": "Fongicide préventif",
                    "description": "Appliquer après pluie / forte humidité.",
                    "organic": False,
                },
                "Retirer les feuilles atteintes et améliorer l’aération.",
            ]

        if "rouille" in name or "rust" in name:
            return [
                {
                    "name": "Fongicide anti-rouille",
                    "description": "Intervenir au début des symptômes.",
                    "organic": False,
                }
            ]

        # défaut
        return [
            {
                "name": "Bonne hygiène de la parcelle",
                "description": "Éliminer les débris infectés, surveiller l’irrigation.",
                "organic": True,
            }
        ]

    def _get_prevention_tips(self, disease_name: str) -> List[str]:
        name = (disease_name or "").lower()
        if "mildiou" in name or "blight" in name:
            return [
                "Éviter d’arroser sur le feuillage.",
                "Espacer les plants pour bien aérer.",
                "Surveiller après les pluies.",
            ]
        if "bactér" in name or "bacterial" in name:
            return [
                "Utiliser des semences saines.",
                "Éviter les éclaboussures d’eau d’une plante à l’autre.",
            ]
        return [
            "Surveiller régulièrement vos cultures.",
            "Enlever les parties très atteintes.",
        ]

    def _guess_crop_from_label(self, label: str) -> str:
        label = (label or "").lower()
        if "tomato" in label or "tomate" in label:
            return "Tomate"
        if "potato" in label or "pomme de terre" in label:
            return "Pomme de terre"
        if "pepper" in label or "poivron" in label:
            return "Poivron"
        if "corn" in label or "maïs" in label or "mais" in label:
            return "Maïs"
        return "Non spécifié"


# ====================== test rapide ======================
if __name__ == "__main__":
    # adapte le chemin
    model_dir = "models/mon_modele"  # <-- mets ton dossier modèle ici
    det = PlantDiseaseDetector(model_dir, verbose=True)
    # det.predict("chemin/vers/image.jpg", language="wo")
    print("Module chargé ✅")
