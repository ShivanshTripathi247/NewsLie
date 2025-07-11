import newsAPI from './api';
import LocalDatabase from './LocalDatabase';
import { AppState } from 'react-native';

class BackgroundSyncService {
  constructor() {
    this.syncInProgress = false;
    this.lastSyncCheck = null;
    this.setupAppStateListener();
  }

  setupAppStateListener() {
    AppState.addEventListener('change', (nextAppState) => {
      if (nextAppState === 'active') {
        // Check for updates when app becomes active
        this.checkForUpdatesIfNeeded();
      }
    });
  }

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

  async forceSync() {
    console.log('🔄 Force sync requested');
    this.lastSyncCheck = null;
    return await this.syncIfNeeded();
  }

  startAutoSync() {
    console.log('🚀 Starting auto-sync service');
    
    // Initial sync
    this.syncIfNeeded();
    
    // Check every 30 minutes
    setInterval(() => {
      this.checkForUpdatesIfNeeded();
    }, 30 * 60 * 1000);
  }

  getSyncStatus() {
    return {
      syncInProgress: this.syncInProgress,
      lastSyncCheck: this.lastSyncCheck
    };
  }
}

export default new BackgroundSyncService();
