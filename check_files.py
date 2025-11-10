# check_files.py
import os
from pathlib import Path

def check_model_files():
    model_dir = Path("C:/Users/USER/Desktop/AgriDetec_test/models/agridetect_model_20251030_054621")
    
    print("🔍 Vérification détaillée des fichiers...")
    print(f"📁 Dossier: {model_dir}")
    print(f"✅ Existe: {model_dir.exists()}")
    
    if model_dir.exists():
        for item in model_dir.iterdir():
            size = item.stat().st_size if item.is_file() else "dossier"
            print(f"   - {item.name} ({size})")
        
        # Vérifier spécifiquement model.keras
        model_file = model_dir / "model.keras"
        if model_file.exists():
            print(f"\n✅ model.keras trouvé - Taille: {model_file.stat().st_size / (1024*1024):.2f} MB")
        else:
            print("❌ model.keras non trouvé!")
            
        # Vérifier metadata.json
        metadata_file = model_dir / "metadata.json"
        if metadata_file.exists():
            print(f"✅ metadata.json trouvé")
            try:
                import json
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                print(f"📊 Contenu metadata: {metadata.keys()}")
                if 'classes' in metadata:
                    print(f"🔤 Classes dans metadata: {len(metadata['classes'])}")
            except Exception as e:
                print(f"❌ Erreur lecture metadata: {e}")
        else:
            print("❌ metadata.json non trouvé!")

if __name__ == "__main__":
    check_model_files()