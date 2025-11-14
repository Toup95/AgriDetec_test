import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Image, Alert, ActivityIndicator, ScrollView } from 'react-native';
import { WebView } from 'react-native-webview';
import * as ImagePicker from 'expo-image-picker';
import axios from 'axios';

// Configuration API - CHANGEZ VOTRE IP ICI
const API_BASE_URL = 'http://192.168.1.10:8000';

// Traductions
const translations = {
  fr: {
    selectLanguage: 'Choisissez votre langue',
    title: 'AgriDetect AI',
    subtitle: 'Détection des maladies des plantes',
    analyzeButton: 'Analyser une plante 🌱',
    chatbotButton: '💬 Assistant Agricole',
    dashboardButton: '📊 Tableau de bord',
    connected: 'Connecté ✓',
    disconnected: 'Déconnecté ✗',
    changeLanguage: 'Changer de langue',
    takePhoto: '📷 Prendre une photo',
    chooseGallery: '🖼️ Galerie',
    analyze: 'Analyser',
    analyzing: 'Analyse...',
    result: 'Résultat',
    confidence: 'Confiance',
    backHome: 'Retour',
    back: '← Retour',
  },
  wo: {
    selectLanguage: 'Tànn sa làkk',
    title: 'AgriDetect AI',
    subtitle: 'Jàngale fetal yi',
    analyzeButton: 'Xool ginnaaw 🌱',
    chatbotButton: '💬 Ndimbalu yoon',
    dashboardButton: '📊 Tablo',
    connected: 'Jàpp na ✓',
    disconnected: 'Jàppul ✗',
    changeLanguage: 'Soppi làkk',
    takePhoto: '📷 Foto',
    chooseGallery: '🖼️ Nataal',
    analyze: 'Xool',
    analyzing: 'Dafa xool...',
    result: 'Laylatee',
    confidence: 'Gëm',
    backHome: 'Dellu',
    back: '← Dellu',
  },
  ff: {
    selectLanguage: 'Suɓo ɗemngal maa',
    title: 'AgriDetect AI',
    subtitle: 'Ɗaɓɓitaare masooji',
    analyzeButton: 'Ɗaɓɓitu gampanɗe 🌱',
    chatbotButton: '💬 Ballal wallude',
    dashboardButton: '📊 Taabalde',
    connected: 'Jokki ✓',
    disconnected: 'Jokkiaani ✗',
    changeLanguage: 'Waylu ɗemngal',
    takePhoto: '📷 Natal',
    chooseGallery: '🖼️ Nataaluuji',
    analyze: 'Ɗaɓɓitu',
    analyzing: 'Ɗaɓɓita...',
    result: 'Keewal',
    confidence: 'Jaabawol',
    backHome: 'Rutto',
    back: '← Rutto',
  },
};

