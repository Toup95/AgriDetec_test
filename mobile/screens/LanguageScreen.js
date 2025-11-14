import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Image } from 'react-native';

const LanguageScreen = ({ navigation }) => {
  const selectLanguage = (language) => {
    // Naviguer vers l'écran d'accueil avec la langue sélectionnée
    navigation.navigate('Home', { language });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>AgriDetect AI</Text>
      <Text style={styles.subtitle}>Détection des maladies des plantes</Text>
      
      <View style={styles.languageContainer}>
        <Text style={styles.prompt}>Choisissez votre langue / Select your language</Text>
        
        <TouchableOpacity 
          style={styles.languageButton}
          onPress={() => selectLanguage('fr')}
        >
          <Text style={styles.languageText}>🇫🇷 Français</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.languageButton}
          onPress={() => selectLanguage('wo')}
        >
          <Text style={styles.languageText}>🇸🇳 Wolof</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.languageButton}
          onPress={() => selectLanguage('ff')}
        >
          <Text style={styles.languageText}>🇸🇳 Pulaar</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.footer}>Pour les agriculteurs du Sénégal 🌾</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#4CAF50',
    padding: 20,
    justifyContent: 'center',
  },
  title: {
    fontSize: 36,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 18,
    color: 'white',
    textAlign: 'center',
    marginBottom: 50,
  },
  languageContainer: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    marginVertical: 20,
  },
  prompt: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
    color: '#333',
  },
  languageButton: {
    backgroundColor: '#4CAF50',
    padding: 18,
    borderRadius: 10,
    marginVertical: 8,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  languageText: {
    color: 'white',
    fontSize: 20,
    textAlign: 'center',
    fontWeight: 'bold',
  },
  footer: {
    fontSize: 14,
    color: 'white',
    textAlign: 'center',
    marginTop: 30,
  },
});

export default LanguageScreen;
