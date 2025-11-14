import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { testConnection } from '../services/api';

const translations = {
  fr: {
    title: 'AgriDetect AI',
    subtitle: 'Détection des maladies des plantes',
    analyzeButton: 'Analyser une plante 🌱',
    connectionStatus: 'État de la connexion',
    connected: 'Connecté au serveur ✓',
    disconnected: 'Serveur non disponible ✗',
    changeLanguage: 'Changer de langue',
    info: 'Prenez une photo de votre plante pour détecter les maladies',
  },
  wo: {
    title: 'AgriDetect AI',
    subtitle: 'Jàngale ay fetal yi ci ginnaaw',
    analyzeButton: 'Xool ginnaaw bi 🌱',
    connectionStatus: 'Jumtukaay',
    connected: 'Jumtukaay bu baax ✓',
    disconnected: 'Amul jumtukaay ✗',
    changeLanguage: 'Soppi làkk',
    info: 'Foto ginnaaw bi ngir gisee fetal yi',
  },
  ff: {
    title: 'AgriDetect AI',
    subtitle: 'Ɗaɓɓitaare masooji gampanɗe',
    analyzeButton: 'Ɗaɓɓitu gampanɗe 🌱',
    connectionStatus: 'Golle sarworde',
    connected: 'Sarworde ina golli ✓',
    disconnected: 'Sarworde alaa ✗',
    changeLanguage: 'Waylu ɗemngal',
    info: 'Jogaa natal gampanɗe maa ngam ɗaɓɓitde masooji',
  },
};

const HomeScreen = ({ route, navigation }) => {
  const language = route.params?.language || 'fr';
  const t = translations[language];
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    checkConnection();
  }, []);

  const checkConnection = async () => {
    const result = await testConnection();
    setIsConnected(result !== null);
  };

  const handleAnalyze = () => {
    if (!isConnected) {
      Alert.alert(
        'Erreur',
        'Le serveur n\'est pas disponible. Vérifiez que votre backend FastAPI est démarré.',
        [{ text: 'OK' }]
      );
      return;
    }
    navigation.navigate('Camera', { language });
  };

  const handleChangeLanguage = () => {
    navigation.navigate('Language');
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>{t.title}</Text>
        <Text style={styles.subtitle}>{t.subtitle}</Text>
      </View>

      <View style={styles.content}>
        <View style={styles.statusContainer}>
          <Text style={styles.statusTitle}>{t.connectionStatus}:</Text>
          <Text style={[
            styles.statusText,
            { color: isConnected ? '#4CAF50' : '#f44336' }
          ]}>
            {isConnected ? t.connected : t.disconnected}
          </Text>
        </View>

        <Text style={styles.info}>{t.info}</Text>

        <TouchableOpacity 
          style={[styles.analyzeButton, !isConnected && styles.disabledButton]}
          onPress={handleAnalyze}
        >
          <Text style={styles.analyzeButtonText}>{t.analyzeButton}</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.languageButton}
          onPress={handleChangeLanguage}
        >
          <Text style={styles.languageButtonText}>{t.changeLanguage}</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>AgriDetect AI v1.0</Text>
        <Text style={styles.footerText}>🇸🇳 Pour le Sénégal et l'Afrique de l'Ouest</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#4CAF50',
    padding: 30,
    paddingTop: 60,
    alignItems: 'center',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    color: 'white',
  },
  content: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
  },
  statusContainer: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    marginBottom: 30,
    alignItems: 'center',
    elevation: 2,
  },
  statusTitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  statusText: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  info: {
    fontSize: 16,
    textAlign: 'center',
    color: '#666',
    marginBottom: 30,
    lineHeight: 24,
  },
  analyzeButton: {
    backgroundColor: '#4CAF50',
    padding: 20,
    borderRadius: 15,
    marginVertical: 10,
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  disabledButton: {
    backgroundColor: '#ccc',
  },
  analyzeButtonText: {
    color: 'white',
    fontSize: 20,
    textAlign: 'center',
    fontWeight: 'bold',
  },
  languageButton: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    marginTop: 10,
    borderWidth: 1,
    borderColor: '#4CAF50',
  },
  languageButtonText: {
    color: '#4CAF50',
    fontSize: 16,
    textAlign: 'center',
    fontWeight: '600',
  },
  footer: {
    padding: 20,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 12,
    color: '#999',
    marginVertical: 2,
  },
});

export default HomeScreen;
