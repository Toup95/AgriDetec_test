# 🤖 Guide Complet d'Entraînement du Modèle AgriDetect

Ce guide vous explique pas à pas comment entraîner votre propre modèle de détection de maladies des plantes.

---

## 📋 Table des Matières

1. [Prérequis](#prérequis)
2. [Préparation des Données](#préparation-des-données)
3. [Entraînement du Modèle](#entraînement-du-modèle)
4. [Évaluation et Tests](#évaluation-et-tests)
5. [Intégration dans l'API](#intégration-dans-lapi)
6. [Optimisation](#optimisation)

---

## 🔧 Prérequis

### Logiciels Nécessaires

```bash
# Installer les dépendances supplémentaires
pip install tensorflow
pip install keras
pip install pillow
pip install matplotlib
pip install tqdm
pip install kaggle  # optionnel, pour télécharger des datasets
```

### Configuration Matérielle Recommandée

- **CPU**: 4+ cores
- **RAM**: 8GB minimum (16GB recommandé)
- **GPU**: Nvidia GPU avec CUDA (optionnel mais fortement recommandé)
- **Espace disque**: 20GB minimum

### Vérifier TensorFlow et GPU

```python
import tensorflow as tf

print(f"TensorFlow version: {tf.__version__}")
print(f"GPU disponible: {tf.config.list_physical_devices('GPU')}")
```

---

## 📊 Préparation des Données

### Étape 1 : Structure des Dossiers

Créez cette structure :

```
data/
├── train/                  # ~70% des images
│   ├── Pepper__bell___Bacterial_spot/
│   ├── Pepper__bell___healthy/
│   ├── Potato___Early_blight/
│   ├── Potato___Late_blight/
│   ├── Potato___healthy/
│   ├── Tomato_Bacterial_spot/
│   ├── Tomato_Early_blight/
│   ├── Tomato_Late_blight/
│   ├── Tomato_Leaf_Mold/
│   ├── Tomato_Septoria_leaf_spot/
│   ├── Tomato_Spider_mites_Two_spotted_spider_mite/
│   ├── Tomato__Target_Spot/
│   ├── Tomato__Tomato_YellowLeaf__Curl_Virus/
│   ├── Tomato__Tomato_mosaic_virus/
│   └── Tomato_healthy/
│
├── validation/             # ~15% des images
│   ├── Pepper__bell___Bacterial_spot/
│   ├── Pepper__bell___healthy/
│   ├── Potato___Early_blight/
│   ├── Potato___Late_blight/
│   ├── Potato___healthy/
│   ├── Tomato_Bacterial_spot/
│   ├── Tomato_Early_blight/
│   ├── Tomato_Late_blight/
│   ├── Tomato_Leaf_Mold/
│   ├── Tomato_Septoria_leaf_spot/
│   ├── Tomato_Spider_mites_Two_spotted_spider_mite/
│   ├── Tomato__Target_Spot/
│   ├── Tomato__Tomato_YellowLeaf__Curl_Virus/
│   ├── Tomato__Tomato_mosaic_virus/
│   └── Tomato_healthy/
│
└── test/                   # ~15% des images
    ├── Pepper__bell___Bacterial_spot/
    ├── Pepper__bell___healthy/
    ├── Potato___Early_blight/
    ├── Potato___Late_blight/
    ├── Potato___healthy/
    ├── Tomato_Bacterial_spot/
    ├── Tomato_Early_blight/
    ├── Tomato_Late_blight/
    ├── Tomato_Leaf_Mold/
    ├── Tomato_Septoria_leaf_spot/
    ├── Tomato_Spider_mites_Two_spotted_spider_mite/
    ├── Tomato__Target_Spot/
    ├── Tomato__Tomato_YellowLeaf__Curl_Virus/
    ├── Tomato__Tomato_mosaic_virus/
    └── Tomato_healthy/
```

### Étape 2 : Obtenir des Images

#### Option A : Utiliser le Script de Téléchargement

```bash
python prepare_dataset.py
```

Choisissez l'option qui vous convient.

#### Option B : Datasets Publics Recommandés

1. **PlantVillage** (54,000+ images)
   - URL: https://www.kaggle.com/datasets/emmarex/plantdisease
   - 38 classes de maladies
   - Très populaire et bien organisé

2. **PlantDoc** (2,598 images)
   - URL: https://github.com/pratikkayal/PlantDoc-Dataset
   - 27 classes
   - Images réelles (pas en laboratoire)

3. **Plant Pathology 2020** (Kaggle Competition)
   - URL: https://www.kaggle.com/c/plant-pathology-2020-fgvc7
   - Focus sur les pommes

#### Option C : Créer Votre Propre Dataset

1. Prenez des photos de plantes malades dans votre région
2. Organisez-les par type de maladie
3. Minimum 100 images par classe (idéalement 500+)
4. Variez les angles, conditions d'éclairage, stades de la maladie

### Étape 3 : Préparer les Données

```bash
# Créer la structure vide
python prepare_dataset.py
# Choisir l'option 1

# Ou organiser un dataset existant
python prepare_dataset.py
# Choisir l'option 4 et indiquer le chemin
```

### Bonnes Pratiques pour les Images

✅ **À FAIRE:**
- Images claires et nettes
- Résolution minimum: 224x224 pixels
- Format: JPG ou PNG
- Focus sur les feuilles malades
- Fond varié mais pas trop distrayant

❌ **À ÉVITER:**
- Images floues
- Trop petites (< 200x200)
- Avec watermark ou texte
- Trop de bruit en arrière-plan

---

## 🚀 Entraînement du Modèle

### Configuration de Base

Éditez `train_model.py` pour ajuster les paramètres :

```python
class Config:
    # Chemins
    DATA_DIR = "data"
    TRAIN_DIR = "data/train"
    VAL_DIR = "data/validation"
    
    # Hyperparamètres
    IMG_HEIGHT = 224
    IMG_WIDTH = 224
    BATCH_SIZE = 32
    EPOCHS = 50
    LEARNING_RATE = 0.001
    
    # Architecture
    USE_PRETRAINED = True
    PRETRAINED_MODEL = "EfficientNetB0" # ou "MobileNetV2"   
    FREEZE_LAYERS = True
```

### Lancer l'Entraînement

```bash
# Activer l'environnement virtuel
source venv/Scripts/activate

# Lancer l'entraînement
python train_model.py
```

### Ce qui se Passe Pendant l'Entraînement

L'entraînement va :

1. ✅ Charger et augmenter les images
2. ✅ Construire le modèle (Transfer Learning avec MobileNetV2)
3. ✅ Entraîner pendant X epochs
4. ✅ Sauvegarder le meilleur modèle
5. ✅ Générer des graphiques de performance
6. ✅ Créer un fichier de métadonnées

### Suivre l'Entraînement

Vous verrez quelque chose comme :

```
Epoch 1/60
45/45 [==============================] - 25s 556ms/step 
- loss: 0.8234 - accuracy: 0.7125 - val_loss: 0.6543 - val_accuracy: 0.7833

Epoch 2/60
45/45 [==============================] - 22s 489ms/step 
- loss: 0.6123 - accuracy: 0.8012 - val_loss: 0.5234 - val_accuracy: 0.8250
...
```

### Temps d'Entraînement Estimé

| Configuration | Temps par Epoch | Total (60 epochs)|
|--------------|----------------|------------------|
| CPU only | ~5-10 min | 6-12 h |
| GPU (GTX 1060) | ~30-60 sec | 25-50 min |
| GPU (RTX 3080) | ~15-30 sec | 12-25 min |

---

## 📈 Évaluation et Tests

### Fichiers Générés

Après l'entraînement, vous aurez :

```
models/
└── agridetect_model_20251107_042206/
    ├── best_model.weights.h5
    ├── fine_tuned_model.weights.h5
    ├── metadata.json
    ├── model.h5
    ├── model.keras
    └── training_log.csv

```

### Analyser les Résultats

#### 1. Vérifier les Courbes d'Apprentissage

Ouvrez `training_curves.png` :

- **Accuracy** devrait augmenter
- **Loss** devrait diminuer
- Les courbes train/validation ne doivent pas trop diverger

**Problèmes Courants:**

🔴 **Overfitting** : Val accuracy stagne mais train accuracy continue d'augmenter
- Solution: Augmenter la régularisation, plus de données, plus d'augmentation

🔴 **Underfitting** : Train et val accuracy restent faibles
- Solution: Modèle plus complexe, entraîner plus longtemps

🟢 **Bon apprentissage** : Les deux courbes augmentent ensemble

#### 2. Tester sur de Nouvelles Images

```python
from model_predictor import DiseaseDetector

# Charger le modèle
detector = DiseaseDetector("models\agridetect_model_20251107_042206")

# Tester
result = detector.detect_disease("test_image.jpg")

print(f"Maladie: {result['disease_name']}")
print(f"Confiance: {result['confidence']:.2%}")
```

### Métriques de Performance

Un bon modèle devrait avoir :

- **Accuracy globale** : > 95,85%
- **Top-3 Accuracy** : > 99,74%
- **Confiance moyenne** : > 97,53%

---

## 🔌 Intégration dans l'API

### Étape 1 : Copier le Modèle

```bash
# Copier le modèle dans le dossier de l'API
cp -r models/agridetect_model_20251107_042206 /chemin/vers/api/models/
```

### Étape 2 : Modifier l'API

Dans votre `main.py` ou `routes/detection.py` :

```python
from model_predictor import DiseaseDetector

# Charger le modèle au démarrage
MODEL_PATH = "models/agridetect_model_20251107_042206"
detector = DiseaseDetector(MODEL_PATH)

@app.post("/api/v1/detect-disease")
async def detect_disease(file: UploadFile = File(...)):
    # Sauvegarder temporairement le fichier
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    try:
        # Détecter
        result = detector.detect_disease(temp_path)
        return result
    finally:
        # Nettoyer
        if os.path.exists(temp_path):
            os.remove(temp_path)
```

### Étape 3 : Tester l'API

```bash
curl -X POST "http://localhost:8000/api/v1/detect-disease" \
  -F "file=@test_image.jpg"
```

---

## ⚡ Optimisation

### Améliorer les Performances

#### 1. Fine-Tuning

Après l'entraînement initial, dégeler certaines couches :

```python
# Dans train_model.py, décommenter :
model = fine_tune_model(model, train_gen, val_gen, config)
```

#### 2. Augmentation de Données Avancée

```python
# Ajouter dans Config
ROTATION_RANGE = 40
BRIGHTNESS_RANGE = [0.8, 1.2]
ZOOM_RANGE = [0.8, 1.2]
HORIZONTAL_FLIP = True
VERTICAL_FLIP = True
```

#### 3. Architecture Plus Performante

Essayez EfficientNetB0 au lieu de MobileNetV2 :

```python
PRETRAINED_MODEL = "EfficientNetB0"
```

#### 4. Ensembling

Entraînez plusieurs modèles et moyennez leurs prédictions.

### Réduire la Taille du Modèle

Pour le déploiement mobile :

```python
import tensorflow as tf

# Quantification
converter = tf.lite.TFLiteConverter.from_saved_model('models/saved_model')
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# Sauvegarder
with open('model.tflite', 'wb') as f:
    f.write(tflite_model)
```

---

## 🐛 Dépannage

### Erreur : Out of Memory (OOM)

**Solution :**
```python
# Réduire le batch size
BATCH_SIZE = 16  # au lieu de 32

# Ou réduire la taille des images
IMG_HEIGHT = 192
IMG_WIDTH = 192
```

### Erreur : CUDA out of memory

**Solution :**
```python
# Limiter l'utilisation de la mémoire GPU
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    tf.config.experimental.set_memory_growth(gpus[0], True)
```

### Accuracy très faible

**Causes possibles :**
- Pas assez de données (< 100 images par classe)
- Classes déséquilibrées
- Images de mauvaise qualité
- Learning rate trop élevé

**Solutions :**
- Collecter plus de données
- Utiliser des techniques de balancing
- Nettoyer le dataset
- Réduire le learning rate

---

## 📚 Ressources Supplémentaires

### Tutoriels

- [Transfer Learning avec Keras](https://www.tensorflow.org/tutorials/images/transfer_learning)
- [Data Augmentation](https://www.tensorflow.org/tutorials/images/data_augmentation)
- [Améliorer les modèles](https://developers.google.com/machine-learning/crash-course)

### Papers de Recherche

- PlantVillage: "Using Deep Learning for Image-Based Plant Disease Detection"
- "Deep Learning for Plant Disease Recognition" (survey)

### Communautés

- Stack Overflow ([tensorflow] tag)
- Reddit: r/MachineLearning
- Kaggle Forums

---

## ✅ Checklist Finale

Avant de déployer en production :

- [ ] Accuracy > 90% sue le test set
- [ ] Testé sur des images réelles (pas du dataset)
- [ ] Modèle optimisé (taille < 100MB)
- [ ] Documentation des classes
- [ ] Gestion des erreurs dans l'API
- [ ] Logging des prédictions
- [ ] Monitoring des performances

---

## 🎉 Félicitations !

Vous avez maintenant un modèle d'IA fonctionnel pour détecter les maladies des plantes !

**Prochaines étapes :**
1. Améliorer continuellement avec plus de données
2. Ajouter de nouvelles classes de maladies
3. Optimiser pour le déploiement mobile
4. Créer une application mobile

---

**Questions ? Consultez la documentation ou ouvrez une issue sur GitHub.**

🌾 AgriDetect - Protéger les cultures grâce à l'IA
