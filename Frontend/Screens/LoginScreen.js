import React, { useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Image,
} from 'react-native';
import { GoogleSignin } from '@react-native-google-signin/google-signin';
import { login, getProfile } from '@react-native-seoul/kakao-login';
import axios from 'axios';

export default function LoginScreen({ navigation }) {
  
  useEffect(() => {
    // 구글 로그인 설정
    GoogleSignin.configure({
      webClientId: '여기에_구글_웹_클라이언트_ID.apps.googleusercontent.com',
      offlineAccess: true,
    });
  }, []);

  // 구글 로그인
  const handleGoogleLogin = async () => {
    try {
      console.log('1. 구글 로그인 시작...');
      await GoogleSignin.hasPlayServices();
      const userInfo = await GoogleSignin.signIn();
      
      console.log('2. 토큰 수신:', userInfo.idToken?.substring(0, 20) + '...');
      const token = (await GoogleSignin.getTokens()).accessToken;

      console.log('3. Django 서버 호출...');
      const response = await axios.post('http://10.0.2.2:8000/users/social-login/', {
        provider: 'google',
        access_token: token,
      });

      console.log('4. 서버 응답:', response.data);
      
      // 프로필 완성 여부 확인
      if (response.data.is_profile_complete) {
        console.log('프로필 완성됨 → 메인 화면으로');
        navigation.replace('Main', { user: response.data });
      } else {
        console.log('프로필 미완성 → 추가 정보 입력');
        navigation.navigate('ProfileSetup', { userId: response.data.id });
      }

    } catch (error) {
      console.error('구글 로그인 실패:', error);
      Alert.alert('로그인 실패', error.message);
    }
  };

  // 카카오 로그인
  const handleKakaoLogin = async () => {
    try {
      console.log('=== 카카오 로그인 시작 ===');
      
      const token = await login();
      console.log('1. 토큰 받음:', token);

      const profile = await getProfile();
      console.log('2. 프로필 받음:', profile);

      console.log('3. Django 서버 호출...');
      const response = await axios.post(
        'http://10.0.2.2:8000/users/social-login/',
        {
          provider: 'kakao',
          access_token: token.accessToken,
        }
      );

      console.log('4. 서버 응답:', response.data);

      // 프로필 완성 여부 확인
      if (response.data.is_profile_complete) {
        console.log('프로필 완성됨 → 메인 화면으로');
        navigation.replace('Main', { user: response.data });
      } else {
        console.log('프로필 미완성 → 추가 정보 입력');
        navigation.navigate('ProfileSetup', { userId: response.data.id });
      }

    } catch (error) {
      console.error('카카오 로그인 에러:', error);
      
      if (error.code) {
        switch (error.code) {
          case 'E_CANCELLED_OPERATION':
            console.log('사용자가 로그인 취소');
            break;
          case 'E_NOT_INSTALLED':
            Alert.alert('알림', '카카오톡이 설치되어 있지 않습니다.');
            break;
          default:
            Alert.alert('로그인 실패', error.message);
        }
      } else {
        Alert.alert('로그인 실패', error.message);
      }
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>길나비</Text>
        <Text style={styles.subtitle}>장애인을 위한 편의 지도</Text>
      </View>

      <View style={styles.buttonContainer}>
        {/* 구글 로그인 버튼 */}
        <TouchableOpacity 
          style={[styles.button, styles.googleButton]} 
          onPress={handleGoogleLogin}
        >
          <Text style={styles.buttonText}>Google로 시작하기</Text>
        </TouchableOpacity>

        {/* 카카오 로그인 버튼 */}
        <TouchableOpacity 
          style={[styles.button, styles.kakaoButton]} 
          onPress={handleKakaoLogin}
        >
          <Text style={[styles.buttonText, styles.kakaoText]}>
            Kakao로 시작하기
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    justifyContent: 'center',
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 60,
  },
  title: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 18,
    color: '#666',
  },
  buttonContainer: {
    gap: 15,
  },
  button: {
    padding: 18,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  googleButton: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#ddd',
  },
  kakaoButton: {
    backgroundColor: '#FEE500',
  },
  buttonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  kakaoText: {
    color: '#000',
  },
});