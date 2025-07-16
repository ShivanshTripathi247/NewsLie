import newsAPI from './api';
import LocalDatabase from './LocalDatabase';
import { AppState } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

class BackgroundSyncService {
  constructor() {
    this.syncInProgress = false;
    this.lastSyncCheck = null;
    this.lastLiveFeedSync = null;
    this.setupAppStateListener();
  }

  setupAppStateListener() {
    AppState.addEventListener('change', (nextAppState) => {
      if (nextAppState === 'active') {
        // Check for updates when app becomes active
        this.checkForUpdatesIfNeeded();
        this.syncLiveFeedIfNeeded();
      }
    });
  }

  // 12-hour headlines sync
  async checkForUpdatesIfNeeded() {
    const now = Date.now();
    const fiveMinutes = 5 * 60 * 1000;

    // Avoid too frequent checks
    if (this.lastSyncCheck && (now - this.lastSyncCheck) < fiveMinutes) {
      console.log('⏰ Skipping sync check - too recent');
      return false;
    }

    this.lastSyncCheck = now;
    return await this.syncIfNeeded();
  }

  async syncIfNeeded() {
    if (this.syncInProgress) {
      console.log('🔄 Sync already in progress');
      return false;
    }

    try {
      this.syncInProgress = true;
      console.log('🔍 Checking for updates...');

      // Get current local update ID
      const localUpdateId = await LocalDatabase.getLastUpdateId();
      console.log(`📱 Local update ID: ${localUpdateId}`);
      
      // Check server for latest update
      const serverResponse = await newsAPI.checkForUpdates(localUpdateId || 'none');
      console.log(`🌐 Server response:`, serverResponse);
      
      if (serverResponse.hasUpdate) {
        console.log('📥 New data available, downloading...');
        
        // Download bulk update
        const bulkData = await newsAPI.getBulkUpdate(serverResponse.latestUpdateId);
        console.log(`📦 Downloaded ${bulkData.headlines?.length || 0} headlines`);
        
        // Replace local data
        const success = await LocalDatabase.replaceAllData(
          bulkData.headlines || [], 
          serverResponse.latestUpdateId
        );
        
        if (success) {
          console.log('✅ Auto-sync completed successfully');
          return true;
        } else {
          console.log('❌ Auto-sync failed during data replacement');
          return false;
        }
      } else {
        console.log('✅ Data is up to date');
        return false;
      }
    } catch (error) {
      console.error('❌ Auto-sync error:', error);
      return false;
    } finally {
      this.syncInProgress = false;
    }
  }

  // Live feed sync (hourly)
  async syncLiveFeedIfNeeded() {
    const now = Date.now();
    const oneHour = 60 * 60 * 1000;

    if (this.lastLiveFeedSync && (now - this.lastLiveFeedSync) < oneHour) {
      console.log('⏰ Skipping live feed sync - too recent');
      return false;
    }

    this.lastLiveFeedSync = now;
    return await this.syncLiveFeed();
  }

  async syncLiveFeed() {
    try {
      console.log('🔄 Syncing live feed...');
      const response = await newsAPI.getLiveFeed(true);
      if (response && response.headlines) {
        await AsyncStorage.setItem('livefeedheadlines', JSON.stringify(response.headlines));
        console.log(`✅ Stored ${response.headlines.length} live feed headlines`);
        return true;
      } else {
        console.log('❌ No live feed headlines received');
        return false;
      }
    } catch (error) {
      console.error('❌ Live feed sync error:', error);
      return false;
    }
  }

  async forceSync() {
    console.log('🔄 Force sync requested');
    this.lastSyncCheck = null;
    this.lastLiveFeedSync = null;
    await this.syncIfNeeded();
    await this.syncLiveFeed();
  }

  startAutoSync() {
    console.log('🚀 Starting auto-sync service');
    this.syncIfNeeded();
    this.syncLiveFeed();
    
    // Headlines sync every 30 min, live feed every hour
    setInterval(() => {
      this.checkForUpdatesIfNeeded();
    }, 30 * 60 * 1000);
    setInterval(() => {
      this.syncLiveFeedIfNeeded();
    }, 60 * 60 * 1000);
  }

  getSyncStatus() {
    return {
      syncInProgress: this.syncInProgress,
      lastSyncCheck: this.lastSyncCheck,
      lastLiveFeedSync: this.lastLiveFeedSync
    };
  }
}

export default new BackgroundSyncService();
