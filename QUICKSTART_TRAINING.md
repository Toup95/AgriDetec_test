# 🚀 Démarrage Rapide - Entraînement du Modèle

Guide ultra-rapide pour entraîner votre modèle AgriDetect en 5 étapes.

---

## ⚡ Installation Express (5 minutes)

```bash
# 1. Installer les dépendances ML
pip install -r requirements_ml.txt

# 2. Vérifier TensorFlow
python -c "import tensorflow as tf; print(f'TensorFlow {tf.__version__}')"
```

---

## 📊 Obtenir des Données (10-30 minutes)

### Option A : Dataset Rapide (Recommandé pour débuter)

```bash
# Créer la structure vide
python prepare_dataset.py
# Choisir option 1

# Puis ajoutez manuellement 50-100 images par classe dans:
# data/train/maladie1/
# data/train/maladie2/
# data/validation/maladie1/
# data/validation/maladie2/
```

### Option B : Dataset PlantVillage (54,000 images)

```bash
# 1. Installer Kaggle
pip install kaggle

# 2. Configurer Kaggle API
# Aller sur kaggle.com/account
# Télécharger kaggle.json
# Placer dans ~/.kaggle/ (Linux/Mac) ou C:\Users\YOU\.kaggle\ (Windows)

# 3. Télécharger
kaggle datasets download -d emmarex/plantdisease
unzip plantdisease.zip -d data/

# 4. Organiser
python prepare_dataset.py
# Choisir option 4, indiquer le chemin
```

### Option C : Dataset PlantDoc (2,598 images)

```bash
python prepare_dataset.py
# Choisir option 3
```

---

## ✅ Vérifier le Setup (2 minutes)

```bash
python check_setup.py
```

Si tout est ✅ vert, continuez !

---

## 🎯 Entraîner le Modèle (30 min - 4h selon GPU)

### Configuration Rapide (Fichier train_model.py)

```python
# Éditer ces lignes si besoin:
BATCH_SIZE = 32          # Réduire à 16 si erreur mémoire
EPOCHS = 50              # Réduire à 20 pour test rapide
PRETRAINED_MODEL = "MobileNetV2"  # Ou "EfficientNetB0"
```

### Lancer l'Entraînement

```bash
python train_model.py
```

**Temps estimés:**
- Avec GPU moderne (RTX 3060+) : 20-40 minutes
- Avec GPU ancien (GTX 1060) : 40-80 minutes  
- Sans GPU (CPU only) : 4-8 heures

### Réduire le Temps pour Test Rapide

```python
# Dans train_model.py, modifier:
EPOCHS = 10              # Au lieu de 50
BATCH_SIZE = 64          # Au lieu de 32 (si assez de mémoire)
```

---

## 📈 Résultats

Après l'entraînement, vous trouverez dans `models/agridetect_model_XXXXXX/`:

```
├── model.h5                  # ✅ Modèle principal
├── saved_model/              # ✅ Format TensorFlow
├── metadata.json             # ℹ️ Infos du modèle
├── training_curves.png       # 📊 Graphiques
└── history.json              # 📝 Historique
```

### Vérifier les Performances

```python
# Ouvrir training_curves.png
# Vérifier que:
# ✅ Accuracy augmente (> 85% idéalement)
# ✅ Val_accuracy suit train_accuracy
# ✅ Loss diminue
```

---

## 🧪 Tester le Modèle (2 minutes)

```python
from model_predictor import DiseaseDetector

# Charger
detector = DiseaseDetector("models/agridetect_model_XXXXXX")

# Tester
result = detector.detect_disease("test_image.jpg")

print(f"Maladie: {result['disease_name']}")
print(f"Confiance: {result['confidence']:.1%}")
print(f"Sévérité: {result['severity']}")
```

---

## 🔌 Intégrer dans l'API (5 minutes)

### 1. Copier le Modèle

```bash
# Copier vers le dossier de votre API
cp -r models/agridetect_model_XXXXXX /chemin/vers/api/models/current_model
```

### 2. Modifier l'API

Dans votre fichier API (main.py ou routes/detection.py):

```python
from model_predictor import DiseaseDetector

# Au démarrage de l'app
MODEL_PATH = "models/current_model"
detector = DiseaseDetector(MODEL_PATH)

# Dans votre endpoint
@app.post("/api/v1/detect-disease")
async def detect(file: UploadFile):
    # Sauvegarder temporairement
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    
    # Détecter
    result = detector.detect_disease(temp_path)
    
    # Nettoyer
    os.remove(temp_path)
    
    return result
```

### 3. Tester l'API

```bash
# Relancer l'API
uvicorn main:app --reload

# Tester
curl -X POST http://localhost:8000/api/v1/detect-disease \
  -F "file=@test_image.jpg"
```

---

## 🎉 C'est Terminé !

Vous avez maintenant :
- ✅ Un modèle entraîné
- ✅ Des prédictions fonctionnelles
- ✅ Une API qui utilise l'IA

---

## 🔥 Pro Tips

### Améliorer les Performances

```bash
# 1. Plus de données = Meilleur modèle
# Objectif: 500+ images par classe

# 2. Fine-tuning après premier entraînement
# Dans train_model.py, décommenter:
# model = fine_tune_model(model, train_gen, val_gen, config)

# 3. Essayer EfficientNet
PRETRAINED_MODEL = "EfficientNetB0"  # Plus précis que MobileNetV2
```

### Problèmes Fréquents

**❌ Out of Memory**
```python
BATCH_SIZE = 16  # ou 8
```

**❌ Accuracy < 70%**
```bash
# Causes: Pas assez de données, données de mauvaise qualité
# Solution: Plus d'images (100+ par classe)
```

**❌ Trop lent**
```python
EPOCHS = 20        # Réduire pour test
IMG_HEIGHT = 192   # Au lieu de 224
IMG_WIDTH = 192
```

---

## 📚 Aller Plus Loin

- **Guide Complet**: Lisez `TRAINING_GUIDE.md`
- **Optimisation**: Consultez la section "Optimisation" du guide
- **Déploiement**: Voir `README.md` pour le déploiement en production

---

## 🆘 Besoin d'Aide ?

1. Vérifiez `check_setup.py` pour diagnostic
2. Consultez `TRAINING_GUIDE.md` pour détails
3. Vérifiez les logs d'entraînement pour erreurs

---

**Temps total estimé : 1-4 heures selon votre setup**

🌾 Bon entraînement !
