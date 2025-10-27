import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import LoginScreen from './screens/LoginScreen';
import ProfileSetupScreen from './screens/ProfileSetupScreen';
import MainScreen from './screens/MainScreen';

const Stack = createStackNavigator();

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
        {/* 로그인 화면 */}
        <Stack.Screen 
          name="Login" 
          component={LoginScreen} 
          options={{ 
            headerShown: false 
          }}
        />
        
        {/* 추가 정보 입력 화면 */}
        <Stack.Screen 
          name="ProfileSetup" 
          component={ProfileSetupScreen}
          options={{ 
            title: '회원가입',
            headerLeft: null,
          }}
        />
        
        {/* 메인 화면 */}
        <Stack.Screen 
          name="Main" 
          component={MainScreen}
          options={{ 
            title: '길나비',
            headerLeft: null,
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

// 📂 최종 파일 구조
```
GilNabiApp/
├── App.js                      ← 네비게이션 관리
├── screens/
│   ├── LoginScreen.js          ← 로그인
│   ├── ProfileSetupScreen.js   ← 추가 정보 입력
│   └── MainScreen.js            ← 메인 (지도)
└── package.json
```