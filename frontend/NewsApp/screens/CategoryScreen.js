import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, FlatList, StatusBar } from 'react-native';
import { APP_CONFIG } from '../constants/config';
import newsAPI from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

const CategoryScreen = ({ route, navigation }) => {
  const { sentiment } = route.params;
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await newsAPI.getCategories();
      setCategories(response.categories);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCategorySelect = (category) => {
    navigation.navigate('Headlines', { sentiment, category });
  };

  const getCategoryConfig = (categoryId) => {
    return APP_CONFIG.CATEGORIES.find(cat => cat.id === categoryId) || {
      id: categoryId,
      name: categoryId.charAt(0).toUpperCase() + categoryId.slice(1),
      icon: '📰',
      color: '#3498db'
    };
  };

  const renderCategory = ({ item }) => {
    const config = getCategoryConfig(item);
    
    return (
      <TouchableOpacity 
        style={[styles.categoryCard, { borderLeftColor: config.color }]}
        onPress={() => handleCategorySelect(item)}
      >
        <Text style={styles.categoryIcon}>{config.icon}</Text>
        <Text style={styles.categoryName}>{config.name}</Text>
        <Text style={styles.categoryArrow}>→</Text>
      </TouchableOpacity>
    );
  };

  if (loading) {
    return <LoadingSpinner message="Loading categories..." />;
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={fetchCategories} />;
  }

  const sentimentConfig = APP_CONFIG.SENTIMENTS[sentiment];

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#f5f5f5" />
      
      
      <View style={styles.header}>
        <Text style={styles.sentimentIndicator}>
          {sentimentConfig.icon} {sentimentConfig.name} News
        </Text>
        <Text style={styles.title}>Choose a Category</Text>
        <Text style={styles.subtitle}>Select the topic you're interested in</Text>
      </View>
      <View style={styles.backButtonContainer}>
            <TouchableOpacity 
            style={styles.backButton} 
            onPress={() => navigation.goBack()}
            >
            <Text style={styles.backButtonIcon}>←</Text>
            <Text style={styles.backButtonText}>Back</Text>
            </TouchableOpacity>
        </View>
      
      <FlatList
        data={categories}
        renderItem={renderCategory}
        keyExtractor={(item) => item}
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 16,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  sentimentIndicator: {
    fontSize: 16,
    fontWeight: '600',
    color: '#7f8c8d',
    marginBottom: 4,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#7f8c8d',
  },
  listContainer: {
    padding: 16,
  },
  categoryCard: {
    backgroundColor: 'white',
    padding: 20,
    marginVertical: 8,
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  categoryIcon: {
    fontSize: 32,
    marginRight: 16,
  },
  categoryName: {
    flex: 1,
    fontSize: 18,
    fontWeight: '600',
    color: '#2c3e50',
  },
  categoryArrow: {
    fontSize: 18,
    color: '#bdc3c7',
  },
backButton: {
  flexDirection: 'row',
  alignItems: 'center',
  paddingVertical: 8,
  paddingHorizontal: 12,
  backgroundColor: '#f8f9fa',
  borderRadius: 20,
  alignSelf: 'flex-start',
},
backButtonIcon: {
  fontSize: 18,
  color: '#3498db',
  marginRight: 6,
},
backButtonText: {
  fontSize: 16,
  color: '#3498db',
  fontWeight: '500',
},

});

export default CategoryScreen;
