import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime, timedelta

class GlobalDatabaseService:
    """Manages global PostgreSQL database for mobile sync"""
    
    def __init__(self):
        self.connection_string = os.getenv('DATABASE_URL')  # From Railway/Supabase
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                self.connection_string,
                cursor_factory=RealDictCursor
            )
            print("✅ Connected to global database")
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            raise
    
    def ensure_connection(self):
        """Ensure database connection is active"""
        if self.connection.closed:
            self.connect()
    
    def store_global_update(self, headlines_data):
        """Store complete news update from global crawl"""
        self.ensure_connection()
        cursor = self.connection.cursor()
        
        try:
            # Generate update ID
            update_id = f"global_{datetime.now().strftime('%Y%m%d_%H%M')}"
            
            # Create update record
            cursor.execute("""
                INSERT INTO news_updates (update_id, total_headlines)
                VALUES (%s, %s)
            """, (update_id, len(headlines_data)))
            
            # Store headlines in batch
            headline_records = []
            for headline in headlines_data:
                headline_records.append((
                    update_id,
                    headline['headline'],
                    headline['category'],
                    headline['sentiment'],
                    headline.get('confidence', 0),
                    headline.get('source_url', ''),
                    headline.get('image_url', '')
                ))
            
            cursor.executemany("""
                INSERT INTO headlines 
                (update_id, headline, category, sentiment, confidence, source_url, image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, headline_records)
            
            self.connection.commit()
            print(f"✅ Stored {len(headlines_data)} headlines with ID: {update_id}")
            return update_id
            
        except Exception as e:
            self.connection.rollback()
            print(f"❌ Error storing global update: {e}")
            raise
        finally:
            cursor.close()
    
    def get_latest_update_id(self):
        """Get the most recent update ID"""
        self.ensure_connection()
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                SELECT update_id FROM news_updates 
                ORDER BY created_at DESC LIMIT 1
            """)
            result = cursor.fetchone()
            return result['update_id'] if result else None
        finally:
            cursor.close()
    
    def get_bulk_data_for_sync(self, update_id):
        """Get all headlines for mobile app sync"""
        self.ensure_connection()
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                SELECT headline, category, sentiment, confidence, 
                       source_url, image_url, timestamp
                FROM headlines 
                WHERE update_id = %s
                ORDER BY category, sentiment, timestamp DESC
            """, (update_id,))
            
            headlines = []
            for row in cursor.fetchall():
                headlines.append({
                    'headline': row['headline'],
                    'category': row['category'],
                    'sentiment': row['sentiment'],
                    'confidence': float(row['confidence']) if row['confidence'] else 0,
                    'source_url': row['source_url'],
                    'image_url': row['image_url'],
                    'timestamp': row['timestamp'].isoformat()
                })
            
            return headlines
        finally:
            cursor.close()

# Global instance
global_db = GlobalDatabaseService()
