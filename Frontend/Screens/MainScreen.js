console.log('✅ MainScreen 로드됨');

import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';

export default function MainScreen({ route }) {
  const { user } = route.params || {};

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>🎉 회원가입 완료!</Text>
        
        {user && (
          <View style={styles.infoBox}>
            <Text style={styles.sectionTitle}>회원 정보</Text>
            
            <View style={styles.infoRow}>
              <Text style={styles.label}>아이디</Text>
              <Text style={styles.value}>{user.username}</Text>
            </View>

            <View style={styles.infoRow}>
              <Text style={styles.label}>닉네임</Text>
              <Text style={styles.value}>{user.nickname}</Text>
            </View>
            
            <View style={styles.infoRow}>
              <Text style={styles.label}>장애 종류</Text>
              <Text style={styles.value}>
                {user.disability_type === 'physical' && '지체장애'}
                {user.disability_type === 'visual' && '시각장애'}
                {user.disability_type === 'hearing' && '청각장애'}
                {user.disability_type === 'other' && '기타'}
              </Text>
            </View>
            
            <View style={styles.infoRow}>
              <Text style={styles.label}>휠체어 사용</Text>
              <Text style={styles.value}>
                {user.has_wheelchair ? '사용함 ♿' : '사용 안 함'}
              </Text>
            </View>
          </View>
        )}

        <View style={styles.mapPlaceholder}>
          <Text style={styles.mapText}>🗺️</Text>
          <Text style={styles.mapSubtext}>
            여기에 지도가 표시될 예정입니다
          </Text>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    padding: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#007AFF',
  },
  infoBox: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  label: {
    fontSize: 16,
    color: '#666',
  },
  value: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  mapPlaceholder: {
    backgroundColor: '#fff',
    padding: 60,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  mapText: {
    fontSize: 64,
    marginBottom: 10,
  },
  mapSubtext: {
    fontSize: 16,
    color: '#999',
    textAlign: 'center',
  },
});