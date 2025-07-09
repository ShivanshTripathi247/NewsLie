// API Configuration
export const API_CONFIG = {
  BASE_URL: 'http://192.168.1.4:5000/api', // Replace with your actual IP
  TIMEOUT: 10000,
};

// App Configuration
export const APP_CONFIG = {
  CATEGORIES: [
    { id: 'politics', name: 'Politics', icon: '🏛️', color: '#3498db' },
    { id: 'sports', name: 'Sports', icon: '⚽', color: '#e74c3c' },
    { id: 'business', name: 'Business', icon: '💼', color: '#2ecc71' },
    { id: 'arts', name: 'Arts', icon: '🎨', color: '#9b59b6' },
    { id: 'earth', name: 'Earth', icon: '🌍', color: '#27ae60' },
    { id: 'technology', name: 'Technology', icon: '💻', color: '#f39c12' }
  ],
  SENTIMENTS: {
    positive: { name: 'Positive', icon: '😊', color: '#27ae60' },
    negative: { name: 'Negative', icon: '😔', color: '#e74c3c' }
  }
};
