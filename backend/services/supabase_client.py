# services/supabase_client.py
from supabase import create_client, Client
import os
from datetime import datetime

class SupabaseService:
    """Supabase client for global database operations"""
    
    def __init__(self):
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase: Client = create_client(url, key)
    
    def store_global_update(self, headlines_data):
        """Store news update using Supabase"""
        try:
            update_id = f"global_{datetime.now().strftime('%Y%m%d_%H%M')}"
            
            # Insert update record
            update_result = self.supabase.table('news_updates').insert({
                'update_id': update_id,
                'total_headlines': len(headlines_data)
            }).execute()
            
            # Prepare headlines for batch insert
            headline_records = []
            for headline in headlines_data:
                headline_records.append({
                    'update_id': update_id,
                    'headline': headline['headline'],
                    'category': headline['category'],
                    'sentiment': headline['sentiment'],
                    'confidence': headline.get('confidence', 0),
                    'source_url': headline.get('source_url', ''),
                    'image_url': headline.get('image_url', '')
                })
            
            # Batch insert headlines
            headlines_result = self.supabase.table('headlines').insert(headline_records).execute()
            
            print(f"✅ Stored {len(headlines_data)} headlines in Supabase")
            return update_id
            
        except Exception as e:
            print(f"❌ Supabase storage error: {e}")
            raise
    
    def get_latest_update_id(self):
        """Get most recent update ID"""
        try:
            result = self.supabase.table('news_updates')\
                .select('update_id')\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            
            return result.data[0]['update_id'] if result.data else None
        except Exception as e:
            print(f"❌ Error getting latest update: {e}")
            return None
    
    def get_bulk_data_for_sync(self, update_id):
        """Get headlines for mobile sync"""
        try:
            result = self.supabase.table('headlines')\
                .select('*')\
                .eq('update_id', update_id)\
                .order('created_at', desc=True)\
                .execute()
            
            return result.data
        except Exception as e:
            print(f"❌ Error getting bulk data: {e}")
            return []

# Global instance
supabase_db = SupabaseService()
