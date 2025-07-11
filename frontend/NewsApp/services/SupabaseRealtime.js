// services/SupabaseRealtime.js
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.EXPO_SUPABASE_URL
const supabaseAnonKey = process.env.EXPO_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

class SupabaseRealtimeService {
  constructor() {
    this.subscription = null;
  }

  subscribeToUpdates(callback) {
    this.subscription = supabase
      .channel('headlines-updates')
      .on('postgres_changes', 
        { event: 'INSERT', schema: 'public', table: 'news_updates' },
        (payload) => {
          console.log('🔔 New update available:', payload.new);
          callback(payload.new);
        }
      )
      .subscribe();
  }

  unsubscribe() {
    if (this.subscription) {
      supabase.removeChannel(this.subscription);
    }
  }
}

export default new SupabaseRealtimeService();
