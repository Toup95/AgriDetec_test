import axios from 'axios';

// Configuration de l'API
// IMPORTANT: Remplacez par l'adresse IP de votre ordinateur
// Pour trouver votre IP: ouvrez cmd et tapez "ipconfig"
// Cherchez "Adresse IPv4" dans la section WiFi
const API_BASE_URL = 'http://192.168.1.10:8000'; // Changez cette IP !

// Service pour analyser une image de plante
export const analyzePlantImage = async (imageUri) => {
  try {
    const formData = new FormData();
    
    // Préparer l'image pour l'envoi
    const filename = imageUri.split('/').pop();
    const match = /\.(\w+)$/.exec(filename);
    const type = match ? `image/${match[1]}` : 'image/jpeg';

    formData.append('file', {
      uri: imageUri,
      name: filename,
      type: type,
    });

    // Envoyer au backend
    const response = await axios.post(
      `${API_BASE_URL}/api/predict`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000, // 30 secondes
      }
    );

    return response.data;
  } catch (error) {
    console.error('Erreur lors de l\'analyse:', error);
    throw error;
  }
};

// Tester la connexion au serveur
export const testConnection = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/`);
    return response.data;
  } catch (error) {
    console.error('Erreur de connexion:', error);
    return null;
  }
};

export default {
  analyzePlantImage,
  testConnection,
};
