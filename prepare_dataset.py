#!/usr/bin/env python3
"""
Script pour télécharger et préparer des datasets de maladies des plantes
"""

import os
import zipfile
import requests
from pathlib import Path
import shutil
from tqdm import tqdm


class DatasetDownloader:
    """
    Téléchargeur de datasets pour AgriDetect
    """
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def download_file(self, url: str, destination: str):
        """
        Télécharger un fichier avec barre de progression
        """
        print(f"📥 Téléchargement depuis {url}...")
        
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(destination, 'wb') as file, tqdm(
            desc=os.path.basename(destination),
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                pbar.update(size)
        
        print(f"✓ Téléchargé: {destination}")
    
    def extract_zip(self, zip_path: str, extract_to: str):
        """
        Extraire un fichier ZIP
        """
        print(f"📦 Extraction de {zip_path}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"✓ Extrait vers: {extract_to}")
    
    def download_plantvillage(self):
        """
        Télécharger le dataset PlantVillage
        Note: Nécessite Kaggle API configuré
        """
        print("🌿 PlantVillage Dataset")
        print("=" * 50)
        print("Ce dataset contient 54,000+ images de feuilles de plantes")
        print("avec 38 classes différentes de maladies et plantes saines.")
        print()
        print("Pour télécharger ce dataset:")
        print("1. Créez un compte sur Kaggle: https://www.kaggle.com")
        print("2. Installez kaggle: pip install kaggle")
        print("3. Configurez vos credentials: https://www.kaggle.com/docs/api")
        print("4. Exécutez: kaggle datasets download -d emmarex/plantdisease")
        print()
        
        try:
            import kaggle
            print("📥 Téléchargement du dataset PlantVillage...")
            kaggle.api.dataset_download_files(
                'emmarex/plantdisease',
                path=self.data_dir,
                unzip=True
            )
            print("✓ Dataset téléchargé!")
        except ImportError:
            print("⚠ Kaggle API non installée. Installez avec: pip install kaggle")
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    def download_plantdoc(self):
        """
        Télécharger le dataset PlantDoc depuis GitHub
        """
        print("🌱 PlantDoc Dataset")
        print("=" * 50)
        
        github_url = "https://github.com/pratikkayal/PlantDoc-Dataset/archive/refs/heads/master.zip"
        zip_path = os.path.join(self.data_dir, "plantdoc.zip")
        extract_path = os.path.join(self.data_dir, "plantdoc")
        
        # Télécharger
        if not os.path.exists(zip_path):
            self.download_file(github_url, zip_path)
        
        # Extraire
        if not os.path.exists(extract_path):
            self.extract_zip(zip_path, self.data_dir)
        
        print("✓ PlantDoc dataset prêt!")
    
    def create_sample_dataset(self):
        """
        Créer un dataset d'exemple pour les tests
        """
        print("📝 Création d'un dataset d'exemple...")
        
        # Structure
        classes = ['mildiou', 'oidium', 'healthy']
        splits = ['train', 'validation', 'test']
        
        for split in splits:
            for class_name in classes:
                path = os.path.join(self.data_dir, split, class_name)
                os.makedirs(path, exist_ok=True)
        
        print("✓ Structure créée:")
        for split in splits:
            print(f"  - {self.data_dir}/{split}/")
            for class_name in classes:
                print(f"    └── {class_name}/")
        
        print()
        print("📸 Ajoutez maintenant vos images dans ces dossiers:")
        print(f"   {os.path.abspath(self.data_dir)}")
    
    def organize_dataset(self, source_dir: str, train_split=0.7, val_split=0.15):
        """
        Organiser un dataset en train/validation/test
        
        Args:
            source_dir: Dossier source contenant les classes
            train_split: Proportion pour l'entraînement
            val_split: Proportion pour la validation
        """
        print(f"📁 Organisation du dataset depuis {source_dir}...")
        
        import random
        
        # Pour chaque classe
        for class_name in os.listdir(source_dir):
            class_path = os.path.join(source_dir, class_name)
            
            if not os.path.isdir(class_path):
                continue
            
            # Lister toutes les images
            images = [f for f in os.listdir(class_path) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            random.shuffle(images)
            
            # Calculer les splits
            n_train = int(len(images) * train_split)
            n_val = int(len(images) * val_split)
            
            train_images = images[:n_train]
            val_images = images[n_train:n_train+n_val]
            test_images = images[n_train+n_val:]
            
            # Copier dans les bons dossiers
            splits_data = {
                'train': train_images,
                'validation': val_images,
                'test': test_images
            }
            
            for split, split_images in splits_data.items():
                dest_dir = os.path.join(self.data_dir, split, class_name)
                os.makedirs(dest_dir, exist_ok=True)
                
                for img in split_images:
                    src = os.path.join(class_path, img)
                    dst = os.path.join(dest_dir, img)
                    shutil.copy2(src, dst)
            
            print(f"✓ {class_name}: {len(train_images)} train, "
                  f"{len(val_images)} val, {len(test_images)} test")
        
        print("✓ Dataset organisé!")


def main():
    """
    Menu interactif
    """
    print("=" * 60)
    print("🌾 AgriDetect - Préparation des Données")
    print("=" * 60)
    print()
    
    downloader = DatasetDownloader()
    
    print("Choisissez une option:")
    print("1. Créer une structure de dataset vide")
    print("2. Télécharger PlantVillage (Kaggle)")
    print("3. Télécharger PlantDoc (GitHub)")
    print("4. Organiser un dataset existant")
    print("5. Quitter")
    print()
    
    choice = input("Votre choix (1-5): ")
    
    if choice == "1":
        downloader.create_sample_dataset()
    elif choice == "2":
        downloader.download_plantvillage()
    elif choice == "3":
        downloader.download_plantdoc()
    elif choice == "4":
        source = input("Chemin du dossier source: ")
        if os.path.exists(source):
            downloader.organize_dataset(source)
        else:
            print(f"❌ Le dossier {source} n'existe pas")
    elif choice == "5":
        print("👋 Au revoir!")
    else:
        print("❌ Choix invalide")


if __name__ == "__main__":
    main()
