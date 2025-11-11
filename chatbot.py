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
            "Pulvériser un produit à base de cuivre (respecter l’étiquette)",
            "Éviter l’arrosage par aspersion",
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
            "Éviter excès d’azote",
            "Espacer les plants pour l’aération"
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
            "Éviter l’humidité prolongée sur le feuillage",
            "Utiliser des variétés tolérantes quand c’est possible"
        ],
        "symptoms": "Taches brun-gris s’élargissant vite, parfois duvet blanc au revers."
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
            "Supprimer feuilles atteintes pour limiter la source d’inoculum"
        ],
        "prevention": [
            "Semences certifiées",
            "Désinfecter les outils",
            "Éviter les éclaboussures d’eau"
        ],
        "symptoms": "Petites taches sombres, parfois huileuses, sur feuilles et fruits."
    },
    "tomato_early_blight": {
        "name": "Brûlure précoce de la tomate",
        "crop": "Tomate",
        "severity": "Modérée",
        "treatments": [
            "Traitement cuivre",
            "Améliorer l’aération du feuillage"
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
            "Fongicide systémique (suivre l’étiquette)",
            "Couper les parties très atteintes"
        ],
        "prevention": [
            "Arroser au pied",
            "Espacer les plants",
            "Éviter l’humidité prolongée"
        ],
        "symptoms": "Taches brun-gris qui s’élargissent vite, parfois duvet blanc au revers."
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
            "Éviter excès d’azote"
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
        "name": "Virus de l’enroulement jaune (tomate)",
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
        "prevention": ["Arroser au pied", "Surveillance régulière"]
    },
}

# petit index texte → clé
_TEXT_INDEX: List[Tuple[str, str]] = []
for key, data in DISEASE_INFO.items():
    _TEXT_INDEX.append((data.get("name", "").lower(), key))
    _TEXT_INDEX.append((data.get("crop", "").lower(), key))


