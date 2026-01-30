from typing import Dict, List
import re


class RobustnessValidator:
    OFF_TOPIC_KEYWORDS = [
        'погода', 'weather', 'политика', 'politics', 'спорт', 'sport',
        'футбол', 'football', 'кино', 'movie', 'музыка', 'music',
        'еда', 'food', 'путешествие', 'travel'
    ]
    
    ON_TOPIC_KEYWORDS = [
        'код', 'code', 'программ', 'program', 'разработка', 'develop',
        'язык', 'language', 'библиотека', 'library', 'фреймворк', 'framework',
        'база данных', 'database', 'алгоритм', 'algorithm', 'тест', 'test',
        'архитектура', 'architecture', 'проект', 'project', 'опыт', 'experience',
        'какие', 'какой', 'как', 'задач', 'работа', 'используете', 'делать',
        'вопрос', 'испытательный'
    ]
    
    @staticmethod
    def is_off_topic(message: str, context: str = "") -> bool:
        """Check if message is off-topic for a technical interview.
        
        Args:
            message: User's message
            context: Current interview context
            
        Returns:
            True if message appears off-topic
        """
        message_lower = message.lower()
        
        # Check for explicit off-topic keywords
        off_topic_count = sum(1 for keyword in RobustnessValidator.OFF_TOPIC_KEYWORDS 
                             if keyword in message_lower)
        
        # Check for on-topic keywords
        on_topic_count = sum(1 for keyword in RobustnessValidator.ON_TOPIC_KEYWORDS 
                            if keyword in message_lower)
        
        # Very short responses are suspicious
        if len(message.strip().split()) < 3:
            return False  # Too short to judge
        
        # If more off-topic than on-topic keywords
        if off_topic_count > 0 and on_topic_count == 0:
            return True
        
        # Check for common evasion patterns
        evasion_patterns = [
            r'давай(те)?\s+поговорим\s+о',
            r'а\s+можно\s+о',
            r'лучше\s+расскажи',
            r'смени\s+тему'
        ]
        
        for pattern in evasion_patterns:
            if re.search(pattern, message_lower):
                return True
        
        return False
    
    @staticmethod
    def detect_evasion(message: str) -> bool:
        """Detect if candidate is trying to evade the question.
        
        Args:
            message: User's message
            
        Returns:
            True if evasion detected
        """
        message_lower = message.lower()
        
        evasion_phrases = [
            'не знаю', 'не помню', 'не уверен', 'сложный вопрос',
            'нужно подумать', 'давно не работал', 'забыл',
            'don\'t know', 'not sure', 'can\'t remember'
        ]
        
        # Simple evasion is okay (honesty)
        simple_evasion = any(phrase in message_lower for phrase in evasion_phrases[:3])
        
        # But if message is ONLY evasion (very short), flag it
        if simple_evasion and len(message.strip().split()) <= 5:
            return True
        
        return False
    
    @staticmethod
    def check_hallucination_indicators(message: str) -> Dict[str, any]:
        """Check for indicators of potential hallucination or bluffing.
        
        Args:
            message: User's message
            
        Returns:
            Dict with hallucination risk assessment
        """
        message_lower = message.lower()
        
        # Confidence markers
        high_confidence = ['точно', 'уверен', 'definitely', 'absolutely', 
                          'exactly', 'obviously', 'clearly']
        
        low_confidence = ['наверное', 'вроде', 'кажется', 'думаю', 
                         'maybe', 'perhaps', 'probably', 'i think']
        
        # Vague language
        vague_terms = ['что-то', 'как-то', 'какой-то', 'типа', 
                      'something like', 'kind of', 'sort of']
        
        confidence_count = sum(1 for word in high_confidence if word in message_lower)
        uncertainty_count = sum(1 for word in low_confidence if word in message_lower)
        vague_count = sum(1 for word in vague_terms if word in message_lower)
        
        # High confidence + vague language = potential hallucination
        hallucination_risk = 'low'
        if confidence_count > 0 and vague_count > 1:
            hallucination_risk = 'high'
        elif confidence_count > 1:
            hallucination_risk = 'medium'  # Very confident - needs verification
        
        return {
            'risk_level': hallucination_risk,
            'confidence_markers': confidence_count,
            'uncertainty_markers': uncertainty_count,
            'vague_terms': vague_count,
            'requires_fact_check': hallucination_risk in ['medium', 'high'] or confidence_count > 1
        }
    
    @staticmethod
    def is_too_short(message: str, min_words: int = 5) -> bool:
        """Check if response is suspiciously short.
        
        Args:
            message: User's message
            min_words: Minimum expected words
            
        Returns:
            True if message is too short
        """
        words = message.strip().split()
        return len(words) < min_words
    
    @staticmethod
    def contains_technical_content(message: str) -> bool:
        """Check if message contains technical content.
        
        Args:
            message: User's message
            
        Returns:
            True if technical content detected
        """
        message_lower = message.lower()
        
        # Look for technical indicators
        technical_patterns = [
            r'\b\w+\(\)',  # Function calls
            r'\b\w+\.\w+',  # Method/property access
            r'\bclass\b', r'\bfunction\b', r'\bmethod\b',
            r'\barray\b', r'\blist\b', r'\bdict\b',
            r'\bapi\b', r'\bhttp\b', r'\bsql\b',
            r'\bimport\b', r'\bexport\b', r'\breturn\b'
        ]
        
        for pattern in technical_patterns:
            if re.search(pattern, message_lower):
                return True
        
        # Check for on-topic keywords
        on_topic_count = sum(1 for keyword in RobustnessValidator.ON_TOPIC_KEYWORDS 
                            if keyword in message_lower)
        
        return on_topic_count > 0
    
    @staticmethod
    def get_redirect_message() -> str:
        """Get a polite redirect message for off-topic responses.
        
        Returns:
            Redirect message
        """
        return ("Спасибо за ваш ответ, но давайте вернемся к техническим вопросам интервью. "
                "Это поможет мне лучше оценить ваши навыки для позиции.")
    
    @staticmethod
    def should_skip_evaluation(message: str) -> bool:
        """Check if message should skip technical evaluation.
        
        Args:
            message: User's message
            
        Returns:
            True if should skip evaluation
        """
        # Skip very short responses
        if RobustnessValidator.is_too_short(message, min_words=3):
            return True
        
        # Skip explicit "I don't know"
        if message.lower().strip() in ['не знаю', 'i don\'t know', 'не знаю']:
            return True
        
        return False
