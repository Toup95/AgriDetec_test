import React from 'react';
import { View, Text, ScrollView, Image, TouchableOpacity, StyleSheet } from 'react-native';

const translations = {
  fr: {
    title: 'Résultat de l\'analyse',
    disease: 'Maladie détectée',
    confidence: 'Niveau de confiance',
    recommendations: 'Recommandations',
    analyzeAnother: 'Analyser une autre plante',
    backHome: 'Retour à l\'accueil',
    healthy: 'Plante saine',
  },
  wo: {
    title: 'Laylatee ci xool bi',
    disease: 'Fetal bu gis',
    confidence: 'Nivo bu gëm',
    recommendations: 'Laajante',
    analyzeAnother: 'Xool beneen ginnaaw',
    backHome: 'Dellu ci bët',
    healthy: 'Ginnaaw bu baax',
  },
  ff: {
    title: 'Keewal ɗaɓɓitgol',
    disease: 'Masoojo ɗaɓɓitngo',
    confidence: 'Daraje jaabawol',
    recommendations: 'Cadeeji',
    analyzeAnother: 'Ɗaɓɓitu goɗɗo gampanɗe',
    backHome: 'Rutto e jaɓɓorgo',
    healthy: 'Gampanɗe hino woodi',
  },
};

const ResultScreen = ({ route, navigation }) => {
  const { language, image, result } = route.params;
  const t = translations[language];

  // Extraction des données du résultat
  const disease = result?.prediction || result?.disease || 'Non identifié';
  const confidence = result?.confidence || result?.accuracy || 0;
  const recommendations = result?.recommendations || result?.treatment || [];
  const isHealthy = disease.toLowerCase().includes('healthy') || 
                    disease.toLowerCase().includes('sain');

  const getConfidenceColor = () => {
    if (confidence >= 0.8) return '#4CAF50';
    if (confidence >= 0.6) return '#FFC107';
    return '#f44336';
  };

  const handleAnalyzeAnother = () => {
    navigation.navigate('Camera', { language });
  };

  const handleBackHome = () => {
    navigation.navigate('Home', { language });
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>{t.title}</Text>
      </View>

      <View style={styles.imageContainer}>
        <Image source={{ uri: image }} style={styles.image} />
      </View>

      <View style={styles.resultCard}>
        <View style={styles.diseaseContainer}>
          <Text style={styles.label}>{t.disease}:</Text>
          <View style={[
            styles.diseaseBadge,
            { backgroundColor: isHealthy ? '#4CAF50' : '#f44336' }
          ]}>
            <Text style={styles.diseaseText}>
              {isHealthy ? `✓ ${t.healthy}` : disease}
            </Text>
          </View>
        </View>

        <View style={styles.confidenceContainer}>
          <Text style={styles.label}>{t.confidence}:</Text>
          <View style={styles.progressBar}>
            <View 
              style={[
                styles.progressFill,
                { 
                  width: `${confidence * 100}%`,
                  backgroundColor: getConfidenceColor()
                }
              ]}
            />
          </View>
          <Text style={[styles.confidenceText, { color: getConfidenceColor() }]}>
            {(confidence * 100).toFixed(1)}%
          </Text>
        </View>

        {!isHealthy && recommendations.length > 0 && (
          <View style={styles.recommendationsContainer}>
            <Text style={styles.recommendationsTitle}>{t.recommendations}:</Text>
            {recommendations.map((rec, index) => (
              <View key={index} style={styles.recommendationItem}>
                <Text style={styles.bullet}>•</Text>
                <Text style={styles.recommendationText}>{rec}</Text>
              </View>
            ))}
          </View>
        )}

        {isHealthy && (
          <View style={styles.healthyMessage}>
            <Text style={styles.healthyEmoji}>🎉</Text>
            <Text style={styles.healthyText}>
              Votre plante est en bonne santé ! Continuez à en prendre soin.
            </Text>
          </View>
        )}
      </View>

      <View style={styles.buttonContainer}>
        <TouchableOpacity 
          style={styles.primaryButton}
          onPress={handleAnalyzeAnother}
        >
          <Text style={styles.primaryButtonText}>{t.analyzeAnother}</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.secondaryButton}
          onPress={handleBackHome}
        >
          <Text style={styles.secondaryButtonText}>{t.backHome}</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#4CAF50',
    padding: 20,
    paddingTop: 50,
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  imageContainer: {
    height: 250,
    backgroundColor: 'white',
    margin: 15,
    borderRadius: 15,
    overflow: 'hidden',
    elevation: 3,
  },
  image: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  resultCard: {
    backgroundColor: 'white',
    margin: 15,
    padding: 20,
    borderRadius: 15,
    elevation: 3,
  },
  diseaseContainer: {
    marginBottom: 20,
  },
  label: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
    fontWeight: '600',
  },
  diseaseBadge: {
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  diseaseText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
  },
  confidenceContainer: {
    marginBottom: 20,
  },
  progressBar: {
    height: 12,
    backgroundColor: '#e0e0e0',
    borderRadius: 6,
    marginVertical: 8,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 6,
  },
  confidenceText: {
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  recommendationsContainer: {
    marginTop: 10,
  },
  recommendationsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  recommendationItem: {
    flexDirection: 'row',
    marginBottom: 12,
    paddingLeft: 10,
  },
  bullet: {
    fontSize: 16,
    color: '#4CAF50',
    marginRight: 10,
    fontWeight: 'bold',
  },
  recommendationText: {
    flex: 1,
    fontSize: 15,
    color: '#555',
    lineHeight: 22,
  },
  healthyMessage: {
    alignItems: 'center',
    marginTop: 10,
  },
  healthyEmoji: {
    fontSize: 50,
    marginBottom: 10,
  },
  healthyText: {
    fontSize: 16,
    color: '#4CAF50',
    textAlign: 'center',
    lineHeight: 24,
  },
  buttonContainer: {
    padding: 15,
    marginBottom: 30,
  },
  primaryButton: {
    backgroundColor: '#4CAF50',
    padding: 18,
    borderRadius: 10,
    marginVertical: 8,
    elevation: 3,
  },
  primaryButtonText: {
    color: 'white',
    fontSize: 18,
    textAlign: 'center',
    fontWeight: 'bold',
  },
  secondaryButton: {
    backgroundColor: 'white',
    padding: 18,
    borderRadius: 10,
    marginVertical: 8,
    borderWidth: 2,
    borderColor: '#4CAF50',
  },
  secondaryButtonText: {
    color: '#4CAF50',
    fontSize: 18,
    textAlign: 'center',
    fontWeight: '600',
  },
});

export default ResultScreen;
