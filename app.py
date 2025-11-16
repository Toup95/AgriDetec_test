# -*- coding: utf-8 -*-
import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import os
from datetime import datetime
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px

# Configuration de la page
st.set_page_config(
    page_title="AgriDetec - Détection IA",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =======================
# CONSTANTES ET CONFIGURATION
# =======================
APP_VERSION = "1.1.0"

# Classes de maladies (extrait de votre main.py)
DATASET_DISEASES = [
    {"id": "pepper_bacterial_spot", "plant_fr": "Poivron", "disease_fr": "Tache bactérienne", "severity": "Modérée"},
    {"id": "pepper_healthy", "plant_fr": "Poivron", "disease_fr": "Sain", "severity": "Aucune"},
    {"id": "potato_early_blight", "plant_fr": "Pomme de terre", "disease_fr": "Brûlure précoce", "severity": "Modérée"},
    {"id": "potato_late_blight", "plant_fr": "Pomme de terre", "disease_fr": "Brûlure tardive", "severity": "Élevée"},
    {"id": "potato_healthy", "plant_fr": "Pomme de terre", "disease_fr": "Sain", "severity": "Aucune"},
    {"id": "tomato_bacterial_spot", "plant_fr": "Tomate", "disease_fr": "Tache bactérienne", "severity": "Modérée"},
    {"id": "tomato_early_blight", "plant_fr": "Tomate", "disease_fr": "Brûlure précoce", "severity": "Modérée"},
    {"id": "tomato_leaf_mold", "plant_fr": "Tomate", "disease_fr": "Moisissure des feuilles", "severity": "Modérée"},
    {"id": "tomato_septoria_leaf_spot", "plant_fr": "Tomate", "disease_fr": "Tache foliaire de Septoria", "severity": "Modérée"},
    {"id": "tomato_spider_mites", "plant_fr": "Tomate", "disease_fr": "Acariens", "severity": "Modérée"},
    {"id": "tomato_target_spot", "plant_fr": "Tomate", "disease_fr": "Tache cible", "severity": "Modérée"},
    {"id": "tomato_mosaic_virus", "plant_fr": "Tomate", "disease_fr": "Virus de la mosaïque", "severity": "Élevée"},
    {"id": "tomato_yellow_leaf_curl_virus", "plant_fr": "Tomate", "disease_fr": "Virus de l'enroulement jaune", "severity": "Élevée"},
    {"id": "tomato_healthy", "plant_fr": "Tomate", "disease_fr": "Sain", "severity": "Aucune"},
]

# Traductions multilingues
TRANSLATIONS = {
    "fr": {
        "title": "🌱 AgriDetec - Détection de Maladies des Plantes",
        "subtitle": "Application IA pour la détection des maladies des cultures",
        "upload": "📸 Téléchargez une image de plante",
        "analyzing": "Analyse en cours...",
        "results": "🔍 Résultats de l'analyse",
        "recommendations": "💊 Recommandations",
        "confidence": "Confiance",
        "disease_detected": "Maladie détectée",
        "healthy_plant": "✅ Plante en bonne santé !",
        "treatment_needed": "⚠️ Traitement recommandé",
        "chat_title": "💬 Assistant Agricole",
        "dashboard_title": "📊 Tableau de Bord",
        "stats_title": "Statistiques",
    },
    "wo": {
        "title": "🌱 AgriDetec - Deteksyon Maladii Géej",
        "subtitle": "Aplikasyon IA ngir detekte maladii géej yi",
        "upload": "📸 Yeb nataal bu géej",
        "analyzing": "Dina analize...",
        "results": "🔍 Résulta ci analizub",
        "recommendations": "💊 Waxtaanu tëriit",
        "confidence": "Dëgg",
        "disease_detected": "Maladi détecté",
        "healthy_plant": "✅ Géej bi baax na!",
        "treatment_needed": "⚠️ Tëriit dina soxla",
        "chat_title": "💬 Ndimbalkat Jëmmal",
        "dashboard_title": "📊 Taabloo",
        "stats_title": "Statistik",
    },
    "pu": {
        "title": "🌱 AgriDetec - Deteksiyoo Maladii Gese",
        "subtitle": "Aplikasiyoo IA ngam yiytude maladii gese",
        "upload": "📸 Yeb natawal ngal",
        "analyzing": "Nana analize...",
        "results": "🔍 Kesudi analisum",
        "recommendations": "💊 Waxtaanu ñalngu",
        "confidence": "Goonga",
        "disease_detected": "Maladi jeyaa",
        "healthy_plant": "✅ Gese nge moƴƴii!",
        "treatment_needed": "⚠️ Ñalngu haani",
        "chat_title": "💬 Ballal Gollal",
        "dashboard_title": "📊 Panneau",
        "stats_title": "Statistik",
    }
}

# =======================
# FONCTIONS UTILITAIRES
# =======================

@st.cache_resource
def load_model():
    """Charge le modèle de détection"""
    try:
        model_path = "models/agridetect_model_20251107_042206"
        if not os.path.exists(model_path):
            return None, f"❌ Modèle non trouvé dans {model_path}"
        
        # Essayer de charger avec TF 2.x (Keras 3)
        try:
            import tf_keras
            model = tf_keras.models.load_model(model_path)
            return model, None
        except:
            pass
        
        # Fallback: essayer avec Keras standard
        try:
            model = tf.keras.models.load_model(model_path, compile=False)
            return model, None
        except Exception as keras_error:
            return None, (
                f"⚠️ Modèle non compatible avec cette version de Keras.\n\n"
                f"Le modèle a été entraîné avec Keras 2 mais Streamlit Cloud utilise Keras 3.\n\n"
                f"**Solutions possibles:**\n"
                f"1. Héberger le modèle sur Hugging Face\n"
                f"2. Ré-entraîner avec Keras 3\n"
                f"3. Utiliser un modèle pré-entraîné compatible\n\n"
                f"**En attendant, testez le Chatbot et le Dashboard !** 🚀"
            )
    except Exception as e:
        return None, f"Erreur lors du chargement : {str(e)}"

def predict_disease(image, model, language="fr"):
    """Effectue la prédiction sur une image"""
    # Prétraitement
    img = image.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    # Prédiction
    predictions = model.predict(img_array, verbose=0)
    predicted_class = np.argmax(predictions[0])
    confidence = float(predictions[0][predicted_class])
    
    # Mapping vers le catalogue
    if predicted_class < len(DATASET_DISEASES):
        disease_info = DATASET_DISEASES[predicted_class]
    else:
        disease_info = {
            "id": "unknown",
            "plant_fr": "Non spécifié",
            "disease_fr": "Maladie inconnue",
            "severity": "Inconnue"
        }
    
    return {
        "disease_name": disease_info["disease_fr"],
        "plant": disease_info["plant_fr"],
        "confidence": confidence,
        "severity": disease_info["severity"],
        "disease_id": disease_info["id"]
    }

def get_treatment_recommendations(disease_id, language="fr"):
    """Retourne les recommandations de traitement"""
    treatments = {
        "bacterial_spot": [
            "Retirer et détruire les feuilles infectées",
            "Appliquer un fongicide à base de cuivre",
            "Éviter l'arrosage par aspersion",
            "Améliorer la circulation d'air"
        ],
        "early_blight": [
            "Enlever les feuilles malades",
            "Rotation des cultures",
            "Appliquer un fongicide préventif",
            "Pailler le sol pour réduire l'éclaboussure"
        ],
        "late_blight": [
            "Traitement fongicide immédiat",
            "Détruire les plants infectés",
            "Éviter l'humidité excessive",
            "Utiliser des variétés résistantes"
        ],
        "healthy": [
            "Continuer les bonnes pratiques culturales",
            "Surveiller régulièrement",
            "Maintenir une fertilisation équilibrée",
            "Assurer un arrosage adapté"
        ]
    }
    
    # Recherche de la clé
    for key in treatments.keys():
        if key in disease_id:
            return treatments[key]
    
    return treatments.get("healthy", ["Consultez un agronome pour plus d'informations"])

# =======================
# INTERFACE SIDEBAR
# =======================

def render_sidebar():
    """Affiche la barre latérale avec navigation et paramètres"""
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/00a651/ffffff?text=AgriDetec", use_container_width=True)
        st.markdown("---")
        
        # Sélection de la langue
        language = st.selectbox(
            "🌍 Langue / Language",
            options=["fr", "wo", "pu"],
            format_func=lambda x: {"fr": "Français", "wo": "Wolof", "pu": "Pulaar"}[x],
            key="language"
        )
        
        # Navigation
        st.markdown("### Navigation")
        page = st.radio(
            "Aller à:",
            options=["detection", "chat", "dashboard", "about"],
            format_func=lambda x: {
                "detection": "🔍 Détection",
                "chat": "💬 Chatbot",
                "dashboard": "📊 Dashboard",
                "about": "ℹ️ À propos"
            }[x],
            key="page"
        )
        
        st.markdown("---")
        st.caption(f"Version {APP_VERSION}")
        st.caption("© 2025 AgriDetec")
        
        return language, page

# =======================
# PAGES DE L'APPLICATION
# =======================

def page_detection(language, t, model, model_error):
    """Page de détection de maladies"""
    st.title(t["title"])
    st.markdown(f"### {t['subtitle']}")
    
    if model_error:
        st.error(model_error)
        st.info("🔧 Pour utiliser la détection, assurez-vous que le modèle est disponible dans le dossier `models/`")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(t["upload"])
        uploaded_file = st.file_uploader(
            "Choisissez une image (JPG, JPEG, PNG)",
            type=['jpg', 'jpeg', 'png'],
            help="Formats acceptés: JPG, JPEG, PNG"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption='Image téléchargée', use_container_width=True)
    
    with col2:
        if uploaded_file is not None:
            st.subheader(t["results"])
            
            with st.spinner(t["analyzing"]):
                result = predict_disease(image, model, language)
            
            # Affichage des résultats
            disease_name = result["disease_name"]
            confidence = result["confidence"]
            severity = result["severity"]
            
            if "sain" in disease_name.lower() or "healthy" in disease_name.lower():
                st.success(f"**{disease_name}**")
                st.balloons()
            else:
                st.warning(f"**{t['disease_detected']}:** {disease_name}")
            
            st.metric(t["confidence"], f"{confidence*100:.2f}%")
            st.progress(confidence)
            
            # Informations supplémentaires
            st.info(f"**Plante:** {result['plant']}")
            st.info(f"**Sévérité:** {severity}")
            
            # Recommandations
            st.subheader(t["recommendations"])
            treatments = get_treatment_recommendations(result["disease_id"], language)
            for i, treatment in enumerate(treatments, 1):
                st.write(f"{i}. {treatment}")
        else:
            st.info("👆 " + t["upload"])

def page_chatbot(language, t):
    """Page du chatbot agricole"""
    st.title(t["chat_title"])
    st.markdown("### Assistant agricole multilingue")
    
    # Initialisation de l'historique
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Affichage de l'historique
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Zone de saisie
    if prompt := st.chat_input("Posez votre question..."):
        # Ajout du message utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Réponse du bot (simulation)
        with st.chat_message("assistant"):
            response = generate_chatbot_response(prompt, language)
            st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

def generate_chatbot_response(message, language="fr"):
    """Génère une réponse du chatbot (version simplifiée)"""
    # Réponses prédéfinies pour la démo
    responses = {
        "fr": {
            "bonjour": "Bonjour ! Je suis l'assistant AgriDetec. Comment puis-je vous aider avec vos cultures aujourd'hui ?",
            "tomate": "La tomate est sensible à plusieurs maladies. Assurez-vous d'arroser au pied et de bien espacer les plants pour la circulation d'air.",
            "default": "Je suis là pour vous aider avec vos questions agricoles. Posez-moi des questions sur les maladies des plantes, les traitements, ou les bonnes pratiques culturales !"
        },
        "wo": {
            "bonjour": "Salam aleykum ! Maa ngi AgriDetec. Noonu laa mën a ko dimbal ci sa géej?",
            "default": "Maa ngi fii ngir dimbalil yow ci ay laaj yu am jëf ak géej. Laaj ma!"
        },
        "pu": {
            "bonjour": "Jam waali! Mi ko AgriDetec. Hol no tawii ma wallude ma e gese maɗa?",
            "default": "Mi ko ɗoo ngam wallitde ma e laawol gese. Naamno ma!"
        }
    }
    
    message_lower = message.lower()
    lang_responses = responses.get(language, responses["fr"])
    
    for key in lang_responses:
        if key in message_lower:
            return lang_responses[key]
    
    return lang_responses["default"]

def page_dashboard(language, t):
    """Page du dashboard avec statistiques"""
    st.title(t["dashboard_title"])
    st.markdown("### Statistiques et aperçu")
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Détections", "1,543", "+12%")
    with col2:
        st.metric("Maladies Détectées", len(DATASET_DISEASES), "14 types")
    with col3:
        st.metric("Taux de Réussite", "95.8%", "+2.1%")
    with col4:
        st.metric("Utilisateurs Actifs", "342", "+23")
    
    st.markdown("---")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Maladies les plus fréquentes")
        
        # Données pour le graphique
        diseases_data = {
            "Maladie": ["Mildiou", "Tache bactérienne", "Septoriose", "Brûlure précoce", "Acariens"],
            "Nombre": [320, 230, 121, 124, 89]
        }
        
        fig = px.bar(
            diseases_data,
            x="Maladie",
            y="Nombre",
            color="Nombre",
            color_continuous_scale="Greens"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🥬 Répartition par culture")
        
        crops_data = {
            "Culture": ["Tomate", "Pomme de terre", "Poivron"],
            "Détections": [856, 452, 235]
        }
        
        fig = px.pie(
            crops_data,
            values="Détections",
            names="Culture",
            color_discrete_sequence=px.colors.sequential.Greens
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Tableau des maladies récentes
    st.subheader("🔍 Détections récentes")
    
    recent_detections = [
        {"Date": "2025-11-16", "Plante": "Tomate", "Maladie": "Mildiou", "Confiance": "94.2%"},
        {"Date": "2025-11-16", "Plante": "Pomme de terre", "Maladie": "Brûlure précoce", "Confiance": "89.7%"},
        {"Date": "2025-11-15", "Plante": "Poivron", "Maladie": "Tache bactérienne", "Confiance": "92.3%"},
        {"Date": "2025-11-15", "Plante": "Tomate", "Maladie": "Sain", "Confiance": "98.1%"},
    ]
    
    st.dataframe(recent_detections, use_container_width=True)

def page_about(language):
    """Page À propos"""
    st.title("ℹ️ À propos d'AgriDetec")
    
    st.markdown("""
    ### 🌱 AgriDetec - Détection IA de Maladies des Plantes
    
    **AgriDetec** est une application d'intelligence artificielle développée pour aider les agriculteurs 
    du Sénégal et d'Afrique de l'Ouest à identifier rapidement les maladies de leurs cultures.
    
    #### 🎯 Fonctionnalités principales:
    
    - **🔍 Détection automatique** : Analysez vos plantes en quelques secondes
    - **💬 Assistant multilingue** : Support en Français, Wolof et Pulaar
    - **📊 Tableau de bord** : Suivez les statistiques et tendances
    - **💊 Recommandations** : Conseils de traitement personnalisés
    
    #### 🌾 Cultures supportées:
    
    - 🍅 Tomate (9 maladies)
    - 🥔 Pomme de terre (3 maladies)
    - 🌶️ Poivron (2 maladies)
    
    #### 👨‍💻 Projet académique
    
    Master 1 Intelligence Artificielle  
    Année universitaire 2024-2025
    
    #### 📧 Contact
    
    Pour toute question ou suggestion, contactez-nous !
    
    ---
    
    *Développé avec ❤️ pour l'agriculture africaine*
    """)

# =======================
# APPLICATION PRINCIPALE
# =======================

def main():
    """Point d'entrée principal de l'application"""
    
    # Chargement du modèle
    model, model_error = load_model()
    
    # Sidebar
    language, page = render_sidebar()
    
    # Traductions
    t = TRANSLATIONS[language]
    
    # Routage des pages
    if page == "detection":
        page_detection(language, t, model, model_error)
    elif page == "chat":
        page_chatbot(language, t)
    elif page == "dashboard":
        page_dashboard(language, t)
    elif page == "about":
        page_about(language)

if __name__ == "__main__":
    main()
