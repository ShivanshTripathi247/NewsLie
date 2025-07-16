import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet, RefreshControl, StatusBar, TouchableOpacity,Linking, Alert } from 'react-native';
import { APP_CONFIG } from '../constants/config';
import newsAPI from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import HeadlineCard from '../components/HeadlineCard';
import LocalDatabase from '../services/LocalDatabase';
import BackgroundSync from '../services/BackgroundSync';


const HeadlinesScreen = ({ route, navigation }) => {
  const { sentiment, category } = route.params;
  const [headlines, setHeadlines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadHeadlinesFromLocal();
  }, []);

  const loadHeadlinesFromLocal = async () => {
    setLoading(true);
    setError(null);
    try {
      const localHeadlines = await LocalDatabase.getHeadlines(category, sentiment, 50);
      setHeadlines(localHeadlines);
      if (!localHeadlines || localHeadlines.length === 0) {
        // fallback to API if local is empty
        await fetchHeadlinesFromAPI();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const fetchHeadlinesFromAPI = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await newsAPI.getHeadlines(category, sentiment, { limit: 50 });
      setHeadlines(response.headlines);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await BackgroundSync.syncIfNeeded();
    await loadHeadlinesFromLocal();
  };

  const getFilteredHeadlines = () => {
    if (filter === 'all') return headlines;
    
    const confidenceThresholds = {
      high: 80,
      medium: 60,
      low: 40
    };
    
    const threshold = confidenceThresholds[filter];
    return headlines.filter(headline => headline.confidence >= threshold);
  };

const handleHeadlinePress = async (headline) => {
  try {
    const url = headline.source_url;
    
    // Check if URL is valid and can be opened
    const supported = await Linking.canOpenURL(url);
    
    if (supported) {
      // Open the URL in the device's default browser
      await Linking.openURL(url);
    } else {
      // Show error if URL cannot be opened
      Alert.alert(
        'Cannot Open Link',
        'This link cannot be opened on your device.',
        [{ text: 'OK' }]
      );
    }
  } catch (error) {
    // Handle any errors that occur
    Alert.alert(
      'Error',
      'Failed to open the link. Please try again.',
      [{ text: 'OK' }]
    );
    console.error('Error opening URL:', error);
  }
};


  const renderHeadline = ({ item }) => (
    <HeadlineCard 
      headline={item} 
      onPress={() => handleHeadlinePress(item)}
    />
  );

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Text style={styles.emptyIcon}>📰</Text>
      <Text style={styles.emptyTitle}>No Headlines Found</Text>
      <Text style={styles.emptySubtitle}>
        Try refreshing or selecting a different filter
      </Text>
    </View>
  );

  if (loading) {
    return <LoadingSpinner message="Loading headlines..." />;
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={fetchHeadlinesFromAPI} />;
  }

  const sentimentConfig = APP_CONFIG.SENTIMENTS[sentiment];
  const categoryConfig = APP_CONFIG.CATEGORIES.find(cat => cat.id === category);
  const filteredHeadlines = getFilteredHeadlines();

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#f5f5f5" />
        <View style={styles.backButtonContainer}>
            <TouchableOpacity 
            style={styles.backButton} 
            onPress={() => navigation.goBack()}
            >
            <Text style={styles.backButtonIcon}>←</Text>
            <Text style={styles.backButtonText}>Back</Text>
            </TouchableOpacity>
        </View>
      
      
      <View style={styles.header}>
        <Text style={styles.categoryTitle}>
          {categoryConfig?.icon} {categoryConfig?.name || category}
        </Text>
        <Text style={styles.sentimentIndicator}>
          {sentimentConfig.icon} {sentimentConfig.name} News
        </Text>
        <Text style={styles.headlineCount}>
          {filteredHeadlines.length} headlines available
        </Text>
      </View>

      <View style={styles.filterContainer}>
        <Text style={styles.filterLabel}>Filter by confidence:</Text>
        <View style={styles.filterButtons}>
          {['all', 'high', 'medium', 'low'].map((filterType) => (
            <TouchableOpacity
              key={filterType}
              style={[
                styles.filterButton,
                filter === filterType && styles.activeFilterButton
              ]}
              onPress={() => setFilter(filterType)}
            >
              <Text style={[
                styles.filterButtonText,
                filter === filterType && styles.activeFilterButtonText
              ]}>
                {filterType.charAt(0).toUpperCase() + filterType.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
      
      <FlatList
        data={filteredHeadlines}
        renderItem={renderHeadline}
        keyExtractor={(item, index) => `${item.timestamp}-${index}`}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={renderEmptyState}
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
  categoryTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 4,
  },
  sentimentIndicator: {
    fontSize: 16,
    fontWeight: '600',
    color: '#7f8c8d',
    marginBottom: 4,
  },
  headlineCount: {
    fontSize: 14,
    color: '#95a5a6',
  },
  filterContainer: {
    backgroundColor: 'white',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  filterLabel: {
    fontSize: 14,
    color: '#7f8c8d',
    marginBottom: 8,
  },
  filterButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  filterButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: '#ecf0f1',
  },
  activeFilterButton: {
    backgroundColor: '#3498db',
  },
  filterButtonText: {
    fontSize: 12,
    color: '#7f8c8d',
    fontWeight: '500',
  },
  activeFilterButtonText: {
    color: 'white',
  },
  listContainer: {
    paddingVertical: 8,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 14,
    color: '#7f8c8d',
    textAlign: 'center',
  },
  backButtonContainer: {
  backgroundColor: 'white',
  paddingHorizontal: 20,
  paddingTop: 10,
  paddingBottom: 5,
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


export default HeadlinesScreen;
