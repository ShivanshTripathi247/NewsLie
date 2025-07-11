import time
from supabase import create_client, Client
import os
from datetime import datetime

class SupabaseService:
    """Enhanced Supabase client with transaction error handling"""
    
    def __init__(self):
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase: Client = create_client(url, key)
        self.max_retries = 3
    
    def store_global_update(self, headlines_data):
        """Store news update with robust error handling and retry logic"""
        for attempt in range(self.max_retries):
            try:
                update_id = f"global_{datetime.now().strftime('%Y%m%d_%H%M')}"
                
                # Check if update already exists to prevent duplicates
                existing = self.supabase.table('news_updates')\
                    .select('update_id')\
                    .eq('update_id', update_id)\
                    .execute()
                
                if existing.data:
                    print(f"⚠️ Update {update_id} already exists, skipping...")
                    return update_id
                
                # Insert update record first
                update_result = self.supabase.table('news_updates').insert({
                    'update_id': update_id,
                    'total_headlines': len(headlines_data),
                    'status': 'processing'
                }).execute()
                
                if not update_result.data:
                    raise Exception("Failed to create update record")
                
                # Batch insert headlines in smaller chunks to avoid transaction timeouts
                batch_size = 50
                total_inserted = 0
                
                for i in range(0, len(headlines_data), batch_size):
                    batch = headlines_data[i:i + batch_size]
                    headline_records = []
                    
                    for headline in batch:
                        headline_records.append({
                            'update_id': update_id,
                            'headline': headline['headline'],
                            'category': headline['category'],
                            'sentiment': headline['sentiment'],
                            'confidence': headline.get('confidence', 0),
                            'source_url': headline.get('source_url', ''),
                            'image_url': headline.get('image_url', '')
                        })
                    
                    # Insert batch with retry logic
                    batch_result = self.supabase.table('headlines').insert(headline_records).execute()
                    
                    if batch_result.data:
                        total_inserted += len(batch_result.data)
                        print(f"✅ Inserted batch {i//batch_size + 1}: {len(batch_result.data)} headlines")
                    else:
                        raise Exception(f"Failed to insert batch {i//batch_size + 1}")
                
                # Update status to completed
                self.supabase.table('news_updates')\
                    .update({'status': 'completed', 'total_headlines': total_inserted})\
                    .eq('update_id', update_id)\
                    .execute()
                
                print(f"✅ Successfully stored {total_inserted} headlines with ID: {update_id}")
                return update_id
                
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    print(f"🔄 Retrying in {2 ** attempt} seconds...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    print(f"❌ All {self.max_retries} attempts failed")
                    raise e
    
    def get_latest_update_id(self):
        """Get most recent update ID with error handling"""
        try:
            result = self.supabase.table('news_updates')\
                .select('update_id')\
                .eq('status', 'completed')\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            
            return result.data[0]['update_id'] if result.data else None
        except Exception as e:
            print(f"❌ Error getting latest update: {e}")
            return None
    
    def get_bulk_data_for_sync(self, update_id):
        """Get headlines for mobile sync with enhanced debugging"""
        try:
            print(f"🔍 Querying Supabase for update_id: {update_id}")
            
            # First, verify the update exists
            update_check = self.supabase.table('news_updates')\
                .select('update_id, total_headlines')\
                .eq('update_id', update_id)\
                .execute()
            
            if not update_check.data:
                print(f"❌ Update record not found: {update_id}")
                return []
            
            print(f"✅ Update record found: {update_check.data[0]}")
            
            # Query headlines
            result = self.supabase.table('headlines')\
                .select('headline, category, sentiment, confidence, source_url, image_url, created_at')\
                .eq('update_id', update_id)\
                .order('created_at', desc=True)\
                .execute()
            
            print(f"📊 Raw query result: {len(result.data) if result.data else 0} headlines")
            
            if not result.data:
                print(f"⚠️ No headlines found in database for update_id: {update_id}")
                
                # Debug: Check if headlines exist with any update_id
                all_headlines = self.supabase.table('headlines')\
                    .select('update_id')\
                    .limit(5)\
                    .execute()
                
                print(f"🔍 Sample update_ids in database: {[h.get('update_id') for h in all_headlines.data] if all_headlines.data else 'None'}")
                return []
            
            # Format data for mobile compatibility
            formatted_headlines = []
            for row in result.data:
                formatted_headlines.append({
                    'headline': row.get('headline', ''),
                    'category': row.get('category', ''),
                    'sentiment': row.get('sentiment', 'neutral'),
                    'confidence': float(row.get('confidence', 0)),
                    'source_url': row.get('source_url', ''),
                    'image_url': row.get('image_url', ''),
                    'timestamp': row.get('created_at', datetime.now().isoformat())
                })
            
            print(f"✅ Formatted {len(formatted_headlines)} headlines for mobile")
            return formatted_headlines
            
        except Exception as e:
            print(f"❌ Error getting bulk data: {e}")
            return []

# Global instance
supabase_db = SupabaseService()
