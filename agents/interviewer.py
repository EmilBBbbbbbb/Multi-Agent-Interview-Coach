from models.llm_factory import LLMProvider, LLMFactory
from core.prompts import get_interviewer_prompt


class InterviewerAgent:
    def __init__(self, llm_provider: LLMProvider = None):
        self.llm = llm_provider or LLMFactory.create_provider()
    
    def generate_response(self, state: dict) -> str:
        system_prompt = get_interviewer_prompt(state)
        context = self._build_context(state)
        
        prompt = f"""КОНТЕКСТ РАЗГОВОРА:
{context}

ПОСЛЕДНИЙ ОТВЕТ КАНДИДАТА:
{state.get('user_message', 'Начало интервью')}

Сгенерируйте ваш следующий вопрос или ответ. Будьте естественным и профессиональным.
Задавайте только ОДИН вопрос.

ПИШИТЕ КОРОТКО: 2-4 предложения. ТОЛЬКО русский. БЕЗ форматирования."""
        
        response = self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=500
        )
        return response.strip()
    
    def _build_context(self, state: dict, window: int = 3) -> str:
        turns = state.get('turns', [])
        if not turns:
            return "Начало интервью"
        
        recent_turns = turns[-window:]
        context_parts = []
        for turn in recent_turns:
            context_parts.append(f"Интервьюер: {turn.agent_visible_message}")
            context_parts.append(f"Кандидат: {turn.user_message}")
        
        return "\n".join(context_parts)
    
    def generate_greeting(self, state: dict) -> str:
        profile = state.get('candidate_profile')
        name = profile.name if profile else 'кандидат'
        position = profile.position if profile else 'разработчик'
        
        system_prompt = get_interviewer_prompt(state)
        prompt = f"""Поприветствуйте кандидата {name}, который претендует на позицию {position}.
Представьтесь и объясните формат интервью. Будьте дружелюбны и профессиональны.
Затем задайте первый ТЕОРЕТИЧЕСКИЙ вопрос про базовые концепции технологии для этой позиции.
НЕ спрашивайте про опыт - он уже известен.

ПИШИТЕ КОРОТКО: максимум 3-4 предложения. ТОЛЬКО русский язык. БЕЗ форматирования."""
        
        response = self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1000
        )
        return response.strip()
