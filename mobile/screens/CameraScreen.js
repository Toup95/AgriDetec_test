import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Image, Alert, ActivityIndicator } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { analyzePlantImage } from '../services/api';

const translations = {
  fr: {
    title: 'Analyser votre plante',
    takePhoto: '📷 Prendre une photo',
    chooseGallery: '🖼️ Choisir de la galerie',
    analyze: 'Analyser l\'image',
    analyzing: 'Analyse en cours...',
    selectImage: 'Sélectionnez ou prenez une photo de votre plante',
    errorTitle: 'Erreur',
    errorPermission: 'Permission refusée pour accéder à la caméra/galerie',
    errorAnalysis: 'Erreur lors de l\'analyse. Vérifiez votre connexion.',
  },
  wo: {
    title: 'Xool sa ginnaaw',
    takePhoto: '📷 Foto bi',
    chooseGallery: '🖼️ Jël ci nataal',
    analyze: 'Xool nataal bi',
    analyzing: 'Dafa ngi xoolxool...',
    selectImage: 'Tànn walla foto sa ginnaaw',
    errorTitle: 'Njumte',
    errorPermission: 'Jamontalul kamera/nataal',
    errorAnalysis: 'Njumte ci xool bi. Xoolal sa jumtukaay.',
  },
  ff: {
    title: 'Ɗaɓɓitu gampanɗe maa',
    takePhoto: '📷 Jogo natal',
    chooseGallery: '🖼️ Suɓo e nataaluuji',
    analyze: 'Ɗaɓɓitu natal',
    analyzing: 'Ina ɗaɓɓita...',
    selectImage: 'Suɓo walla jogo natal gampanɗe maa',
    errorTitle: 'Juumre',
    errorPermission: 'Jaabidaama kamera/nataaluuji',
    errorAnalysis: 'Juumre e ɗaɓɓitgol. Ƴeewto jogitagol maa.',
  },
};

const CameraScreen = ({ route, navigation }) => {
  const language = route.params?.language || 'fr';
  const t = translations[language];
  const [image, setImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const takePhoto = async () => {
    try {
      const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
      
      if (permissionResult.granted === false) {
        Alert.alert(t.errorTitle, t.errorPermission);
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        quality: 0.8,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        setImage(result.assets[0].uri);
      }
    } catch (error) {
      console.error('Erreur caméra:', error);
    }
  };

  const pickImage = async () => {
    try {
      const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
      
      if (permissionResult.granted === false) {
        Alert.alert(t.errorTitle, t.errorPermission);
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        quality: 0.8,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        setImage(result.assets[0].uri);
      }
    } catch (error) {
      console.error('Erreur galerie:', error);
    }
  };

  const analyzeImage = async () => {
    if (!image) return;

    setIsAnalyzing(true);
    try {
      const result = await analyzePlantImage(image);
      
      navigation.navigate('Result', {
        language,
        image,
        result,
      });
    } catch (error) {
      Alert.alert(t.errorTitle, t.errorAnalysis);
      console.error('Erreur:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t.title}</Text>

      <View style={styles.imageContainer}>
        {image ? (
          <Image source={{ uri: image }} style={styles.image} />
        ) : (
          <View style={styles.placeholderContainer}>
            <Text style={styles.placeholder}>🌱</Text>
            <Text style={styles.placeholderText}>{t.selectImage}</Text>
          </View>
        )}
      </View>

      <View style={styles.buttonContainer}>
        <TouchableOpacity 
          style={styles.button}
          onPress={takePhoto}
          disabled={isAnalyzing}
        >
          <Text style={styles.buttonText}>{t.takePhoto}</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.button}
          onPress={pickImage}
          disabled={isAnalyzing}
        >
          <Text style={styles.buttonText}>{t.chooseGallery}</Text>
        </TouchableOpacity>

        {image ? (
          <TouchableOpacity 
            style={[styles.analyzeButton, isAnalyzing ? styles.disabledButton : null]}
            onPress={analyzeImage}
            disabled={isAnalyzing}
          >
            {isAnalyzing ? (
              <View style={styles.loadingContainer}>
                <ActivityIndicator color="white" size="small" />
                <Text style={styles.analyzeButtonText}> {t.analyzing}</Text>
              </View>
            ) : (
              <Text style={styles.analyzeButtonText}>{t.analyze}</Text>
            )}
          </TouchableOpacity>
        ) : null}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4CAF50',
    textAlign: 'center',
    marginTop: 40,
    marginBottom: 20,
  },
  imageContainer: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: 15,
    overflow: 'hidden',
    marginVertical: 20,
    elevation: 3,
  },
  image: {
    width: '100%',
    height: '100%',
    resizeMode: 'contain',
  },
  placeholderContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  placeholder: {
    fontSize: 80,
    marginBottom: 20,
  },
  placeholderText: {
    fontSize: 16,
    color: '#999',
    textAlign: 'center',
    paddingHorizontal: 40,
  },
  buttonContainer: {
    marginBottom: 20,
  },
  button: {
    backgroundColor: 'white',
    padding: 18,
    borderRadius: 10,
    marginVertical: 8,
    borderWidth: 2,
    borderColor: '#4CAF50',
  },
  buttonText: {
    color: '#4CAF50',
    fontSize: 18,
    textAlign: 'center',
    fontWeight: '600',
  },
  analyzeButton: {
    backgroundColor: '#4CAF50',
    padding: 18,
    borderRadius: 10,
    marginTop: 10,
    elevation: 5,
  },
  disabledButton: {
    backgroundColor: '#ccc',
  },
  analyzeButtonText: {
    color: 'white',
    fontSize: 18,
    textAlign: 'center',
    fontWeight: 'bold',
  },
  loadingContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default CameraScreen;
