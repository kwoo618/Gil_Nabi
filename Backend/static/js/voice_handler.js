// static/js/voice_handler.js
const voiceHandler = {
    // 음성 인식 (STT)
    startVoiceRecognition: function() {
        if (!('webkitSpeechRecognition' in window)) {
            alert('음성 인식이 지원되지 않는 브라우저입니다');
            return;
        }
        
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'ko-KR';
        
        recognition.onstart = function() {
            console.log('음성 인식 시작');
            document.getElementById('voice-btn').style.color = 'red';
        };
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            console.log('인식된 텍스트:', transcript);
            
            // 검색창에 입력
            document.getElementById('search-input').value = transcript;
            
            // AI 명령 처리
            voiceHandler.processVoiceCommand(transcript);
        };
        
        recognition.onerror = function(event) {
            console.error('음성 인식 오류:', event.error);
        };
        
        recognition.onend = function() {
            document.getElementById('voice-btn').style.color = 'black';
        };
        
        recognition.start();
    },
    
    // 음성 출력 (TTS)
    speak: function(text) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'ko-KR';
        utterance.rate = 1.0;
        speechSynthesis.speak(utterance);
    },
    
    // AI 명령 처리
    processVoiceCommand: function(command) {
        // "내 주변 휠체어 접근 가능한 카페"
        if (command.includes('휠체어') && command.includes('카페')) {
            document.getElementById('wheelchair').checked = true;
            mapFilter.updateFilters();
            mapSearch.search();
            this.speak('휠체어 접근 가능한 카페를 검색합니다');
        }
        // "AI 추천"
        else if (command.includes('추천')) {
            mapAI.getRecommendation();
            this.speak('AI 추천을 시작합니다');
        }
    }
};