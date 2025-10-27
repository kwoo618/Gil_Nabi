console.log('✅ ProfileSetupScreen 로드됨');

import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import axios from 'axios';

export default function ProfileSetupScreen({ route, navigation }) {
  const { userId } = route.params;
  
  const [nickname, setNickname] = useState('');
  const [disabilityType, setDisabilityType] = useState('');
  const [hasWheelchair, setHasWheelchair] = useState(null);

  const disabilityOptions = [
    { value: 'physical', label: '지체장애' },
    { value: 'visual', label: '시각장애' },
    { value: 'hearing', label: '청각장애' },
    { value: 'other', label: '기타' },
  ];

  const handleSubmit = async () => {
    // 유효성 검사
    if (!nickname.trim()) {
      Alert.alert('알림', '닉네임을 입력해주세요.');
      return;
    }
    
    if (nickname.trim().length < 2) {
      Alert.alert('알림', '닉네임은 2글자 이상이어야 합니다.');
      return;
    }

    if (!disabilityType) {
      Alert.alert('알림', '장애 종류를 선택해주세요.');
      return;
    }

    if (hasWheelchair === null) {
      Alert.alert('알림', '휠체어 사용 여부를 선택해주세요.');
      return;
    }

    try {
      console.log('프로필 완성 요청:', {
        user_id: userId,
        nickname: nickname.trim(),
        disability_type: disabilityType,
        has_wheelchair: hasWheelchair,
      });

      const response = await axios.post(
        'http://10.0.2.2:8000/users/complete-profile/',
        {
          user_id: userId,
          nickname: nickname.trim(),
          disability_type: disabilityType,
          has_wheelchair: hasWheelchair,
        }
      );

      console.log('프로필 완성 성공:', response.data);
      
      Alert.alert('환영합니다!', '회원가입이 완료되었습니다.', [
        {
          text: '확인',
          onPress: () => {
            navigation.replace('Main', { user: response.data.user });
          }
        }
      ]);
      
    } catch (error) {
      console.error('프로필 완성 실패:', error.response?.data || error.message);
      Alert.alert(
        '오류', 
        error.response?.data?.error || '정보 저장에 실패했습니다.'
      );
    }
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView 
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        <Text style={styles.title}>추가 정보 입력</Text>
        <Text style={styles.subtitle}>
          길나비 앱 이용을 위해{'\n'}몇 가지 정보를 입력해주세요
        </Text>

        {/* 닉네임 입력 */}
        <View style={styles.section}>
          <Text style={styles.label}>닉네임 *</Text>
          <TextInput
            style={styles.input}
            placeholder="2글자 이상 입력해주세요"
            value={nickname}
            onChangeText={setNickname}
            maxLength={20}
            autoCapitalize="none"
          />
          <Text style={styles.charCount}>{nickname.length}/20</Text>
        </View>

        {/* 장애 종류 선택 */}
        <View style={styles.section}>
          <Text style={styles.label}>장애 종류 *</Text>
          <View style={styles.buttonGroup}>
            {disabilityOptions.map((option) => (
              <TouchableOpacity
                key={option.value}
                style={[
                  styles.optionButton,
                  disabilityType === option.value && styles.selectedButton
                ]}
                onPress={() => setDisabilityType(option.value)}
              >
                <Text style={[
                  styles.optionText,
                  disabilityType === option.value && styles.selectedText
                ]}>
                  {option.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* 휠체어 사용 여부 */}
        <View style={styles.section}>
          <Text style={styles.label}>휠체어 사용 *</Text>
          <View style={styles.buttonGroup}>
            <TouchableOpacity
              style={[
                styles.wheelchairButton,
                hasWheelchair === true && styles.selectedButton
              ]}
              onPress={() => setHasWheelchair(true)}
            >
              <Text style={[
                styles.optionText,
                hasWheelchair === true && styles.selectedText
              ]}>
                사용함
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.wheelchairButton,
                hasWheelchair === false && styles.selectedButton
              ]}
              onPress={() => setHasWheelchair(false)}
            >
              <Text style={[
                styles.optionText,
                hasWheelchair === false && styles.selectedText
              ]}>
                사용 안 함
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* 완료 버튼 */}
        <TouchableOpacity 
          style={styles.submitButton} 
          onPress={handleSubmit}
          activeOpacity={0.8}
        >
          <Text style={styles.submitButtonText}>완료</Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  scrollContent: {
    padding: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginTop: 20,
    marginBottom: 8,
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 32,
    lineHeight: 24,
  },
  section: {
    marginBottom: 32,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
    color: '#333',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    backgroundColor: '#f9f9f9',
  },
  charCount: {
    fontSize: 12,
    color: '#999',
    textAlign: 'right',
    marginTop: 4,
  },
  buttonGroup: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  optionButton: {
    flex: 1,
    minWidth: '47%',
    padding: 16,
    borderWidth: 2,
    borderColor: '#ddd',
    borderRadius: 12,
    alignItems: 'center',
    backgroundColor: '#f9f9f9',
  },
  wheelchairButton: {
    flex: 1,
    padding: 16,
    borderWidth: 2,
    borderColor: '#ddd',
    borderRadius: 12,
    alignItems: 'center',
    backgroundColor: '#f9f9f9',
  },
  selectedButton: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
  },
  optionText: {
    fontSize: 16,
    color: '#333',
    fontWeight: '500',
  },
  selectedText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  submitButton: {
    backgroundColor: '#007AFF',
    padding: 18,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 40,
    shadowColor: '#007AFF',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});