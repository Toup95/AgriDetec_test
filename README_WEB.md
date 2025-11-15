# 🌾 AgriDetect - Interface Web

Interface web complète pour le système de détection des maladies des cultures AgriDetect.

## 📁 Fichiers Inclus

- **index.html** - Page principale avec upload et détection d'images
- **chat.html** - Interface de chat avec le bot agricole
- **dashboard.html** - Tableau de bord avec statistiques
- **style.css** - Styles CSS modernes et responsives
- **app.js** - Logique JavaScript pour connexion API

## 🚀 Installation Rapide

### Étape 1 : Placer les fichiers

1. Téléchargez tous les fichiers (HTML, CSS, JS)
2. Placez-les dans un même dossier sur votre ordinateur

### Étape 2 : Vérifier que l'API est active

Assurez-vous que votre API AgriDetect est lancée :

```bash
# Dans votre terminal Git Bash
cd /e/court_DIT_24072025/Cours\ DIT/projet\ de\ fin\ etude/AgriDetec_test
source venv/Scripts/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Vous devriez voir :
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Étape 3 : Ouvrir l'interface web

**Méthode 1 : Directement dans le navigateur**
- Double-cliquez sur `index.html`
- Le fichier s'ouvrira dans votre navigateur par défaut

**Méthode 2 : Avec un serveur local (recommandé)**

Si vous avez Python installé :
```bash
# Dans le dossier contenant les fichiers HTML
python -m http.server 3000
```

Puis ouvrez : http://localhost:3000

Si vous avez Node.js avec `live-server` :
```bash
npm install -g live-server
live-server
```

## 📱 Utilisation

### 🔍 Page de Détection (index.html)

1. Cliquez sur "Choisir une image" ou glissez-déposez une photo
2. Sélectionnez une image de plante malade
3. Cliquez sur "Analyser"
4. Consultez les résultats :
   - Maladie détectée
   - Niveau de confiance
   - Sévérité
   - Traitements recommandés
   - Conseils de prévention

### 💬 Chat Bot (chat.html)

1. Tapez votre question dans le champ de texte
2. Appuyez sur "Envoyer" ou touche Entrée
3. Le bot répond avec des informations pertinentes
4. Utilisez les suggestions de questions pour explorer

**Exemples de questions :**
- Comment traiter le mildiou sur la tomate ?
- Quels sont les symptômes de l'oïdium ?
- Comment prévenir les maladies fongiques ?
- Quels traitements biologiques sont disponibles ?

### 📊 Dashboard (dashboard.html)

Consultez les statistiques en temps réel :
- Nombre total de détections
- Utilisateurs actifs
- Types de maladies détectées
- Taux de réussite
- Maladies les plus courantes

## 🎨 Fonctionnalités

✅ **Design moderne et responsive**
- Compatible mobile, tablette, desktop
- Interface intuitive
- Animations fluides

✅ **Upload d'images**
- Glisser-déposer
- Prévisualisation
- Formats : JPG, PNG, JPEG

✅ **Détection en temps réel**
- Analyse instantanée
- Résultats détaillés
- Recommandations personnalisées

✅ **Chatbot intelligent**
- Réponses en français
- Suggestions contextuelles
- Historique de conversation

✅ **Statistiques détaillées**
- Dashboard interactif
- Graphiques de données
- Maladies courantes

## 🔧 Configuration

Si votre API n'est pas sur `http://localhost:8000`, modifiez le fichier `app.js` :

```javascript
// Ligne 4 dans app.js
const API_BASE_URL = 'http://VOTRE_ADRESSE:PORT';
```

## ⚠️ Dépannage

### L'interface ne se connecte pas à l'API

**Problème :** Erreur CORS ou connexion refusée

**Solution :**
1. Vérifiez que l'API est lancée (`docker ps` ou terminal uvicorn actif)
2. Assurez-vous que l'URL dans `app.js` est correcte
3. Vérifiez les paramètres CORS dans votre backend FastAPI

### Les images ne s'uploadent pas

**Problème :** Erreur lors de l'upload

**Solution :**
1. Vérifiez le format de l'image (JPG, PNG, JPEG)
2. Réduisez la taille de l'image si elle est trop grande (< 5MB recommandé)
3. Vérifiez les logs de l'API dans le terminal

### Le chat ne répond pas

**Problème :** Pas de réponse du bot

**Solution :**
1. Vérifiez que l'endpoint `/api/v1/chat` est actif
2. Consultez les logs de l'API
3. Testez l'endpoint dans Swagger UI (http://localhost:8000/docs)

## 📸 Captures d'Écran

### Page d'Accueil
Interface d'upload avec glisser-déposer et prévisualisation

### Résultats de Détection
Diagnostic complet avec traitements et conseils

### Chat Bot
Interface conversationnelle avec suggestions

### Dashboard
Statistiques et données en temps réel

## 🚀 Prochaines Étapes

Pour améliorer l'interface :

1. **Ajouter l'authentification**
   - Système de login/register
   - Gestion des profils utilisateurs

2. **Historique des détections**
   - Sauvegarder les analyses
   - Consulter l'historique

3. **Mode hors-ligne**
   - Progressive Web App (PWA)
   - Cache des données

4. **Notifications**
   - Alertes pour nouvelles maladies
   - Rappels de traitement

## 📞 Support

Pour toute question ou problème :
- Consultez la documentation API : http://localhost:8000/docs
- Vérifiez les logs de l'API dans le terminal
- Inspectez la console du navigateur (F12) pour les erreurs JavaScript

## 📝 Notes Techniques

**Technologies utilisées :**
- HTML5
- CSS3 (Variables CSS, Flexbox, Grid)
- JavaScript Vanilla (ES6+)
- Fetch API pour les requêtes
- Design Responsive

**Compatibilité navigateurs :**
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

---

**Projet de Fin d'année - 2025**

🌾 AgriDetect v1.0.0 - Détection Intelligente des Maladies des Cultures
