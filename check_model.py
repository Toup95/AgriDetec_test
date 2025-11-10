# check_model.py
import os
from pathlib import Path
from disease_detector import PlantDiseaseDetector

def diagnose_model_loading():
    model_path = "C:/Users/USER/Desktop/AgriDetec_test/models/agridetect_model_20251030_054621"
    
    print(f"🔍 Diagnostic du modèle: {model_path}")
    print(f"📁 Le chemin existe: {os.path.exists(model_path)}")
    
    if not os.path.exists(model_path):
        print("❌ Le chemin n'existe pas!")
        return
    
    # Lister le contenu
    print("\n📁 Contenu du dossier:")
    for item in Path(model_path).iterdir():
        print(f"   - {item.name} ({'fichier' if item.is_file() else 'dossier'})")
    
    # Vérifier les fichiers requis
    model_files = list(Path(model_path).glob("model.*"))
    metadata_files = list(Path(model_path).glob("metadata.json"))
    
    print(f"\n🔍 Fichiers model.* trouvés: {[f.name for f in model_files]}")
    print(f"🔍 Fichiers metadata.json trouvés: {[f.name for f in metadata_files]}")
    
    if not model_files:
        print("❌ Aucun fichier model.* trouvé!")
        return
    
    # Essayer de charger le modèle
    print(f"\n🚀 Test de chargement du modèle...")
    try:
        detector = PlantDiseaseDetector(model_path=model_path)
        print(f"✅ Modèle chargé: {detector.is_loaded}")
        print(f"📊 Classes: {len(detector.class_names)}")
        print(f"🔤 Noms des classes: {detector.class_names}")
        
        if detector.model:
            print(f"🏗️  Architecture du modèle chargée")
        else:
            print("❌ Aucun modèle TensorFlow chargé")
            
    except Exception as e:
        print(f"❌ Erreur lors du chargement: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_model_loading()