import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  FlatList, 
  StyleSheet, 
  RefreshControl, 
  StatusBar, 
  TouchableOpacity,
  Alert,
  Linking
} from 'react-native';
import newsAPI from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import LocalDatabase from '../services/LocalDatabase';
import BackgroundSync from '../services/BackgroundSync';

const LiveFeedScreen = ({ navigation }) => {
  const [headlines, setHeadlines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    loadLiveFeedFromLocal();
  }, []);

  const loadLiveFeedFromLocal = async () => {
    setLoading(true);
    setError(null);
    try {
      const localHeadlines = await LocalDatabase.getLiveFeedHeadlines(30);
      setHeadlines(localHeadlines);
      if (!localHeadlines || localHeadlines.length === 0) {
        // fallback to API if local is empty
        await fetchLiveFeedFromAPI();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const fetchLiveFeedFromAPI = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await newsAPI.getLiveFeed(true);
      setHeadlines(response.headlines || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await BackgroundSync.syncLiveFeed();
    await loadLiveFeedFromLocal();
  };

  const handleHeadlinePress = async (headline) => {
    try {
      const url = headline.source_url;
      const supported = await Linking.canOpenURL(url);
      
      if (supported) {
        await Linking.openURL(url);
      } else {
        Alert.alert(
          'Cannot Open Link',
          'This link cannot be opened on your device.',
          [{ text: 'OK' }]
        );
      }
    } catch (error) {
      Alert.alert(
        'Error',
        'Failed to open the link. Please try again.',
        [{ text: 'OK' }]
      );
    }
  };

  const renderHeadline = ({ item, index }) => {
    // Generate unique key for the TouchableOpacity
    const uniqueKey = `headline_${item.quick_id || item.id || index}_${item.timestamp || Date.now()}`;
    
    return (
      <TouchableOpacity 
        key={uniqueKey}
        style={styles.headlineCard}
        onPress={() => handleHeadlinePress(item)}
      >
        <View style={styles.headlineHeader}>
          <Text style={styles.sourceText}>{item.source}</Text>
          <Text style={styles.categoryBadge}>{item.category?.toUpperCase() || 'NEWS'}</Text>
        </View>
        
        <Text style={styles.headlineText}>{item.headline}</Text>
        
        <View style={styles.headlineFooter}>
          <Text style={styles.timestampText}>
            {item.timestamp ? new Date(item.timestamp).toLocaleTimeString() : 'Unknown time'}
          </Text>
          <Text style={styles.tapHint}>Tap to read →</Text>
        </View>
      </TouchableOpacity>
    );
  };


  const renderHeader = () => (
    <View style={styles.header}>
      <Text style={styles.title}>📰 Live News Feed</Text>
      <Text style={styles.subtitle}>Latest headlines • No analysis</Text>
      {lastUpdated && (
        <Text style={styles.lastUpdated}>
          Last updated: {lastUpdated.toLocaleTimeString()}
        </Text>
      )}
    </View>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Text style={styles.emptyIcon}>📰</Text>
      <Text style={styles.emptyTitle}>No Headlines Available</Text>
      <Text style={styles.emptySubtitle}>
        Pull down to refresh and get the latest news
      </Text>
    </View>
  );

  if (loading) {
    return <LoadingSpinner message="Loading live feed..." />;
  }

  if (error && headlines.length === 0) {
    return <ErrorMessage message={error} onRetry={() => fetchLiveFeedFromAPI()} />;
  }

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#f5f5f5" />
      
      <FlatList
        data={headlines}
        renderItem={renderHeadline}
        keyExtractor={(item, index) => {
          // Create unique key using multiple identifiers
          const baseKey = item.quick_id || item.id || index;
          const timestamp = item.timestamp || Date.now();
          return `headline_${baseKey}_${timestamp}_${index}`;
        }}
        ListHeaderComponent={renderHeader}
        ListEmptyComponent={renderEmptyState}
        refreshControl={
          <RefreshControl 
            refreshing={refreshing} 
            onRefresh={onRefresh}
            colors={['#3498db']}
            tintColor="#3498db"
          />
        }
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
      />
      
      {error && headlines.length > 0 && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorBannerText}>
            ⚠️ {error}
          </Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  listContainer: {
    paddingBottom: 20,
  },
  header: {
    backgroundColor: 'white',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
    marginBottom: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#7f8c8d',
    marginBottom: 8,
  },
  lastUpdated: {
    fontSize: 12,
    color: '#95a5a6',
  },
  headlineCard: {
    backgroundColor: 'white',
    marginHorizontal: 16,
    marginVertical: 6,
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  headlineHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  sourceText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#3498db',
  },
  categoryBadge: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#7f8c8d',
    backgroundColor: '#ecf0f1',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
  },
  headlineText: {
    fontSize: 16,
    fontWeight: '500',
    lineHeight: 22,
    color: '#2c3e50',
    marginBottom: 12,
  },
  headlineFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  timestampText: {
    fontSize: 12,
    color: '#95a5a6',
  },
  tapHint: {
    fontSize: 12,
    color: '#3498db',
    fontWeight: '500',
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
  errorBanner: {
    backgroundColor: '#e74c3c',
    padding: 12,
    margin: 16,
    borderRadius: 8,
  },
  errorBannerText: {
    color: 'white',
    fontSize: 14,
    textAlign: 'center',
  },
});

export default LiveFeedScreen;
