import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';  // ← 이 줄 확인!
import LoginScreen from './Screens/LoginScreen';
import ProfileSetupScreen from './Screens/ProfileSetupScreen';
import MainScreen from './Screens/MainScreen';

const Stack = createNativeStackNavigator();  // ← 이 줄 확인!

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator 
        initialRouteName="Login"
        screenOptions={{
          headerStyle: {
            backgroundColor: '#007AFF',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        <Stack.Screen 
          name="Login" 
          component={LoginScreen} 
          options={{ headerShown: false }}
        />
        
        <Stack.Screen 
          name="ProfileSetup" 
          component={ProfileSetupScreen}
          options={{ 
            title: '회원가입',
            headerLeft: () => null,
          }}
        />
        
        <Stack.Screen 
          name="Main" 
          component={MainScreen}
          options={{ 
            title: '길나비',
            headerLeft: () => null,
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}