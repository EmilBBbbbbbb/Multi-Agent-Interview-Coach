import re
from models.llm_factory import LLMProvider, LLMFactory
from core.prompts import get_evaluator_prompt


class EvaluatorAgent:
    def __init__(self, llm_provider: LLMProvider = None):
        self.llm = llm_provider or LLMFactory.create_cheap_provider()
    
    def evaluate_response(self, state: dict, interviewer_question: str) -> dict:
        system_prompt = get_evaluator_prompt(state, interviewer_question)
        
        prompt = """Оцените технический ответ кандидата по следующим критериям:

1. Фактическая корректность (correct/incorrect/partial)
2. Полнота ответа (complete/partial/incomplete)
3. Глубина понимания (deep/medium/shallow)
4. Числовая оценка 0.0 - 1.0

Если ответ содержит ошибки, укажите ПРАВИЛЬНЫЙ ответ.

Формат: [Evaluator]: <корректность> | Балл: <число> | <комментарий>
Правильный ответ (если нужен): <ответ>"""
        
        evaluation = self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=500
        )
        
        # Parse evaluation
        score = self._extract_score(evaluation)
        correctness = self._extract_correctness(evaluation)
        correct_answer = self._extract_correct_answer(evaluation)
        
        return {
            'evaluation': evaluation.strip(),
            'score': score,
            'correctness': correctness,
            'correct_answer': correct_answer,
            'feedback': evaluation.strip()
        }
    
    def _extract_score(self, evaluation: str) -> float:
        """Extract numerical score from evaluation.
        
        Args:
            evaluation: Evaluation text
            
        Returns:
            Score between 0.0 and 1.0
        """
        # Look for "Балл: X.X" pattern
        match = re.search(r'[Бб]алл:\s*(\d+\.?\d*)', evaluation)
        if match:
            try:
                score = float(match.group(1))
                return min(max(score, 0.0), 1.0)
            except ValueError:
                pass
        
        # Fallback: analyze keywords
        eval_lower = evaluation.lower()
        if any(word in eval_lower for word in ['отлично', 'правильно', 'корректно', 'correct']):
            return 0.8
        elif any(word in eval_lower for word in ['частично', 'неполно', 'partial']):
            return 0.5
        elif any(word in eval_lower for word in ['неправильно', 'ошибка', 'incorrect']):
            return 0.2
        
        return 0.5  # Default neutral score
    
    def _extract_correctness(self, evaluation: str) -> str:
        """Extract correctness assessment from evaluation.
        
        Args:
            evaluation: Evaluation text
            
        Returns:
            'correct', 'partial', or 'incorrect'
        """
        eval_lower = evaluation.lower()
        
        if 'incorrect' in eval_lower or 'неправильно' in eval_lower or 'ошибк' in eval_lower:
            return 'incorrect'
        elif 'partial' in eval_lower or 'частично' in eval_lower or 'неполн' in eval_lower:
            return 'partial'
        elif 'correct' in eval_lower or 'правильно' in eval_lower or 'корректн' in eval_lower:
            return 'correct'
        
        return 'partial'
    
    def _extract_correct_answer(self, evaluation: str) -> str:
        """Extract the correct answer if provided in evaluation.
        
        Args:
            evaluation: Evaluation text
            
        Returns:
            Correct answer or empty string
        """
        # Look for "Правильный ответ:" pattern
        match = re.search(r'[Пп]равильный ответ[:\s]+(.+?)(?:\n|$)', evaluation, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Alternative pattern
        match = re.search(r'[Дд]олжен был[:\s]+(.+?)(?:\n|$)', evaluation, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        return ""
    
    def calculate_performance_metrics(self, state: dict) -> dict:
        """Calculate comprehensive performance metrics.
        
        Args:
            state: Current interview state
            
        Returns:
            Dict with accuracy, completeness, communication clarity scores
        """
        perf_history = state.get('performance_history', [])
        
        if not perf_history:
            return {
                'accuracy': 0.0,
                'completeness': 0.0,
                'communication_clarity': 0.0,
                'overall_score': 0.0
            }
        
        accuracy = sum(perf_history) / len(perf_history)
        
        # Estimate other metrics from recent performance
        recent = perf_history[-3:] if len(perf_history) >= 3 else perf_history
        completeness = sum(recent) / len(recent)
        
        # Communication clarity - assume good if scores improving
        if len(perf_history) >= 2:
            trend = perf_history[-1] - perf_history[0]
            communication_clarity = 0.5 + min(trend, 0.3)
        else:
            communication_clarity = 0.7
        
        overall = (accuracy * 0.5 + completeness * 0.3 + communication_clarity * 0.2)
        
        return {
            'accuracy': round(accuracy, 2),
            'completeness': round(completeness, 2),
            'communication_clarity': round(communication_clarity, 2),
            'overall_score': round(overall, 2)
        }
