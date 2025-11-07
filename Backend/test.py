# test_claude.py
import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from ai_service.claude_client import ClaudeClient

def test_claude_api():
    print("="*50)
    print("Claude API 테스트 시작")
    print("="*50)
    
    client = ClaudeClient()
    
    # 1. 연결 테스트
    print("\n1. 연결 테스트...")
    success, message = client.test_connection()
    if success:
        print(f"✅ 연결 성공: {message}")
    else:
        print(f"❌ 연결 실패: {message}")
        return
    
    # 2. 긍정적 리뷰 테스트
    print("\n2. 긍정적 리뷰 분석...")
    positive_review = "이 카페 정말 좋아요! 직원분들도 친절하시고 휠체어로 들어가기도 편했어요."
    success, result = client.analyze_review_sentiment(positive_review)
    if success:
        print(f"✅ 분석 성공:")
        print(f"   - 점수: {result.get('sentiment_score')}/100")
        print(f"   - 감성: {result.get('sentiment')}")
        print(f"   - 포인트: {result.get('key_points')}")
    else:
        print(f"❌ 분석 실패: {result}")
    
    # 3. 부정적 리뷰 테스트
    print("\n3. 부정적 리뷰 분석...")
    negative_review = "접근성이 너무 안 좋아요. 계단만 있고 도움도 안 줬어요."
    success, result = client.analyze_review_sentiment(negative_review)
    if success:
        print(f"✅ 분석 성공:")
        print(f"   - 점수: {result.get('sentiment_score')}/100")
        print(f"   - 감성: {result.get('sentiment')}")
        print(f"   - 포인트: {result.get('key_points')}")
    else:
        print(f"❌ 분석 실패: {result}")
    
    print("\n" + "="*50)
    print("테스트 완료!")
    print("="*50)

if __name__ == "__main__":
    test_claude_api()