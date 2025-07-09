import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { Ionicons } from '@expo/vector-icons';
import SentimentSelectionScreen from './screens/SentimentSelectionScreen';
import CategoryScreen from './screens/CategoryScreen';
import HeadlinesScreen from './screens/HeadlinesScreen';
import LiveFeedScreen from './screens/LiveFeedScreen';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// Stack Navigator for Sentiment Analysis Flow
function AnalysisStack() {
  return (
    <Stack.Navigator 
      screenOptions={{
        headerStyle: {
          backgroundColor: '#3498db',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <Stack.Screen 
        name="SentimentSelection" 
        component={SentimentSelectionScreen}
        options={{ 
          title: 'News Sentiment',
          headerShown: false 
        }}
      />
      <Stack.Screen 
        name="Categories" 
        component={CategoryScreen}
        options={{ 
          title: 'Categories',
          headerShown: false 
        }}
      />
      <Stack.Screen 
        name="Headlines" 
        component={HeadlinesScreen}
        options={{ 
          title: 'Headlines',
          headerShown: false 
        }}
      />
    </Stack.Navigator>
  );
}

// Main Tab Navigator
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
        options={{
          title: 'Live Feed',
          tabBarBadge: null, // Can be used for notifications later
        }}
      />
      <Tab.Screen 
        name="Analysis" 
        component={AnalysisStack}
        options={{
          title: 'Analysis',
        }}
      />
    </Tab.Navigator>
  );
}

export default function App() {
  return (
    <NavigationContainer>
      <MainTabs />
    </NavigationContainer>
  );
}
