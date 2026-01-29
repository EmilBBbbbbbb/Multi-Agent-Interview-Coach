from models.llm_factory import LLMProvider, LLMFactory
from core.prompts import get_observer_prompt
from config import settings


class ObserverAgent:
    def __init__(self, llm_provider: LLMProvider = None):
        self.llm = llm_provider or LLMFactory.create_cheap_provider()
    
    def analyze_response(self, state: dict) -> dict:
        system_prompt = get_observer_prompt(state)
        
        prompt = """Проанализируйте последний ответ кандидата и дайте рекомендации:

1. Оценка качества ответа (краткая)
2. Уровень уверенности кандидата
3. Нужно ли изменить сложность вопросов?
4. Какую тему/аспект исследовать далее?
5. Идет ли кандидат от темы или отвечает корректно?

Дайте конкретную ОДНУ рекомендацию для следующего вопроса."""
        
        analysis = self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=400
        )
        
        # Parse difficulty adjustment
        difficulty_change = self._determine_difficulty_change(analysis, state)
        
        return {
            'analysis': analysis.strip(),
            'difficulty_change': difficulty_change,
            'strategy_decision': self._extract_strategy(analysis)
        }
    
    def _determine_difficulty_change(self, analysis: str, state: dict) -> int:
        analysis_lower = analysis.lower()
        
        perf_history = state.get('performance_history', [])
        if len(perf_history) >= 2:
            recent_avg = sum(perf_history[-2:]) / 2
            if recent_avg > settings.PERFORMANCE_THRESHOLD_HIGH:
                return 1
            elif recent_avg < settings.PERFORMANCE_THRESHOLD_LOW:
                return -1
        if any(word in analysis_lower for word in ['усложнить', 'слишком просто', 'отлично', 'легко справляется']):
            return 1
        elif any(word in analysis_lower for word in ['упростить', 'сложно', 'не знает', 'пробелы', 'слабо']):
            return -1
        
        return 0
    
    def _extract_strategy(self, analysis: str) -> str:
        """Extract the main strategic decision from analysis.
        
        Args:
            analysis: Observer's analysis text
            
        Returns:
            Strategic recommendation for interviewer
        """
        # Try to find explicit recommendation
        lines = analysis.split('\n')
        for line in lines:
            if 'рекомендация' in line.lower() or 'следующий' in line.lower():
                return line.strip()
        
        # Return last substantial line
        for line in reversed(lines):
            if len(line.strip()) > 20:
                return line.strip()
        
        return analysis.strip()
    
    def check_interview_completion(self, state: dict) -> bool:
        """Check if interview should be completed.
        
        Args:
            state: Current interview state
            
        Returns:
            True if interview should end
        """
        turns = state.get('turns', [])
        max_turns = settings.MAX_INTERVIEW_TURNS
        
        # Check turn limit
        if len(turns) >= max_turns:
            return True
        
        # Check if enough topics covered
        topics_covered = state.get('topics_covered', set())
        if len(topics_covered) >= 5 and len(turns) >= 10:
            # Enough content for evaluation
            return True
        
        return False
