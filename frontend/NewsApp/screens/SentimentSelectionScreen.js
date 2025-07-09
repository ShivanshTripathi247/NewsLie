import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, StatusBar } from 'react-native';
import { APP_CONFIG } from '../constants/config';
import newsAPI from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

const SentimentSelectionScreen = ({ navigation }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [apiHealth, setApiHealth] = useState(false);

  useEffect(() => {
    checkAPIHealth();
  }, []);

  const checkAPIHealth = async () => {
    try {
      setLoading(true);
      setError(null);
      await newsAPI.healthCheck();
      setApiHealth(true);
    } catch (err) {
      setError(err.message);
      setApiHealth(false);
    } finally {
      setLoading(false);
    }
  };

  const handleSentimentSelect = (sentiment) => {
    if (!apiHealth) {
      setError('API is not available. Please try again.');
      return;
    }
    navigation.navigate('Categories', { sentiment });
  };

  if (loading) {
    return <LoadingSpinner message="Checking system status..." />;
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={checkAPIHealth} />;
  }

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#f5f5f5" />
      
      <View style={styles.header}>
        <Text style={styles.title}>News Sentiment</Text>
        <Text style={styles.subtitle}>How are you feeling today?</Text>
        <Text style={styles.description}>Choose the type of news you want to read</Text>
      </View>
      
      <View style={styles.buttonContainer}>
        <TouchableOpacity 
          style={[styles.button, styles.positiveButton]}
          onPress={() => handleSentimentSelect('positive')}
        >
          <Text style={styles.buttonIcon}>😊</Text>
          <Text style={styles.buttonText}>Positive News</Text>
          <Text style={styles.buttonSubtext}>Uplifting and good news</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.button, styles.negativeButton]}
          onPress={() => handleSentimentSelect('negative')}
        >
          <Text style={styles.buttonIcon}>😔</Text>
          <Text style={styles.buttonText}>Negative News</Text>
          <Text style={styles.buttonSubtext}>Important issues and concerns</Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.footer}>
        <Text style={styles.footerText}>✅ System Status: Healthy</Text>
        <Text style={styles.footerText}>📊 Headlines Available: 700+</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    paddingHorizontal: 20,
  },
  header: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 60,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#34495e',
    marginBottom: 8,
  },
  description: {
    fontSize: 16,
    color: '#7f8c8d',
    textAlign: 'center',
    marginBottom: 40,
  },
  buttonContainer: {
    flex: 1,
    justifyContent: 'center',
    gap: 20,
  },
  button: {
    padding: 24,
    borderRadius: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  positiveButton: {
    backgroundColor: '#27ae60',
  },
  negativeButton: {
    backgroundColor: '#e74c3c',
  },
  buttonIcon: {
    fontSize: 48,
    marginBottom: 8,
  },
  buttonText: {
    color: 'white',
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  buttonSubtext: {
    color: 'white',
    fontSize: 14,
    opacity: 0.9,
    textAlign: 'center',
  },
  footer: {
    paddingVertical: 20,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 12,
    color: '#95a5a6',
    marginVertical: 2,
  },
});

export default SentimentSelectionScreen;
