import React, { useEffect, useState } from 'react';
import { View, Text, Alert } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { Ionicons } from '@expo/vector-icons';
import SentimentSelectionScreen from './screens/SentimentSelectionScreen';
import CategoryScreen from './screens/CategoryScreen';
import HeadlinesScreen from './screens/HeadlinesScreen';
import LiveFeedScreen from './screens/LiveFeedScreen';
import FactCheckerScreen from './screens/FactCheckerScreen'; // NEW
import BackgroundSync from './services/BackgroundSync';
import LocalDatabase from './services/LocalDatabase';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// Stack Navigator for Sentiment Analysis Flow
function AnalysisStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="SentimentSelection" component={SentimentSelectionScreen} />
      <Stack.Screen name="Categories" component={CategoryScreen} />
      <Stack.Screen name="Headlines" component={HeadlinesScreen} />
    </Stack.Navigator>
  );
}

// Main Tab Navigator with Fact Checker
function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'LiveFeed') {
            iconName = focused ? 'newspaper' : 'newspaper-outline';
          } else if (route.name === 'Analysis') {
            iconName = focused ? 'analytics' : 'analytics-outline';
          } else if (route.name === 'FactChecker') {
            iconName = focused ? 'shield-checkmark' : 'shield-checkmark-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#3498db',
        tabBarInactiveTintColor: '#95a5a6',
        tabBarStyle: {
          backgroundColor: 'white',
          borderTopWidth: 1,
          borderTopColor: '#ecf0f1',
          height: 60,
          paddingBottom: 8,
          paddingTop: 8,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '600',
        },
        headerShown: false,
      })}
    >
      <Tab.Screen 
        name="LiveFeed" 
        component={LiveFeedScreen}
        options={{ title: 'Live Feed' }}
      />
      <Tab.Screen 
        name="Analysis" 
        component={AnalysisStack}
        options={{ title: 'Analysis' }}
      />
      <Tab.Screen 
        name="FactChecker" 
        component={FactCheckerScreen}
        options={{ title: 'Fact Check' }}
      />
    </Tab.Navigator>
  );
}

export default function App() {
  const [isInitialized, setIsInitialized] = useState(false);
  const [initError, setInitError] = useState(null);

  useEffect(() => {
    const initializeApp = async () => {
      try {
        console.log('🚀 Starting app initialization...');
        
        // Initialize database first
        await LocalDatabase.initDatabase();
        console.log('✅ Database initialized');
        
        // Start background sync
        BackgroundSync.startAutoSync();
        console.log('✅ Background sync started');
        
        setIsInitialized(true);
        console.log('🎉 App initialization completed');
      } catch (error) {
        console.error('❌ App initialization error:', error);
        setInitError(error.message);
        
        // Show user-friendly error
        Alert.alert(
          'Initialization Error',
          'The app failed to initialize properly. Some features may not work.',
          [{ text: 'OK' }]
        );
      }
    };

    initializeApp();
  }, []);

  return (
    <NavigationContainer>
      <MainTabs />
    </NavigationContainer>
  );
}

