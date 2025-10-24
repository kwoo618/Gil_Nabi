import React, {useState} from 'react'
import {
  SafeAreaView,
  Text,
  Button,
  StyleSheet,
  View,
  Image,
  Alert,
  ActivityIndicator,
} from 'react-native'
import { login as kakaoLogin } from '@react-native-seoul/kakao-login'

export default function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(false)
  const API_BASE = 'http://10.0.2.2:8000'

  const handleKakaoLogin = async () => {
    setLoading(true)
    try {
      console.log('1. 카카오 로그인 시도...');
      const kakaoToken = await kakaoLogin()
      console.log('2. 카카오 토큰 수신 성공:', kakaoToken);

      const response = await fetch(`${API_BASE}/auth/social-login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: 'kakao',
          access_token: kakaoToken.accessToken,
        }),
      })
      console.log('3. 서버 응답 상태:', response.status);

      const data = await response.json()
      console.log('4. 서버로부터 받은 데이터:', data);

      if (response.ok) {
        setUser(data)
        Alert.alert('로그인 성공', `환영합니다, ${data.username}님!`)
      } else {
        throw new Error(data.error || `서버 오류: ${response.status}`)      
      }
    } catch (error) {
      console.error('❌ 최종 에러 발생:', error)
      Alert.alert('로그인 중 오류 발생', error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => { setUser(null) }

  if (loading) {
    return (
      <View style={styles.container}><ActivityIndicator size="large" /></View>
    )
  }

  return (
    <SafeAreaView style={styles.container}>
      {!user ? (
        <>
          <Text style={styles.title}>로그인 테스트</Text>
          <Button title="카카오로 로그인하기" onPress={handleKakaoLogin} color="#FEE500" />
        </>
      ) : (
        <>
          <Text style={styles.title}>로그인 성공!</Text>
          <Text>{user.username}님 환영합니다.</Text>
          <Button title="로그아웃" onPress={handleLogout} color="tomato" />
        </>
      )}
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  title: { fontSize: 24, marginBottom: 20 },
})