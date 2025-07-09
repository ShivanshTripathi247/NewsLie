import axios from 'axios';
import { API_CONFIG } from '../constants/config';

class NewsAPI {
  constructor() {
    this.client = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Get all categories
  async getCategories() {
    try {
      const response = await this.client.get('/categories');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Get headlines for specific category and sentiment
  async getHeadlines(category, sentiment, options = {}) {
    try {
      const params = {
        limit: options.limit || 20,
        ...(options.minConfidence && { min_confidence: options.minConfidence })
      };
      
      const response = await this.client.get(`/headlines/${category}/${sentiment}`, { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Get statistics
  async getStats() {
    try {
      const response = await this.client.get('/stats');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }
  // Add these methods to your NewsAPI class

// Get live feed headlines
    async getLiveFeed(forceRefresh = false) {
    try {
        const params = forceRefresh ? { refresh: true } : {};
        const response = await this.client.get('/live-feed', { params });
        return response.data;
    } catch (error) {
        throw this.handleError(error);
    }
    }

    // Refresh live feed
    async refreshLiveFeed() {
    try {
        const response = await this.client.post('/live-feed/refresh');
        return response.data;
    } catch (error) {
        throw this.handleError(error);
    }
    }

    // Get live feed status
    async getLiveFeedStatus() {
    try {
        const response = await this.client.get('/live-feed/status');
        return response.data;
    } catch (error) {
        throw this.handleError(error);
    }
    }


  // Health check
  async healthCheck() {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Error handler
  handleError(error) {
    if (error.response) {
      // Server responded with error status
      return new Error(error.response.data.error || 'Server error');
    } else if (error.request) {
      // Network error
      return new Error('Network error - check your connection');
    } else {
      // Other error
      return new Error(error.message || 'Unknown error');
    }
  }
}

export default new NewsAPI();
