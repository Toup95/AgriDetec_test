#!/usr/bin/env python3
"""
Script de vérification pré-entraînement
Vérifie que tout est prêt pour l'entraînement du modèle
"""

import os
import sys
import tensorflow as tf
from PIL import Image


def check_tensorflow():
    """Vérifier TensorFlow"""
    print("🔍 Vérification de TensorFlow...")
    print(f"   Version: {tf.__version__}")
    
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        print(f"   ✅ GPU détecté: {gpus}")
        for gpu in gpus:
            print(f"      {gpu}")
    else:
        print("   ⚠️  Aucun GPU détecté - L'entraînement sera lent")
    print()


def check_data_structure(data_dir="data"):
    """Vérifier la structure des données"""
    print("📁 Vérification de la structure des données...")
    
    required_dirs = [
        os.path.join(data_dir, "train"),
        os.path.join(data_dir, "validation"),
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"   ✅ {dir_path} existe")
        else:
            print(f"   ❌ {dir_path} manquant")
            all_ok = False
    
    print()
    return all_ok


def count_images(data_dir="data"):
    """Compter les images par classe"""
    print("📊 Statistiques du dataset...")
    
    stats = {}
    splits = ['train', 'validation', 'test']
    
    for split in splits:
        split_dir = os.path.join(data_dir, split)
        if not os.path.exists(split_dir):
            continue
        
        stats[split] = {}
        
        # Pour chaque classe
        for class_name in os.listdir(split_dir):
            class_path = os.path.join(split_dir, class_name)
            
            if not os.path.isdir(class_path):
                continue
            
            # Compter les images
            images = [f for f in os.listdir(class_path) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            stats[split][class_name] = len(images)
    
    # Afficher les stats
    all_classes = set()
    for split_stats in stats.values():
        all_classes.update(split_stats.keys())
    
    print(f"   Nombre de classes: {len(all_classes)}")
    print(f"   Classes: {', '.join(sorted(all_classes))}")
    print()
    
    # Tableau des stats
    print("   Distribution des données:")
    print("   " + "-" * 60)
    print(f"   {'Classe':<20} {'Train':<10} {'Validation':<12} {'Test':<10}")
    print("   " + "-" * 60)
    
    total_train = 0
    total_val = 0
    total_test = 0
    warnings = []
    
    for class_name in sorted(all_classes):
        train_count = stats.get('train', {}).get(class_name, 0)
        val_count = stats.get('validation', {}).get(class_name, 0)
        test_count = stats.get('test', {}).get(class_name, 0)
        
        total_train += train_count
        total_val += val_count
        total_test += test_count
        
        print(f"   {class_name:<20} {train_count:<10} {val_count:<12} {test_count:<10}")
        
        # Vérifier les problèmes
        if train_count < 50:
            warnings.append(f"⚠️  {class_name}: Seulement {train_count} images d'entraînement (recommandé: 100+)")
        
        if train_count == 0:
            warnings.append(f"❌ {class_name}: Aucune image d'entraînement!")
    
    print("   " + "-" * 60)
    print(f"   {'TOTAL':<20} {total_train:<10} {total_val:<12} {total_test:<10}")
    print()
    
    # Afficher les avertissements
    if warnings:
        print("   ⚠️  Avertissements:")
        for warning in warnings:
            print(f"   {warning}")
        print()
    
    # Recommandations
    if total_train < 500:
        print("   💡 Conseil: Plus de données amélioreront la performance")
        print("      Recommandé: Au moins 100 images par classe")
    
    return total_train > 0


def check_image_quality(data_dir="data", sample_size=10):
    """Vérifier la qualité des images"""
    print("🖼️  Vérification de la qualité des images...")
    
    train_dir = os.path.join(data_dir, "train")
    if not os.path.exists(train_dir):
        print("   ❌ Dossier train non trouvé")
        return False
    
    # Trouver des images à échantillonner
    sample_images = []
    for class_name in os.listdir(train_dir):
        class_path = os.path.join(train_dir, class_name)
        if not os.path.isdir(class_path):
            continue
        
        images = [f for f in os.listdir(class_path)
                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        # Prendre quelques images
        sample_images.extend([os.path.join(class_path, img) 
                            for img in images[:min(2, len(images))]])
    
    if not sample_images:
        print("   ❌ Aucune image trouvée")
        return False
    
    # Vérifier les images
    issues = []
    sizes = []
    
    for img_path in sample_images[:sample_size]:
        try:
            img = Image.open(img_path)
            width, height = img.size
            sizes.append((width, height))
            
            # Vérifier la taille
            if width < 224 or height < 224:
                issues.append(f"Image trop petite: {os.path.basename(img_path)} ({width}x{height})")
            
            # Vérifier le format
            if img.mode not in ['RGB', 'L']:
                issues.append(f"Format inhabituel: {os.path.basename(img_path)} ({img.mode})")
            
        except Exception as e:
            issues.append(f"Erreur lors de l'ouverture de {os.path.basename(img_path)}: {e}")
    
    # Résumé
    if sizes:
        avg_width = sum(w for w, h in sizes) / len(sizes)
        avg_height = sum(h for w, h in sizes) / len(sizes)
        min_width = min(w for w, h in sizes)
        min_height = min(h for w, h in sizes)
        
        print(f"   Taille moyenne: {avg_width:.0f}x{avg_height:.0f} pixels")
        print(f"   Taille minimale: {min_width}x{min_height} pixels")
    
    if issues:
        print("   ⚠️  Problèmes détectés:")
        for issue in issues[:5]:  # Afficher max 5 problèmes
            print(f"      {issue}")
        if len(issues) > 5:
            print(f"      ... et {len(issues)-5} autres problèmes")
    else:
        print("   ✅ Images OK")
    
    print()
    return len(issues) == 0


def check_dependencies():
    """Vérifier les dépendances"""
    print("📦 Vérification des dépendances...")
    
    required = {
        'tensorflow': 'TensorFlow',
        'PIL': 'Pillow',
        'numpy': 'NumPy',
        'matplotlib': 'Matplotlib',
    }
    
    missing = []
    for module, name in required.items():
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} manquant")
            missing.append(name)
    
    if missing:
        print()
        print(f"   ⚠️  Installez les dépendances manquantes:")
        print(f"      pip install {' '.join(missing.lower())}")
        return False
    
    print()
    return True


def estimate_training_time(num_images, epochs=50):
    """Estimer le temps d'entraînement"""
    print("⏱️  Estimation du temps d'entraînement...")
    
    # Temps estimé par image (très approximatif)
    gpus = tf.config.list_physical_devices('GPU')
    
    if gpus:
        seconds_per_image = 0.02  # Avec GPU
        device = "GPU"
    else:
        seconds_per_image = 0.5   # Sans GPU
        device = "CPU"
    
    total_seconds = num_images * epochs * seconds_per_image
    hours = int(total_seconds / 3600)
    minutes = int((total_seconds % 3600) / 60)
    
    print(f"   Device: {device}")
    print(f"   Images: {num_images}")
    print(f"   Epochs: {epochs}")
    print(f"   Temps estimé: ~{hours}h {minutes}min")
    print()


def main():
    """
    Vérification complète
    """
    print("=" * 70)
    print("🌾 AgriDetect - Vérification Pré-Entraînement")
    print("=" * 70)
    print()
    
    data_dir = "data"
    all_ok = True
    
    # 1. Vérifier TensorFlow
    check_tensorflow()
    
    # 2. Vérifier les dépendances
    if not check_dependencies():
        all_ok = False
    
    # 3. Vérifier la structure
    if not check_data_structure(data_dir):
        all_ok = False
        print("❌ Structure de données incorrecte")
        print()
        print("Créez la structure avec:")
        print("   python prepare_dataset.py")
        return
    
    # 4. Compter les images
    has_images = count_images(data_dir)
    if not has_images:
        all_ok = False
        print("❌ Aucune image trouvée")
        print()
        print("Ajoutez des images ou téléchargez un dataset:")
        print("   python prepare_dataset.py")
        return
    
    # 5. Vérifier la qualité
    check_image_quality(data_dir)
    
    # 6. Estimer le temps
    train_dir = os.path.join(data_dir, "train")
    total_images = 0
    for class_name in os.listdir(train_dir):
        class_path = os.path.join(train_dir, class_name)
        if os.path.isdir(class_path):
            images = [f for f in os.listdir(class_path)
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            total_images += len(images)
    
    estimate_training_time(total_images)
    
    # Résumé
    print("=" * 70)
    if all_ok:
        print("✅ Tout est prêt pour l'entraînement!")
        print()
        print("Lancez l'entraînement avec:")
        print("   python train_model.py")
    else:
        print("⚠️  Certaines vérifications ont échoué")
        print("   Corrigez les problèmes avant de lancer l'entraînement")
    print("=" * 70)


if __name__ == "__main__":
    main()