class MultilingualAgriChatbot:
    def __init__(self, default_lang: str = "fr"):
        self.default_lang = default_lang

    # ---------- utils ----------
    def _normalize(self, text: str) -> str:
        text = text.lower().strip()
        repl = {
            "é": "e", "è": "e", "ê": "e", "à": "a", "ù": "u",
            "ç": "c", "ô": "o", "î": "i", "ï": "i"
        }
        for a, b in repl.items():
            text = text.replace(a, b)
        return text

    def _find_disease_key(self, msg_norm: str) -> Optional[str]:
        disease_fr = {
            "mildiou": ["late_blight"],
            "brulure precoce": ["early_blight"],
            "brulure": ["early_blight"],
            "tache bacterienne": ["bacterial_spot", "bacterial"],
            "septoriose": ["septoria_leaf_spot"],
            "acariens": ["spider_mites"],
            "araignees rouges": ["spider_mites"],
            "mosaique": ["mosaic_virus"],
            "mosaïque": ["mosaic_virus"],
            "enroulement jaune": ["yellow_leaf_curl_virus"],
        }
        cultures = {
            "tomate": ["tomato"],
            "poivron": ["pepper"],
            "piment": ["pepper"],
            "pomme de terre": ["potato"],
            "patate": ["potato"],
        }

        # 1) essayer couple
        for c_fr, c_keys in cultures.items():
            if c_fr in msg_norm:
                for d_fr, d_keys in disease_fr.items():
                    if d_fr in msg_norm:
                        for ck in c_keys:
                            for dk in d_keys:
                                candidate = f"{ck}_{dk}"
                                for real_key in DISEASE_INFO.keys():
                                    if candidate in real_key:
                                        return real_key

        # 2) matching texte plus souple
        for text, key in _TEXT_INDEX:
            parts = text.split()
            matches = sum(1 for p in parts if p in msg_norm)
            if matches >= min(2, len(parts)):
                return key

        # 3) dernier recours
        for text, key in _TEXT_INDEX:
            if text in msg_norm:
                return key

        return None

    def _general_reply(self, msg_norm: str) -> str:
        # 🔹 nouveau : prévention maladies fongiques / champignons
        if (
            "maladie fongique" in msg_norm
            or "maladies fongiques" in msg_norm
            or "fongique" in msg_norm
            or "champignon" in msg_norm
            or "champignons" in msg_norm
        ):
            return (
                "Pour prévenir les maladies fongiques 🌿 :\n"
                "1. Arroser au pied (pas sur les feuilles)\n"
                "2. Espacer les plants pour que ça sèche vite\n"
                "3. Pailler le sol pour éviter les éclaboussures\n"
                "4. Enlever les feuilles touchées et les sortir de la parcelle\n"
                "5. Faire une rotation des cultures (éviter tomate → tomate au même endroit)\n"
                "6. En saison humide : surveiller souvent pour traiter tôt (cuivre/soufre si autorisé)."
            )

        if "traitement biologique" in msg_norm or "traitements biologiques" in msg_norm:
            return (
                "Traitements biologiques possibles 🌱 :\n"
                "- savon noir dilué (insectes, acariens)\n"
                "- huile de Neem (le soir, éviter fleurs ouvertes)\n"
                "- décoction d’ail ou de neem en prévention\n"
                "- cuivre/bouillie bordelaise = autorisé en bio dans certains pays (voir règlement local)\n"
                "- toujours traiter le matin ou le soir."
            )
        if "arrosage" in msg_norm or "arroser" in msg_norm:
            return (
                "Bonnes pratiques d’arrosage :\n"
                "1. Arroser au pied, pas sur les feuilles\n"
                "2. Le matin (ou le soir s’il fait très chaud)\n"
                "3. Garder le sol humide mais non détrempé\n"
                "4. Pailler pour réduire l’évaporation ✅"
            )
        if "prevention" in msg_norm or "prévention" in msg_norm or "eviter maladie" in msg_norm:
            return (
                "Prévention générale des maladies :\n"
                "- utiliser des semences/plants sains\n"
                "- espacer les plants pour l’aération\n"
                "- arroser au pied\n"
                "- retirer les feuilles malades\n"
                "- pratiquer la rotation des cultures"
            )
        if "tomate" in msg_norm and "maladie" in msg_norm:
            return (
                "Maladies courantes de la tomate : mildiou, tache bactérienne, brûlure précoce, septoriose, virus de la mosaïque, enroulement jaune.\n"
                "Demande par ex. « traitement mildiou tomate » 👍"
            )
        return (
            "Je n’ai pas trouvé exactement la maladie dans ton message 😅.\n"
            "Tu peux écrire :\n"
            "- « traitement mildiou tomate »\n"
            "- « prévention tache bactérienne poivron »\n"
            "- « symptômes brûlure précoce pomme de terre »"
        )

    def _format_disease_answer(self, key: str, msg_norm: str) -> str:
        data = DISEASE_INFO.get(key, {})
        title = data.get("name", key)
        severity = data.get("severity", "Inconnue")
        treatments = data.get("treatments", [])
        prevention = data.get("prevention", [])
        symptoms = data.get("symptoms", "")

        # traitement ?
        if "traitement" in msg_norm or "soigner" in msg_norm:
            if treatments:
                lines = [f"Traitement pour **{title}** :"]
                for t in treatments:
                    lines.append(f"- {t}")
                lines.append(f"Sévérité : **{severity}**.")
                return "\n".join(lines)
            else:
                return (
                    f"Pour **{title}**, pas de traitement spécifique enregistré. "
                    "Supprime les parties atteintes et améliore l’aération."
                )

        # prévention ?
        if "prevention" in msg_norm or "prévention" in msg_norm or "eviter" in msg_norm:
            if prevention:
                lines = [f"Prévention pour **{title}** :"]
                for p in prevention:
                    lines.append(f"- {p}")
                return "\n".join(lines)
            else:
                return (
                    f"Prévention générale pour **{title}** : rotation, arrosage au pied, enlever les feuilles malades."
                )

        # symptômes ?
        if "symptome" in msg_norm or "symptômes" in msg_norm or "reconnaitre" in msg_norm:
            if symptoms:
                return f"Symptômes de **{title}** : {symptoms}"
            else:
                return f"Les symptômes de **{title}** sont taches sur feuilles et affaiblissement de la plante."

        # sinon fiche courte
        parts = [
            f"📋 Maladie : **{title}**",
            f"Sévérité : {severity}",
        ]
        if symptoms:
            parts.append(f"Symptômes : {symptoms}")
        if treatments:
            parts.append("Traitements possibles : " + "; ".join(treatments))
        if prevention:
            parts.append("Prévention : " + "; ".join(prevention))
        return "\n".join(parts)

    def generate_response(
        self,
        message: str,
        session_id: str = "default",
        language: Optional[str] = "fr",
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
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
                "bonnes pratiques d’arrosage",
            ],
            "context": {
                "session_id": session_id,
                "topic": "plant_disease_assistant",
                **(extra_context or {}),
            },
            "timestamp": datetime.now().isoformat(),
        }


# Singleton du chatbot
_CHATBOT_INSTANCE: Optional[MultilingualAgriChatbot] = None

def _get_chatbot(language: str = "fr") -> MultilingualAgriChatbot:
    """Retourne une instance singleton du chatbot"""
    global _CHATBOT_INSTANCE
    if _CHATBOT_INSTANCE is None:
        _CHATBOT_INSTANCE = MultilingualAgriChatbot(default_lang=language)
    return _CHATBOT_INSTANCE

# ==============================================
# 🟢 Fonction compatible avec ton main.py
# ==============================================
def generate_chat_response(
    session_id: str,
    message: str,
    language: str = "fr",
    extra_context: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Fonction simple compatible avec main.py.
    
    Args:
        session_id: ID de la session de chat
        message: Message de l'utilisateur
        language: Langue (fr, en, wo)
        extra_context: Contexte additionnel
    
    Returns:
        str: La réponse du chatbot
    """
    try:
        bot = _get_chatbot(language)
        response_dict = bot.generate_response(
            message=message,
            session_id=session_id,
            language=language,
            extra_context=extra_context,
        )
        # Retourne juste le texte de réponse
        return response_dict.get("response", "Erreur du chatbot")
    except Exception as e:
        log.error(f"Erreur generate_chat_response: {e}", exc_info=True)
        return f"❌ Erreur: {str(e)}"


if __name__ == "__main__":
    b = MultilingualAgriChatbot()
    tests = [
        "Comment prévenir les maladies fongiques ?",
        "Traitement mildiou tomate",
        "Prévention tache bactérienne poivron",
        "Symptômes brûlure précoce pomme de terre",
        "bonnes pratiques d'arrosage",
    ]
    for t in tests:
        print(">", t)
        r = b.generate_response(t)
        print(r["response"])
        print()
