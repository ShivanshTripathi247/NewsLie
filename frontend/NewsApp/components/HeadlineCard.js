import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image } from 'react-native';

const HeadlineCard = ({ headline, onPress }) => {
  const [imageError, setImageError] = useState(false);

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return '#27ae60';
    if (confidence >= 60) return '#f39c12';
    if (confidence >= 40) return '#e67e22';
    return '#e74c3c';
  };

  const getConfidenceLabel = (confidence) => {
    if (confidence >= 80) return 'High';
    if (confidence >= 60) return 'Medium';
    if (confidence >= 40) return 'Low';
    return 'Very Low';
  };

  const hasImage = headline.image_url && !imageError;

  const dateString = headline.created_at || headline.timestamp;
  let displayDate = 'No Date';
  if (dateString) {
    const dateObj = new Date(dateString);
    if (!isNaN(dateObj.getTime())) {
      displayDate = dateObj.toLocaleString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    }
  }

  return (
    <TouchableOpacity style={styles.card} onPress={onPress}>
      {hasImage && (
        <Image
          source={{ uri: headline.image_url }}
          style={styles.image}
          onError={() => setImageError(true)}
          resizeMode="cover"
        />
      )}
      
      <View style={styles.contentContainer}>
        <Text style={styles.headlineText}>{headline.headline}</Text>
        
        <View style={styles.metaContainer}>
          <View style={styles.confidenceContainer}>
            <Text style={styles.confidenceLabel}>Confidence:</Text>
            <View style={[styles.confidenceBadge, { backgroundColor: getConfidenceColor(headline.confidence) }]}>
              <Text style={styles.confidenceText}>
                {headline.confidence}% ({getConfidenceLabel(headline.confidence)})
              </Text>
            </View>
          </View>
          
          <Text style={styles.timestamp}>
            {displayDate}
          </Text>
        </View>
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: 'white',
    marginVertical: 8,
    marginHorizontal: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    overflow: 'hidden',
  },
  image: {
    width: '100%',
    height: 180,
    backgroundColor: '#f8f9fa',
  },
  contentContainer: {
    padding: 16,
  },
  headlineText: {
    fontSize: 16,
    fontWeight: '500',
    lineHeight: 22,
    marginBottom: 12,
    color: '#2c3e50',
  },
  metaContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  confidenceContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  confidenceLabel: {
    fontSize: 12,
    color: '#7f8c8d',
    marginRight: 8,
  },
  confidenceBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  confidenceText: {
    color: 'white',
    fontSize: 11,
    fontWeight: 'bold',
  },
  timestamp: {
    fontSize: 12,
    color: '#95a5a6',
  },
});

export default HeadlineCard;
