# reviews/ai_analysis.py
import anthropic
from django.conf import settings

def analyze_review_sentiment(text):
    """
    리뷰 텍스트를 Claude API로 분석하여 0~100점 사이의 감성 점수를 반환합니다.
    """
    api_key = getattr(settings, 'CLAUDE_API_KEY', None)
    if not api_key:
        print("⚠️ CLAUDE_API_KEY가 설정되지 않았습니다.")
        return None

    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""
        다음은 장애인 접근성 관련 장소 리뷰입니다:
        "{text}"
        
        이 리뷰가 해당 장소의 접근성(이동 편리성, 시설 구비 등)에 대해 
        얼마나 긍정적인지 **0점에서 100점 사이의 정수**로만 평가해주세요.
        
        - 0~20점: 매우 부정적 (이용 불가, 위험함)
        - 40~60점: 중립적 또는 정보성 (단순 사실 나열)
        - 80~100점: 매우 긍정적 (매우 편리함, 추천함)
        
        반드시 **숫자만** 응답하세요. 다른 말은 하지 마세요.
        """

        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=10,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # 응답에서 숫자만 추출
        response_text = message.content[0].text.strip()
        # 숫자 외의 문자가 섞여 있을 경우를 대비해 숫자만 걸러냄
        score = int(''.join(filter(str.isdigit, response_text)))
        
        # 0~100 범위로 제한
        return max(0, min(score, 100))
        
    except Exception as e:
        print(f"🔥 AI 분석 실패: {e}")
        return None