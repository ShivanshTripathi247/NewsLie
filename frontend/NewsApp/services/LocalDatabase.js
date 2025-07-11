import SQLite from 'react-native-sqlite-storage';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Enable debugging (remove in production)
SQLite.DEBUG(true);
SQLite.enablePromise(true);

class LocalDatabase {
  constructor() {
    this.db = null;
    this.isAvailable = false;
    this.initDatabase();
  }


  async initDatabase() {
    try {
      this.db = await SQLite.openDatabase({
        name: 'NewsLocal.db',
        location: 'default',
      });

      await this.createTables();
      this.isAvailable = true;
      console.log('✅ Local SQLite database initialized');
    } catch (error) {
      console.error('❌ Database initialization error:', error);
      this.isAvailable = false;
    }
  }


  async createTables() {
    const createHeadlinesTable = `
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
    `;

    const createSyncTable = `
      CREATE TABLE IF NOT EXISTS sync_metadata (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );
    `;

    const createIndexes = `
      CREATE INDEX IF NOT EXISTS idx_category_sentiment 
      ON local_headlines(category, sentiment);
      
      CREATE INDEX IF NOT EXISTS idx_timestamp 
      ON local_headlines(timestamp DESC);
    `;

    try {
      await this.db.executeSql(createHeadlinesTable);
      await this.db.executeSql(createSyncTable);
      await this.db.executeSql(createIndexes);
      console.log('✅ Database tables created');
    } catch (error) {
      console.error('❌ Table creation error:', error);
    }
  }

  async replaceAllData(headlines, updateId) {
    try {
      await this.db.transaction(async (tx) => {
        // Clear existing data
        await tx.executeSql('DELETE FROM local_headlines');
        console.log('🗑️ Cleared old headlines');

        // Insert new headlines in batches
        const batchSize = 50;
        let insertedCount = 0;

        for (let i = 0; i < headlines.length; i += batchSize) {
          const batch = headlines.slice(i, i + batchSize);
          
          for (const headline of batch) {
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
            insertedCount++;
          }
        }

        // Update sync metadata
        await tx.executeSql(
          'INSERT OR REPLACE INTO sync_metadata (key, value) VALUES (?, ?)',
          ['last_update_id', updateId]
        );

        await tx.executeSql(
          'INSERT OR REPLACE INTO sync_metadata (key, value) VALUES (?, ?)',
          ['last_sync_time', new Date().toISOString()]
        );

        console.log(`✅ Inserted ${insertedCount} headlines locally`);
      });

      // Store in AsyncStorage for quick access
      await AsyncStorage.setItem('lastUpdateId', updateId);
      await AsyncStorage.setItem('lastSyncTime', new Date().toISOString());
      
      return true;
    } catch (error) {
      console.error('❌ Error replacing local data:', error);
      return false;
    }
  }

  async getHeadlines(category, sentiment, limit = 20) {
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

      console.log(`📱 Retrieved ${headlines.length} local headlines for ${category}/${sentiment}`);
      return headlines;
    } catch (error) {
      console.error('❌ Error getting headlines:', error);
      return [];
    }
  }

  async getLiveFeedHeadlines(limit = 30) {
    try {
      const [results] = await this.db.executeSql(
        `SELECT * FROM local_headlines 
         ORDER BY timestamp DESC LIMIT ?`,
        [limit]
      );

      const headlines = [];
      for (let i = 0; i < results.rows.length; i++) {
        headlines.push(results.rows.item(i));
      }

      console.log(`📱 Retrieved ${headlines.length} headlines for live feed`);
      return headlines;
    } catch (error) {
      console.error('❌ Error getting live feed headlines:', error);
      return [];
    }
  }

  async getLastUpdateId() {
    if (!this.isAvailable || !this.db) {
    console.log('📱 Database not available, returning null');
    return null;
    }
    try {
      // Try AsyncStorage first (faster)
      const asyncStorageId = await AsyncStorage.getItem('lastUpdateId');
      if (asyncStorageId) {
        return asyncStorageId;
      }

      // Fallback to database
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

  async getDataStats() {
    try {
      const [results] = await this.db.executeSql(
        'SELECT COUNT(*) as total, MAX(timestamp) as latest FROM local_headlines'
      );
      
      const stats = results.rows.item(0);
      const lastUpdateId = await this.getLastUpdateId();

      return {
        totalHeadlines: stats.total,
        latestTimestamp: stats.latest,
        lastUpdateId: lastUpdateId,
        hasData: stats.total > 0
      };
    } catch (error) {
      console.error('❌ Error getting data stats:', error);
      return { totalHeadlines: 0, latestTimestamp: null, lastUpdateId: null, hasData: false };
    }
  }

  async clearAllData() {
    try {
      await this.db.executeSql('DELETE FROM local_headlines');
      await this.db.executeSql('DELETE FROM sync_metadata');
      await AsyncStorage.removeItem('lastUpdateId');
      await AsyncStorage.removeItem('lastSyncTime');
      console.log('🗑️ All local data cleared');
    } catch (error) {
      console.error('❌ Error clearing data:', error);
    }
  }
}

export default new LocalDatabase();
