# chatbot.py
from __future__ import annotations

from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import logging

log = logging.getLogger("agridetect.chatbot")

# ---------------------------------------------------------------------
# Base de connaissances : mêmes cultures / maladies que ton modèle
# ---------------------------------------------------------------------
DISEASE_INFO: Dict[str, Dict[str, Any]] = {
    # ---------------- POIVRON / PIMENT ----------------
    "pepper_bacterial_spot": {
        "name": "Tache bactérienne du poivron",
        "crop": "Poivron / Piment",
        "severity": "Modérée",
        "treatments": [
            "Pulvériser un produit à base de cuivre (respecter l'étiquette)",
            "Éviter l'arrosage par aspersion",
            "Supprimer les feuilles très atteintes"
        ],
        "prevention": [
            "Semences/plants sains",
            "Désinfection des outils",
            "Éviter de manipuler les plantes mouillées"
        ],
        "symptoms": "Petites taches brun-noir, parfois entourées de jaune, sur feuilles et parfois fruits."
    },
    "pepper_healthy": {
        "name": "Poivron sain",
        "crop": "Poivron",
        "severity": "Aucune",
        "treatments": [],
        "prevention": ["Surveillance régulière", "Arrosage au pied"]
    },

    # ---------------- POMME DE TERRE ----------------
    "potato_early_blight": {
        "name": "Brûlure précoce (pomme de terre)",
        "crop": "Pomme de terre",
        "severity": "Modérée",
        "treatments": [
            "Fongicide de contact (cuivre ou chlorothalonil) si disponible",
            "Retirer les feuilles très atteintes"
        ],
        "prevention": [
            "Rotation 2 à 3 ans",
            "Éviter excès d'azote",
            "Espacer les plants pour l'aération"
        ],
        "symptoms": "Taches brunes avec cercles concentriques sur les feuilles âgées."
    },
    "potato_late_blight": {
        "name": "Mildiou de la pomme de terre",
        "crop": "Pomme de terre",
        "severity": "Élevée",
        "treatments": [
            "Fongicide systémique homologué",
            "Éliminer/enterrer les parties fortement atteintes"
        ],
        "prevention": [
            "Arroser au pied",
            "Éviter l'humidité prolongée sur le feuillage",
            "Utiliser des variétés tolérantes quand c'est possible"
        ],
        "symptoms": "Taches brun-gris s'élargissant vite, parfois duvet blanc au revers."
    },
    "potato_healthy": {
        "name": "Pomme de terre saine",
        "crop": "Pomme de terre",
        "severity": "Aucune",
        "treatments": [],
        "prevention": ["Surveillance", "Arrosage régulier sans détremper le sol"]
    },

    # ---------------- TOMATE ----------------
    "tomato_bacterial_spot": {
        "name": "Tache bactérienne de la tomate",
        "crop": "Tomate",
        "severity": "Modérée",
        "treatments": [
            "Traitement cuivre (hydroxyde ou oxichlorure)",
            "Supprimer feuilles atteintes pour limiter la source d'inoculum"
        ],
        "prevention": [
            "Semences certifiées",
            "Désinfecter les outils",
            "Éviter les éclaboussures d'eau"
        ],
        "symptoms": "Petites taches sombres, parfois huileuses, sur feuilles et fruits."
    },
    "tomato_early_blight": {
        "name": "Brûlure précoce de la tomate",
        "crop": "Tomate",
        "severity": "Modérée",
        "treatments": [
            "Traitement cuivre",
            "Améliorer l'aération du feuillage"
        ],
        "prevention": [
            "Rotation",
            "Ne pas mouiller le feuillage le soir",
            "Ramasser les débris au sol"
        ],
        "symptoms": "Taches brunes avec anneaux concentriques sur feuilles âgées."
    },
    "tomato_late_blight": {
        "name": "Tomate — mildiou",
        "crop": "Tomate",
        "severity": "Élevée",
        "treatments": [
            "Fongicide systémique (suivre l'étiquette)",
            "Couper les parties très atteintes"
        ],
        "prevention": [
            "Arroser au pied",
            "Espacer les plants",
            "Éviter l'humidité prolongée"
        ],
        "symptoms": "Taches brun-gris qui s'élargissent vite, parfois duvet blanc au revers."
    },
    "tomato_leaf_mold": {
        "name": "Moisissure des feuilles de la tomate",
        "crop": "Tomate",
        "severity": "Modérée",
        "treatments": [
            "Pulvérisation soufre ou cuivre",
            "Éclaircir le feuillage"
        ],
        "prevention": [
            "Bonne ventilation",
            "Éviter condensation dans les abris"
        ],
        "symptoms": "Tache jaune en dessus, feutrage olive en dessous."
    },
    "tomato_septoria_leaf_spot": {
        "name": "Tache foliaire de Septoria (tomate)",
        "crop": "Tomate",
        "severity": "Modérée",
        "treatments": [
            "Traitement cuivre",
            "Enlever les feuilles basses atteintes"
        ],
        "prevention": [
            "Rotation",
            "Arrosage au pied"
        ],
        "symptoms": "Petites taches rondes à centre clair et bord foncé."
    },
    "tomato_spider_mites": {
        "name": "Acariens / araignées rouges (tomate)",
        "crop": "Tomate",
        "severity": "Modérée",
        "treatments": [
            "Pulvérisation de savon noir dilué",
            "Ou huile de Neem (en soirée)"
        ],
        "prevention": [
            "Éviter le stress hydrique",
            "Surveiller le revers des feuilles"
        ],
        "symptoms": "Feuilles décolorées, fines toiles, petits points jaunes."
    },
    "tomato_target_spot": {
        "name": "Tache cible (tomate)",
        "crop": "Tomate",
        "severity": "Modérée",
        "treatments": [
            "Traitement cuivre",
            "Éliminer les feuilles atteintes"
        ],
        "prevention": [
            "Aérer",
            "Éviter excès d'azote"
        ],
        "symptoms": "Taches rondes avec cercles concentriques."
    },
    "tomato_mosaic_virus": {
        "name": "Virus de la mosaïque (tomate)",
        "crop": "Tomate",
        "severity": "Élevée",
        "treatments": [
            "Détruire les plants très atteints",
            "Limiter les manipulations"
        ],
        "prevention": [
            "Semences saines",
            "Désinfection des outils",
            "Contrôler les vecteurs (pucerons, aleurodes)"
        ],
        "symptoms": "Feuilles marbrées vert clair/vert foncé, déformation éventuelle."
    },
    "tomato_yellow_leaf_curl_virus": {
        "name": "Virus de l'enroulement jaune (tomate)",
        "crop": "Tomate",
        "severity": "Élevée",
        "treatments": [
            "Éliminer les plants atteints",
            "Lutter contre les aleurodes (mouches blanches)"
        ],
        "prevention": [
            "Filets anti-insectes",
            "Paillage",
            "Variétés tolérantes"
        ],
        "symptoms": "Feuilles jaunes enroulées vers le haut, pousse ralentie."
    },
    "tomato_healthy": {
        "name": "Tomate saine",
        "crop": "Tomate",
        "severity": "Aucune",
        "treatments": [],
        "prevention": ["Surveillance régulière", "Bonne irrigation"]
    },
}


