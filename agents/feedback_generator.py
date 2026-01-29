import json
from typing import Dict, List
from models.llm_factory import LLMProvider, LLMFactory
from models.schemas import FinalFeedback, KnowledgeGap
from core.prompts import get_feedback_prompt


class FeedbackGeneratorAgent:
    def __init__(self, llm_provider: LLMProvider = None):
        self.llm = llm_provider or LLMFactory.create_provider()
    
    def generate_feedback(self, state: dict) -> FinalFeedback:
        interview_history = self._build_interview_history(state)
        
        system_prompt = get_feedback_prompt(state, interview_history)
        
        prompt = """На основе всего интервью составьте финальный отчет в JSON формате:

{
  "grade": "Junior|Middle|Senior",
  "hiring_recommendation": "Hire|No Hire|Strong Hire",
  "confidence_score": 0-100,
  "reasoning": "краткое обоснование",
  "confirmed_skills": ["навык1", "навык2", ...],
  "knowledge_gaps": [
    {
      "topic": "тема",
      "user_answer": "что ответил кандидат",
      "correct_answer": "правильный ответ"
    }
  ],
  "soft_skills": {
    "clarity": "оценка 1-10 + комментарий",
    "honesty": "комментарий о честности",
    "engagement": "комментарий о вовлеченности"
  },
  "roadmap": ["тема для изучения 1", "тема 2", ...]
}

Будьте объективны и конструктивны."""
        
        response = self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=2000
        )
        
        # Parse JSON response
        feedback_data = self._parse_feedback_json(response)
        
        # Create FinalFeedback object
        feedback = FinalFeedback(
            grade=feedback_data.get('grade', 'Junior'),
            hiring_recommendation=feedback_data.get('hiring_recommendation', 'No Hire'),
            confidence_score=float(feedback_data.get('confidence_score', 50)),
            confirmed_skills=feedback_data.get('confirmed_skills', []),
            knowledge_gaps=[
                KnowledgeGap(**gap) for gap in feedback_data.get('knowledge_gaps', [])
            ],
            soft_skills=feedback_data.get('soft_skills', {}),
            roadmap=feedback_data.get('roadmap', [])
        )
        
        return feedback
    
    def _build_interview_history(self, state: dict) -> str:
        """Build a formatted summary of the interview.
        
        Args:
            state: Interview state
            
        Returns:
            Formatted interview history string
        """
        turns = state.get('turns', [])
        
        history_parts = []
        for turn in turns:
            history_parts.append(f"\n--- Ход {turn.turn_id} ---")
            history_parts.append(f"Вопрос: {turn.agent_visible_message}")
            history_parts.append(f"Ответ: {turn.user_message}")
            
            if turn.internal_thoughts:
                history_parts.append(f"Оценка: {turn.internal_thoughts}")
        
        return "\n".join(history_parts)
    
    def _parse_feedback_json(self, response: str) -> dict:
        """Parse JSON feedback from LLM response.
        
        Args:
            response: LLM response text
            
        Returns:
            Parsed feedback dictionary
        """
        # Try to extract JSON from response
        try:
            # Look for JSON block
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # Fallback: create basic feedback from text analysis
        return self._fallback_parse(response)
    
    def _fallback_parse(self, response: str) -> dict:
        """Fallback parser if JSON parsing fails.
        
        Args:
            response: LLM response text
            
        Returns:
            Basic feedback dictionary
        """
        response_lower = response.lower()
        
        # Determine grade
        grade = "Junior"
        if "senior" in response_lower:
            grade = "Senior"
        elif "middle" in response_lower:
            grade = "Middle"
        
        # Determine recommendation
        recommendation = "No Hire"
        if "strong hire" in response_lower or "однозначно нанять" in response_lower:
            recommendation = "Strong Hire"
        elif "hire" in response_lower or "нанять" in response_lower:
            recommendation = "Hire"
        
        return {
            'grade': grade,
            'hiring_recommendation': recommendation,
            'confidence_score': 60,
            'confirmed_skills': [],
            'knowledge_gaps': [],
            'soft_skills': {
                'clarity': 'Средняя',
                'honesty': 'Требуется анализ',
                'engagement': 'Требуется анализ'
            },
            'roadmap': ['Проанализируйте ответы вручную для детального плана']
        }
    
    def generate_quick_summary(self, state: dict) -> str:
        """Generate a quick text summary of the interview.
        
        Args:
            state: Interview state
            
        Returns:
            Brief text summary
        """
        perf_history = state.get('performance_history', [])
        avg_score = sum(perf_history) / len(perf_history) if perf_history else 0
        
        profile = state.get('candidate_profile')
        name = profile.name if profile else 'Кандидат'
        
        summary = f"""Интервью завершено: {name}
Вопросов задано: {len(state.get('turns', []))}
Средняя оценка: {avg_score:.2f}
Темы покрыты: {', '.join(state.get('topics_covered', set()))}
"""
        
        return summary
