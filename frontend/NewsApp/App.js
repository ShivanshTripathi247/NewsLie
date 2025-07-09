import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import SentimentSelectionScreen from './screens/SentimentSelectionScreen';
import CategoryScreen from './screens/CategoryScreen';
import HeadlinesScreen from './screens/HeadlinesScreen';

const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator 
        initialRouteName="SentimentSelection"
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
    </NavigationContainer>
  );
}
