#!/usr/bin/env python3
"""
Test rapide du modèle AgriDetect.

Exemples:
  python test_model.py --model models/agridetect
  python test_model.py --model models/agridetect --image data/test/Tomato___healthy/001.jpg
  python test_model.py --model models/agridetect --dir data/test/Tomato___Late_blight
  python test_model.py --model models/agridetect --dir data/test --topk 5 --threshold 0.6

Compatibilité: utilise PlantDiseaseDetector (disease_detector.py)
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Iterable, List, Dict, Any, Optional
from PIL import Image
from disease_detector import PlantDiseaseDetector

# Extensions d’images autorisées
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


# ------------------------------------------------------------
# Utilitaires
# ------------------------------------------------------------
def iter_images(root: Path) -> Iterable[Path]:
    """Itère récursivement sur les images valides."""
    if root.is_file() and root.suffix.lower() in IMG_EXTS:
        yield root
        return
    if root.is_dir():
        for p in root.rglob("*"):
            if p.is_file() and not p.name.startswith(".") and p.suffix.lower() in IMG_EXTS:
                yield p


def pick_first_image(path: Path) -> Optional[Path]:
    """Renvoie la première image trouvée dans un dossier."""
    for img in iter_images(path):
        return img
    return None


def print_header(title: str) -> None:
    bar = "=" * max(20, len(title))
    print(f"\n{bar}\n{title}\n{bar}\n")


def format_pct(x: float) -> str:
    try:
        return f"{100.0 * float(x):.2f}%"
    except Exception:
        return "—"


# ------------------------------------------------------------
# Conversion des résultats
# ------------------------------------------------------------
def decide_from_predict(pred: Dict[str, Any], threshold: float, topk: int) -> Dict[str, Any]:
    """Formate la sortie `predict()` pour affichage lisible / JSON."""
    name = pred.get("disease_name", "—")
    conf = float(pred.get("confidence", 0.0))
    severity = pred.get("severity", "—")
    crop = pred.get("affected_crop", "—")
    topn = pred.get("top_3_predictions", []) or []

    alt = []
    for i, p in enumerate(topn):
        # ignore la 1ère si identique
        if i == 0 and p.get("disease") == name:
            continue
        alt.append({
            "disease_name": p.get("disease", "—"),
            "confidence": float(p.get("confidence", 0.0)),
            "severity": p.get("severity", "—"),
        })

    return {
        "disease_key": pred.get("disease_key", "unknown"),
        "disease_name": name,
        "confidence": conf,
        "severity": severity,
        "affected_crop": crop,
        "treatments": pred.get("treatments", []),
        "prevention_tips": pred.get("prevention_tips", []),
        "alternative_diagnoses": alt[: max(0, topk - 1)],
        "requires_action": bool(pred.get("requires_action", True)),
        "top_n": topn,
    }


# ------------------------------------------------------------
# Programme principal
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Test rapide du modèle AgriDetect")
    parser.add_argument("--model", type=Path, required=True,
                        help="Dossier contenant model.h5|model.keras et metadata.json.")
    parser.add_argument("--image", type=Path, help="Image unique à tester")
    parser.add_argument("--dir", type=Path, help="Dossier d’images à parcourir")
    parser.add_argument("--lang", default="fr", help="Langue de sortie (fr|wo|pu)")
    parser.add_argument("--topk", type=int, default=3, help="Nombre de prédictions à afficher")
    parser.add_argument("--threshold", type=float, default=0.7, help="Seuil de confiance principale")
    parser.add_argument("--json", action="store_true", help="Sortie JSON compacte (pour CI/scripts)")
    args = parser.parse_args()

    # -------------------- Vérification modèle --------------------
    model_path: Path = args.model
    if not model_path.exists():
        print(f"❌ Modèle introuvable: {model_path}", file=sys.stderr)
        sys.exit(2)

    print(f"🔧 Chargement du modèle depuis {model_path} ...")
    try:
        detector = PlantDiseaseDetector(str(model_path))
        print("✅ Modèle chargé !")
        print(f"📊 Nombre de classes: {len(detector.class_names)}")
    except Exception as e:
        print(f"❌ Erreur lors du chargement du modèle: {e}", file=sys.stderr)
        sys.exit(1)

    # -------------------- Sélection image --------------------
    chosen: Optional[Path] = None
    if args.image and args.image.exists():
        chosen = args.image
    elif args.dir and args.dir.exists():
        chosen = pick_first_image(args.dir)
    else:
        chosen = pick_first_image(Path("data/test"))

    if not chosen:
        print("⚠️ Aucune image trouvée (utilisez --image ou --dir)", file=sys.stderr)
        sys.exit(0)

    print(f"🧪 Image testée : {chosen}")

    # -------------------- Prédiction --------------------
    try:
        img = Image.open(chosen).convert("RGB")
        pred = detector.predict(img, language=args.lang, topk=max(1, args.topk))
    except Exception as e:
        print(f"❌ Erreur pendant predict(): {e}", file=sys.stderr)
        sys.exit(1)

    result = decide_from_predict(pred, threshold=args.threshold, topk=args.topk)

    # -------------------- Sortie JSON --------------------
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)

    # -------------------- Sortie texte --------------------
    print_header("📈 Top prédictions")
    topn = result.get("top_n", [])
    for i, p in enumerate(topn, start=1):
        print(f"  #{i:<2} {p.get('disease','—'):<36}  conf: {format_pct(p.get('confidence', 0.0))}  sev: {p.get('severity','—')}")

    print_header("🎯 Résultat principal")
    print(f"   Maladie:   {result['disease_name']}")
    print(f"   Confiance: {format_pct(result['confidence'])}")
    print(f"   Sévérité:  {result['severity']}")
    print(f"   Culture:   {result['affected_crop']}\n")

    trts = result.get("treatments", [])
    print("💊 Traitements :")
    if trts:
        for t in trts:
            if isinstance(t, dict):
                bio = " (bio)" if t.get("organic") else ""
                print(f"   - {t.get('name','Traitement')}{bio}: {t.get('description','')}")
            else:
                print(f"   - {t}")
    else:
        print("   — Aucun traitement disponible")

    tips = result.get("prevention_tips", [])
    print("\n🛡️ Prévention :")
    if tips:
        for tip in tips:
            print(f"   - {tip}")
    else:
        print("   — Aucun conseil disponible")

    alt = result.get("alternative_diagnoses", [])
    if alt:
        print("\n🔎 Alternatives possibles :")
        for a in alt:
            print(f"   • {a.get('disease_name','—'):<36}  conf: {format_pct(a.get('confidence',0.0))}")

    print("\n✅ Test terminé avec succès !")


if __name__ == "__main__":
    main()