export default function App() {
  const [screen, setScreen] = useState('language'); // language, home, camera, result, chatbot, dashboard
  const [language, setLanguage] = useState('fr');
  const [isConnected, setIsConnected] = useState(false);
  const [image, setImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);

  const t = translations[language];

  useEffect(() => {
    checkConnection();
  }, []);

  const checkConnection = async () => {
    try {
      await axios.get(`${API_BASE_URL}/`);
      setIsConnected(true);
    } catch (error) {
      setIsConnected(false);
    }
  };

  const selectLanguage = (lang) => {
    setLanguage(lang);
    setScreen('home');
  };

  const takePhoto = async () => {
    try {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Erreur', 'Permission refusée');
        return;
      }

      const result = await ImagePicker.launchCameraAsync({ quality: 0.8 });
      if (!result.canceled) {
        setImage(result.assets[0].uri);
      }
    } catch (error) {
      console.error(error);
    }
  };

  const pickImage = async () => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Erreur', 'Permission refusée');
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({ quality: 0.8 });
      if (!result.canceled) {
        setImage(result.assets[0].uri);
      }
    } catch (error) {
      console.error(error);
    }
  };

  const analyzeImage = async () => {
    if (!image) return;

    setIsAnalyzing(true);
    try {
      const formData = new FormData();
      const filename = image.split('/').pop();
      const match = /\.(\w+)$/.exec(filename);
      const type = match ? `image/${match[1]}` : 'image/jpeg';

      formData.append('file', {
        uri: image,
        name: filename,
        type: type,
      });

      const response = await axios.post(`${API_BASE_URL}/api/v1/detect-disease`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 30000,
      });

      setResult(response.data);
      setScreen('result');
    } catch (error) {
      Alert.alert('Erreur', 'Erreur lors de l\'analyse');
      console.error(error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const resetAndGoHome = () => {
    setImage(null);
    setResult(null);
    setScreen('home');
  };

  // Écran de sélection de langue
  if (screen === 'language') {
    return (
      <View style={styles.container}>
        <Text style={styles.bigTitle}>AgriDetect AI</Text>
        <Text style={styles.subtitle}>Détection des maladies des plantes</Text>
        
        <View style={styles.card}>
          <Text style={styles.prompt}>{t.selectLanguage}</Text>
          
          <TouchableOpacity style={styles.langButton} onPress={() => selectLanguage('fr')}>
            <Text style={styles.langButtonText}>🇫🇷 Français</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.langButton} onPress={() => selectLanguage('wo')}>
            <Text style={styles.langButtonText}>🇸🇳 Wolof</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.langButton} onPress={() => selectLanguage('ff')}>
            <Text style={styles.langButtonText}>🇸🇳 Pulaar</Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.footer}>Pour les agriculteurs du Sénégal 🌾</Text>
      </View>
    );
  }

  // Écran d'accueil avec les 3 fonctionnalités
  if (screen === 'home') {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>{t.title}</Text>
          <Text style={styles.subtitle}>{t.subtitle}</Text>
          <Text style={[styles.status, { color: isConnected ? '#fff' : '#ffcdd2' }]}>
            {isConnected ? t.connected : t.disconnected}
          </Text>
        </View>

        <View style={styles.content}>
          <TouchableOpacity 
            style={styles.featureCard}
            onPress={() => setScreen('camera')}
          >
            <Text style={styles.featureEmoji}>🌱</Text>
            <Text style={styles.featureTitle}>Détection</Text>
            <Text style={styles.featureDesc}>Analyser les maladies des plantes</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.featureCard}
            onPress={() => setScreen('chatbot')}
          >
            <Text style={styles.featureEmoji}>💬</Text>
            <Text style={styles.featureTitle}>Assistant</Text>
            <Text style={styles.featureDesc}>Poser des questions agricoles</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.featureCard}
            onPress={() => setScreen('dashboard')}
          >
            <Text style={styles.featureEmoji}>📊</Text>
            <Text style={styles.featureTitle}>Statistiques</Text>
            <Text style={styles.featureDesc}>Tableau de bord et historique</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.secondaryButton}
            onPress={() => setScreen('language')}
          >
            <Text style={styles.secondaryButtonText}>{t.changeLanguage}</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  // Écran Chatbot avec WebView
  if (screen === 'chatbot') {
    return (
      <View style={styles.webviewContainer}>
        <View style={styles.webviewHeader}>
          <TouchableOpacity onPress={() => setScreen('home')} style={styles.backButton}>
            <Text style={styles.backButtonText}>{t.back}</Text>
          </TouchableOpacity>
          <Text style={styles.webviewTitle}>💬 Assistant Agricole</Text>
        </View>
        <WebView
          source={{ uri: `${API_BASE_URL}/chat.html` }}
          style={styles.webview}
          startInLoadingState={true}
          renderLoading={() => (
            <View style={styles.loadingView}>
              <ActivityIndicator size="large" color="#4CAF50" />
              <Text>Chargement...</Text>
            </View>
          )}
        />
      </View>
    );
  }

  // Écran Dashboard avec WebView
  if (screen === 'dashboard') {
    return (
      <View style={styles.webviewContainer}>
        <View style={styles.webviewHeader}>
          <TouchableOpacity onPress={() => setScreen('home')} style={styles.backButton}>
            <Text style={styles.backButtonText}>{t.back}</Text>
          </TouchableOpacity>
          <Text style={styles.webviewTitle}>📊 Tableau de bord</Text>
        </View>
        <WebView
          source={{ uri: `${API_BASE_URL}/dashboard.html` }}
          style={styles.webview}
          startInLoadingState={true}
          renderLoading={() => (
            <View style={styles.loadingView}>
              <ActivityIndicator size="large" color="#4CAF50" />
              <Text>Chargement...</Text>
            </View>
          )}
        />
      </View>
    );
  }

  // Écran de capture/analyse
  if (screen === 'camera') {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>{t.title}</Text>
        </View>

        <View style={styles.imageBox}>
          {image ? (
            <Image source={{ uri: image }} style={styles.image} />
          ) : (
            <View style={styles.placeholder}>
              <Text style={styles.emoji}>🌱</Text>
            </View>
          )}
        </View>

        <View style={styles.content}>
          <TouchableOpacity style={styles.button} onPress={takePhoto}>
            <Text style={styles.buttonText}>{t.takePhoto}</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.button} onPress={pickImage}>
            <Text style={styles.buttonText}>{t.chooseGallery}</Text>
          </TouchableOpacity>

          {image ? (
            <TouchableOpacity 
              style={[styles.bigButton, isAnalyzing ? styles.disabledButton : null]}
              onPress={analyzeImage}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? (
                <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'center' }}>
                  <ActivityIndicator color="white" />
                  <Text style={[styles.bigButtonText, { marginLeft: 10 }]}>{t.analyzing}</Text>
                </View>
              ) : (
                <Text style={styles.bigButtonText}>{t.analyze}</Text>
              )}
            </TouchableOpacity>
          ) : null}

          <TouchableOpacity style={styles.secondaryButton} onPress={resetAndGoHome}>
            <Text style={styles.secondaryButtonText}>{t.backHome}</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  // Écran de résultats
  if (screen === 'result' && result) {
    const disease = result.prediction || result.disease || 'Non identifié';
    const confidence = result.confidence || result.accuracy || 0;
    const isHealthy = disease.toLowerCase().includes('healthy');

    return (
      <ScrollView style={styles.scrollContainer}>
        <View style={styles.header}>
          <Text style={styles.title}>{t.result}</Text>
        </View>

        <Image source={{ uri: image }} style={styles.resultImage} />

        <View style={styles.card}>
          <View style={[styles.badge, { backgroundColor: isHealthy ? '#4CAF50' : '#f44336' }]}>
            <Text style={styles.badgeText}>{disease}</Text>
          </View>

          <Text style={styles.label}>{t.confidence}: {(confidence * 100).toFixed(1)}%</Text>
          
          <View style={styles.progressBar}>
            <View style={[styles.progressFill, { width: `${confidence * 100}%` }]} />
          </View>
        </View>

        <TouchableOpacity style={styles.bigButton} onPress={() => setScreen('camera')}>
          <Text style={styles.bigButtonText}>Nouvelle analyse</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.secondaryButton} onPress={resetAndGoHome}>
          <Text style={styles.secondaryButtonText}>{t.backHome}</Text>
        </TouchableOpacity>
      </ScrollView>
    );
  }

  return null;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#4CAF50',
  },
  scrollContainer: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#4CAF50',
    padding: 30,
    paddingTop: 60,
    alignItems: 'center',
  },
  bigTitle: {
    fontSize: 40,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
    marginTop: 80,
    marginBottom: 10,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    color: 'white',
    textAlign: 'center',
  },
  status: {
    fontSize: 14,
    marginTop: 10,
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
  },
  featureCard: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 25,
    marginVertical: 10,
    alignItems: 'center',
    elevation: 3,
  },
  featureEmoji: {
    fontSize: 50,
    marginBottom: 10,
  },
  featureTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  featureDesc: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    margin: 20,
  },
  prompt: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
    color: '#333',
  },
  langButton: {
    backgroundColor: '#4CAF50',
    padding: 18,
    borderRadius: 10,
    marginVertical: 8,
  },
  langButtonText: {
    color: 'white',
    fontSize: 20,
    textAlign: 'center',
    fontWeight: 'bold',
  },
  bigButton: {
    backgroundColor: '#4CAF50',
    padding: 20,
    borderRadius: 15,
    marginVertical: 10,
  },
  bigButtonText: {
    color: 'white',
    fontSize: 18,
    textAlign: 'center',
    fontWeight: 'bold',
  },
  button: {
    backgroundColor: 'white',
    padding: 18,
    borderRadius: 10,
    marginVertical: 8,
  },
  buttonText: {
    color: '#4CAF50',
    fontSize: 16,
    textAlign: 'center',
    fontWeight: '600',
  },
  secondaryButton: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    marginTop: 10,
  },
  secondaryButtonText: {
    color: '#4CAF50',
    fontSize: 16,
    textAlign: 'center',
    fontWeight: '600',
  },
  disabledButton: {
    backgroundColor: '#ccc',
  },
  imageBox: {
    height: 300,
    backgroundColor: 'white',
    margin: 15,
    borderRadius: 15,
    overflow: 'hidden',
  },
  image: {
    width: '100%',
    height: '100%',
    resizeMode: 'contain',
  },
  resultImage: {
    width: '100%',
    height: 250,
    resizeMode: 'cover',
  },
  placeholder: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emoji: {
    fontSize: 80,
  },
  badge: {
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
  },
  badgeText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  label: {
    fontSize: 16,
    color: '#666',
    marginVertical: 10,
  },
  progressBar: {
    height: 10,
    backgroundColor: '#e0e0e0',
    borderRadius: 5,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#4CAF50',
  },
  footer: {
    fontSize: 14,
    color: 'white',
    textAlign: 'center',
    marginBottom: 30,
  },
  // Styles WebView
  webviewContainer: {
    flex: 1,
    backgroundColor: '#fff',
  },
  webviewHeader: {
    backgroundColor: '#4CAF50',
    paddingTop: 50,
    paddingBottom: 15,
    paddingHorizontal: 15,
    flexDirection: 'row',
    alignItems: 'center',
  },
  backButton: {
    marginRight: 15,
  },
  backButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  webviewTitle: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
  },
  webview: {
    flex: 1,
  },
  loadingView: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
});
