import os
import json
import anthropic
from django.conf import settings

class ClaudeClient:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv('CLAUDE_API_KEY')
        )
    
    def test_connection(self):
        """API 연결 테스트"""
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                messages=[{"role": "user", "content": "Hello, respond with 'Connection successful' if you can read this."}]
            )
            return True, response.content[0].text
        except Exception as e:
            return False, str(e)
    
    def analyze_review_sentiment(self, review_text):
        """리뷰의 전체적인 감성 점수 분석"""
        prompt = f"""
        다음 장소 리뷰를 분석해서 전체적인 만족도 점수를 매겨주세요.
        
        리뷰: "{review_text}"
        
        다음 JSON 형식으로만 답변하세요:
        {{
            "sentiment_score": 0-100 사이의 숫자,
            "sentiment": "positive" 또는 "negative" 또는 "neutral",
            "key_points": ["주요 포인트 1", "주요 포인트 2"]
        }}
        
        점수 기준:
        - 0-30: 매우 부정적
        - 31-50: 부정적
        - 51-70: 중립/보통
        - 71-85: 긍정적
        - 86-100: 매우 긍정적
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # JSON 파싱
            result = json.loads(response.content[0].text)
            return True, result
        except Exception as e:
            return False, str(e)