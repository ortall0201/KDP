/**
 * AI Ghostwriter Mobile App
 *
 * Main entry point with navigation
 */

import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar } from 'expo-status-bar';

// Screens
import HomeScreen from './src/screens/HomeScreen';
import ProcessingScreen from './src/screens/ProcessingScreen';
import CompletedScreen from './src/screens/CompletedScreen';
import SettingsScreen from './src/screens/SettingsScreen';

const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerStyle: {
            backgroundColor: '#6366f1',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        <Stack.Screen
          name="Home"
          component={HomeScreen}
          options={{ title: 'AI Ghostwriter' }}
        />
        <Stack.Screen
          name="Processing"
          component={ProcessingScreen}
          options={{ title: 'Processing Manuscript' }}
        />
        <Stack.Screen
          name="Completed"
          component={CompletedScreen}
          options={{ title: 'Completed' }}
        />
        <Stack.Screen
          name="Settings"
          component={SettingsScreen}
          options={{ title: 'API Keys Settings' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
