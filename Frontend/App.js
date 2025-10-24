import React, { useState } from 'react';
import {
  SafeAreaView,
  Text,
  Button,
  StyleSheet,
  Alert,
  View,
  ActivityIndicator,
} from 'react-native';
import { login as kakaoLogin } from '@react-native-seoul/kakao-login';

export default function App() {
  const [user, setUser] = useState(null); 
  const [loading, setLoading] = useState(false);
  const API_BASE = 'http://10.0.2.2:8000'; // Android Emulator
  
  const handleKakaoLogin = async () => {
    setLoading(true);
    try {
      console.log('1. 카카오 로그인 시작...');
      const kakaoToken = await kakaoLogin();
      console.log('2. 토큰 수신:', kakaoToken.accessToken.substring(0, 20) + '...');

      console.log('3. Django 서버 호출...');
      const response = await fetch(`${API_BASE}/users/auth/social-login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: 'kakao',
          access_token: kakaoToken.accessToken,
        }),
      });

      const data = await response.json();
      console.log('4. 서버 응답:', data);

      if (response.ok) {
        setUser(data);
        Alert.alert('로그인 성공', `환영합니다, ${data.username}님!`);
      } else {
        throw new Error(data.error || '서버 오류');
      }
    } catch (error) {
      console.error('❌ 에러:', error);
      Alert.alert('로그인 실패', error.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#FEE500" />
        <Text style={styles.loadingText}>로그인 중...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>길나비 앱</Text>
      {!user ? (
        <Button 
          title="🍋 카카오 로그인" 
          onPress={handleKakaoLogin} 
          color="#FEE500" 
        />
      ) : (
        <View style={styles.userInfo}>
          <Text style={styles.welcome}>{user.username}님 환영합니다!</Text>
          <Text>제공자: {user.provider}</Text>
          <Text>ID: {user.social_id}</Text>
          <Button 
            title="로그아웃" 
            onPress={() => setUser(null)} 
            color="tomato" 
          />
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 30,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  userInfo: {
    padding: 20,
    backgroundColor: 'white',
    borderRadius: 10,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  welcome: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10,
  },
});