class MultilingualAgriChatbot:
    """Chatbot agricole multilingue pour AgriDetect"""

    def __init__(self, default_lang: str = "fr"):
        self.default_lang = default_lang
        self._build_index()

    def _build_index(self):
        """Construit un index texte pour reconnaissance rapide"""
        self._TEXT_INDEX = []
        for key, info in DISEASE_INFO.items():
            name = info.get("name", "")
            crop = info.get("crop", "")
            if name:
                self._TEXT_INDEX.append((name.lower(), key))
            if crop:
                self._TEXT_INDEX.append((crop.lower(), key))

    def _normalize(self, text: str) -> str:
        """Normalise un texte pour recherche"""
        return text.lower().strip()

    def _find_disease_key(self, msg_norm: str) -> Optional[str]:
        """Trouve la clé maladie dans le message normalisé"""
        # 1) Essai : correspondance crop + disease
        disease_fr = {
            "tache bactérienne": ["pepper_bacterial_spot", "tomato_bacterial_spot"],
            "mildiou": ["potato_late_blight", "tomato_late_blight"],
            "brûlure précoce": ["potato_early_blight", "tomato_early_blight"],
            "moisissure": ["tomato_leaf_mold"],
            "septoriose": ["tomato_septoria_leaf_spot"],
            "acariens": ["tomato_spider_mites"],
            "tache cible": ["tomato_target_spot"],
            "virus mosaïque": ["tomato_mosaic_virus"],
            "enroulement jaune": ["tomato_yellow_leaf_curl_virus"],
        }

        crop_fr = {
            "tomate": ["tomato_"],
            "pomme de terre": ["potato_"],
            "poivron": ["pepper_"],
            "piment": ["pepper_"],
        }

        # Tentative 1 : correspondance directe crop + disease
        for c_fr, c_keys in crop_fr.items():
            if c_fr in msg_norm:
                for d_fr, d_keys in disease_fr.items():
                    if d_fr in msg_norm:
                        for ck in c_keys:
                            for dk in d_keys:
                                candidate = f"{ck}{dk.replace('_', '')}"
                                for real_key in DISEASE_INFO.keys():
                                    if ck in real_key and dk.replace("_", "") in real_key:
                                        return real_key

        # 2) Tentative 2 : matching texte plus souple
        for text, key in self._TEXT_INDEX:
            parts = text.split()
            matches = sum(1 for p in parts if p in msg_norm)
            if matches >= min(2, len(parts)):
                return key

        # 3) Tentative 3 : matching simple
        for text, key in self._TEXT_INDEX:
            if text in msg_norm:
                return key

        return None

    def _general_reply(self, msg_norm: str) -> str:
        """Génère une réponse générale si pas de maladie trouvée"""
        # Maladie fongique
        if any(word in msg_norm for word in ["maladie fongique", "fongique", "champignon", "champignons"]):
            return (
                "Pour prévenir les maladies fongiques 🌿 :\n"
                "1. Arroser au pied (pas sur les feuilles)\n"
                "2. Espacer les plants pour que ça sèche vite\n"
                "3. Pailler le sol pour éviter les éclaboussures\n"
                "4. Enlever les feuilles touchées et les sortir de la parcelle\n"
                "5. Faire une rotation des cultures\n"
                "6. En saison humide : surveiller souvent pour traiter tôt (cuivre/soufre si autorisé)."
            )

        # Traitement biologique
        if any(word in msg_norm for word in ["traitement biologique", "traitements biologiques", "bio"]):
            return (
                "Traitements biologiques possibles 🌱 :\n"
                "- Savon noir dilué (insectes, acariens)\n"
                "- Huile de Neem (le soir, éviter fleurs ouvertes)\n"
                "- Décoction d'ail ou de neem en prévention\n"
                "- Cuivre/bouillie bordelaise (autorité locales)\n"
                "- Toujours traiter le matin ou le soir."
            )

        # Arrosage
        if any(word in msg_norm for word in ["arrosage", "arroser"]):
            return (
                "Bonnes pratiques d'arrosage 💧:\n"
                "1. Arroser au pied, pas sur les feuilles\n"
                "2. Le matin (ou le soir s'il fait très chaud)\n"
                "3. Garder le sol humide mais non détrempé\n"
                "4. Pailler pour réduire l'évaporation ✅"
            )

        # Prévention générale
        if any(word in msg_norm for word in ["prevention", "prévention", "eviter maladie", "éviter"]):
            return (
                "Prévention générale des maladies 🛡️ :\n"
                "- Utiliser des semences/plants sains\n"
                "- Espacer les plants pour l'aération\n"
                "- Arroser au pied\n"
                "- Retirer les feuilles malades\n"
                "- Pratiquer la rotation des cultures"
            )

        # Tomate + maladie
        if "tomate" in msg_norm and "maladie" in msg_norm:
            return (
                "Maladies courantes de la tomate 🍅 :\n"
                "- Mildiou\n"
                "- Tache bactérienne\n"
                "- Brûlure précoce\n"
                "- Septoriose\n"
                "- Virus de la mosaïque\n"
                "- Virus de l'enroulement jaune\n"
                "Demande par ex. « traitement mildiou tomate » 👍"
            )

        # Réponse par défaut
        return (
            "Je n'ai pas trouvé exactement la maladie dans ton message 😅.\n"
            "Tu peux écrire :\n"
            "- « traitement mildiou tomate »\n"
            "- « prévention tache bactérienne poivron »\n"
            "- « symptômes brûlure précoce pomme de terre »\n"
            "- « bonnes pratiques d'arrosage »"
        )

    def _format_disease_answer(self, key: str, msg_norm: str) -> str:
        """Formate la réponse pour une maladie spécifique"""
        data = DISEASE_INFO.get(key, {})
        title = data.get("name", key)
        severity = data.get("severity", "Inconnue")
        treatments = data.get("treatments", [])
        prevention = data.get("prevention", [])
        symptoms = data.get("symptoms", "")

        # Traitement ?
        if any(word in msg_norm for word in ["traitement", "soigner", "traiter"]):
            if treatments:
                lines = [f"Traitement pour **{title}** :"]
                for t in treatments:
                    lines.append(f"  • {t}")
                lines.append(f"\nSévérité : **{severity}**")
                return "\n".join(lines)
            else:
                return (
                    f"Pour **{title}**, pas de traitement spécifique enregistré.\n"
                    "Supprime les parties atteintes et améliore l'aération."
                )

        # Prévention ?
        if any(word in msg_norm for word in ["prevention", "prévention", "eviter", "éviter"]):
            if prevention:
                lines = [f"Prévention pour **{title}** :"]
                for p in prevention:
                    lines.append(f"  • {p}")
                return "\n".join(lines)
            else:
                return (
                    f"Prévention générale pour **{title}** :\n"
                    "Rotation, arrosage au pied, enlever les feuilles malades."
                )

        # Symptômes ?
        if any(word in msg_norm for word in ["symptome", "symptômes", "reconnaitre", "reconnaître"]):
            if symptoms:
                return f"Symptômes de **{title}** 🔍 :\n{symptoms}"
            else:
                return f"Symptômes de **{title}** : taches sur feuilles et affaiblissement de la plante."

        # Fiche courte par défaut
        parts = [
            f"📋 Maladie : **{title}**",
            f"Sévérité : {severity}",
        ]
        if symptoms:
            parts.append(f"Symptômes : {symptoms}")
        if treatments:
            parts.append("Traitements : " + "; ".join(treatments[:2]))
        if prevention:
            parts.append("Prévention : " + "; ".join(prevention[:2]))
        return "\n".join(parts)

    def reply(
        self,
        message: str,
        session_id: str = "default",
        language: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Méthode compatible avec ChatbotManager"""
        return self.generate_response(
            message=message,
            session_id=session_id,
            language=language or self.default_lang,
            extra_context=context,
        )

    def generate_response(
        self,
        message: str,
        session_id: str = "default",
        language: Optional[str] = "fr",
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Génère une réponse complète au chatbot"""
        msg_norm = self._normalize(message)
        disease_key = self._find_disease_key(msg_norm)

        if disease_key:
            text = self._format_disease_answer(disease_key, msg_norm)
            intent = "disease_info"
        else:
            text = self._general_reply(msg_norm)
            intent = "general"

        return {
            "response": text,
            "language": language or self.default_lang,
            "intent": intent,
            "suggestions": [
                "traitement mildiou tomate",
                "prévention tache bactérienne poivron",
                "bonnes pratiques d'arrosage",
            ],
            "context": {
                "session_id": session_id,
                "topic": "plant_disease_assistant",
                **(extra_context or {}),
            },
            "timestamp": datetime.now().isoformat(),
        }


class ChatbotManager:
    """🟢 Classe requise par main.py pour gérer le chatbot"""

    def __init__(self):
        try:
            self._bot = MultilingualAgriChatbot(default_lang="fr")
            self._available = True
            log.info("✅ ChatbotManager initialisé avec succès")
        except Exception as e:
            log.error(f"❌ Erreur initialisation ChatbotManager: {e}")
            self._bot = None
            self._available = False

    def is_available(self) -> bool:
        """Vérifie si le chatbot est disponible"""
        return self._available and self._bot is not None

    def reply(
        self,
        message: str,
        session_id: str = "default",
        language: str = "fr",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Génère une réponse du chatbot"""
        if not self.is_available():
            log.warning("⚠️ Chatbot non disponible")
            return {
                "response": "Le chatbot n'est pas disponible pour le moment.",
                "language": language,
                "intent": "error",
                "suggestions": [],
                "context": {"session_id": session_id},
                "timestamp": datetime.now().isoformat(),
                "success": False,
            }

        return self._bot.reply(
            message=message,
            session_id=session_id,
            language=language,
            context=context,
        )


# =====================================================================
# 🟢 Fonction EXACTEMENT compatible avec ton main.py
# =====================================================================
def generate_chat_response(
    bot: Optional[MultilingualAgriChatbot],
    message: str,
    session_id: str = "default",
    language: str = "fr",
    extra_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Compatible avec l'appel main.py :
        generate_chat_response(self._bot, message=..., session_id=..., language=..., extra_context=...)
    """
    if bot is None:
        bot = MultilingualAgriChatbot(default_lang=language)
    return bot.generate_response(
        message=message,
        session_id=session_id,
        language=language,
        extra_context=extra_context,
    )


if __name__ == "__main__":
    # Test du chatbot
    print("🤖 Tests du ChatbotManager\n")
    manager = ChatbotManager()

    tests = [
        "Comment prévenir les maladies fongiques ?",
        "Traitement mildiou tomate",
        "Prévention tache bactérienne poivron",
        "Symptômes brûlure précoce pomme de terre",
        "bonnes pratiques d'arrosage",
        "Tomate saine ?",
    ]

    for test_msg in tests:
        print(f"❓ Entrée: {test_msg}")
        response = manager.reply(test_msg, language="fr")
        print(f"✅ Réponse: {response['response']}")
        print(f"   Intent: {response['intent']}")
        print()
