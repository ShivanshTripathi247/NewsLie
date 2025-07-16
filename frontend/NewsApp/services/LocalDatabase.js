import SQLite from 'react-native-sqlite-storage';
import AsyncStorage from '@react-native-async-storage/async-storage';

SQLite.DEBUG(false);
SQLite.enablePromise(true);

class LocalDatabase {
  constructor() {
    this.db = null;
    this.isAvailable = false;
    this.initDatabase();
  }

  async initDatabase() {
    try {
      // Simplified database configuration
      this.db = await SQLite.openDatabase({
        name: 'NewsLocal.db',
        location: 'default',
      });

      if (this.db) {
        await this.createTables();
        this.isAvailable = true;
        console.log('✅ Local SQLite database initialized');
      } else {
        throw new Error('Database connection failed');
      }
    } catch (error) {
      console.error('❌ Database initialization error:', error);
      this.isAvailable = false;
    }
  }

  async createTables() {
    if (!this.db) return;

    try {
      await this.db.transaction(async (tx) => {
        await tx.executeSql(`
          CREATE TABLE IF NOT EXISTS local_headlines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            headline TEXT NOT NULL,
            category TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            confidence REAL DEFAULT 0,
            source_url TEXT,
            image_url TEXT,
            timestamp TEXT,
            update_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
          );
        `);

        await tx.executeSql(`
          CREATE TABLE IF NOT EXISTS sync_metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
          );
        `);
      });

      console.log('✅ Database tables created successfully');
    } catch (error) {
      console.error('❌ Table creation error:', error);
      this.isAvailable = false;
    }
  }

  async getLastUpdateId() {
    if (!this.isAvailable || !this.db) {
      return null;
    }

    try {
      const asyncStorageId = await AsyncStorage.getItem('lastUpdateId');
      if (asyncStorageId) return asyncStorageId;

      const [results] = await this.db.executeSql(
        'SELECT value FROM sync_metadata WHERE key = ?',
        ['last_update_id']
      );

      return results.rows.length > 0 ? results.rows.item(0).value : null;
    } catch (error) {
      console.error('❌ Error getting last update ID:', error);
      return null;
    }
  }

  async replaceAllData(headlines, updateId) {
    if (!this.isAvailable || !this.db) {
      console.log('📱 Database not available for data replacement');
      return false;
    }

    try {
      await this.db.transaction(async (tx) => {
        // Clear existing data
        await tx.executeSql('DELETE FROM local_headlines');
        console.log('🗑️ Cleared old headlines');

        // Insert new headlines
        for (const headline of headlines) {
          await tx.executeSql(
            `INSERT INTO local_headlines 
             (headline, category, sentiment, confidence, source_url, image_url, timestamp, update_id) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
            [
              headline.headline,
              headline.category,
              headline.sentiment,
              headline.confidence || 0,
              headline.source_url || '',
              headline.image_url || '',
              headline.timestamp,
              updateId
            ]
          );
        }

        // Update sync metadata
        await tx.executeSql(
          'INSERT OR REPLACE INTO sync_metadata (key, value) VALUES (?, ?)',
          ['last_update_id', updateId]
        );
      });

      // Store in AsyncStorage for quick access
      await AsyncStorage.setItem('lastUpdateId', updateId);
      
      console.log(`✅ Successfully stored ${headlines.length} headlines locally`);
      return true;
    } catch (error) {
      console.error('❌ Error replacing local data:', error);
      return false;
    }
  }

  async getHeadlines(category, sentiment, limit = 20) {
    if (!this.isAvailable || !this.db) {
      return [];
    }

    try {
      const [results] = await this.db.executeSql(
        `SELECT * FROM local_headlines 
         WHERE category = ? AND sentiment = ? 
         ORDER BY timestamp DESC LIMIT ?`,
        [category, sentiment, limit]
      );

      const headlines = [];
      for (let i = 0; i < results.rows.length; i++) {
        headlines.push(results.rows.item(i));
      }

      return headlines;
    } catch (error) {
      console.error('❌ Error getting headlines:', error);
      return [];
    }
  }

  // Save live feed headlines to local storage
  async saveLiveFeedHeadlines(headlines) {
    try {
      await AsyncStorage.setItem('livefeedheadlines', JSON.stringify(headlines));
      console.log(`✅ Saved ${headlines.length} live feed headlines to local storage`);
      return true;
    } catch (error) {
      console.error('❌ Failed to save live feed headlines:', error);
      return false;
    }
  }

  // Get live feed headlines from local storage
  async getLiveFeedHeadlines(limit = 30) {
    try {
      const stored = await AsyncStorage.getItem('livefeedheadlines');
      if (stored) {
        const headlines = JSON.parse(stored);
        console.log(`📱 Retrieved ${headlines.length} live feed headlines from local storage`);
        return headlines.slice(0, limit);
      } else {
        console.log('📱 No live feed headlines found in local storage');
        return [];
      }
    } catch (error) {
      console.error('❌ Error retrieving live feed headlines:', error);
      return [];
    }
  }
}

export default new LocalDatabase();
