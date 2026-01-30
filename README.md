# Multi-Agent Interview Coach

Система технического собеседования с использованием нескольких AI-агентов. Система имитирует реальное интервью, где агенты взаимодействуют между собой перед тем как задать следующий вопрос.

## Описание

Это мультиагентная система для проведения технических интервью. Особенность в том, что перед каждым ответом кандидату агенты анализируют ситуацию и обсуждают между собой следующий шаг. Пользователь видит только вопросы интервьюера, но в логах сохраняется вся внутренняя коммуникация агентов.

## Как работают агенты

Система состоит из четырех агентов, каждый из которых выполняет свою роль:

### 1. Interviewer Agent (Интервьюер)
Ведет диалог с кандидатом. Задает вопросы на основе рекомендаций других агентов.

Пример кода:
```python
class InterviewerAgent:
    def generate_response(self, state: dict) -> str:
        system_prompt = get_interviewer_prompt(state)
        context = self._build_context(state)
        
        prompt = f"""КОНТЕКСТ РАЗГОВОРА:
{context}

ПОСЛЕДНИЙ ОТВЕТ КАНДИДАТА:
{state.get('user_message', 'Начало интервью')}

Сгенерируйте ваш следующий вопрос или ответ."""
        
        response = self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt
        )
        return response.strip()
```

### 2. Observer Agent (Наблюдатель)
Анализирует ответы кандидата и определяет стратегию. Решает нужно ли усложнить или упростить вопросы.

Пример кода:
```python
class ObserverAgent:
    def analyze_response(self, state: dict) -> dict:
        analysis = self.llm.generate(
            prompt="""Проанализируйте ответ кандидата:
1. Оценка качества ответа
2. Уровень уверенности кандидата
3. Нужно ли изменить сложность вопросов?
4. Какую тему исследовать далее?"""
        )
        
        return {
            'analysis': analysis.strip(),
            'difficulty_change': self._determine_difficulty_change(analysis),
            'strategy_decision': self._extract_strategy(analysis)
        }
```

### 3. Evaluator Agent (Оценщик)
Проверяет фактическую корректность ответов кандидата. Выставляет оценки и сохраняет информацию о пробелах в знаниях.

### 4. Feedback Generator Agent (Генератор отчетов)
После завершения интервью генерирует подробный отчет с оценками, рекомендациями и планом развития.

## Как работает workflow

Процесс интервью выглядит так:

```python
def process_turn(self, user_message: str) -> str:
    # 1. Проверяем, не пытается ли кандидат уйти от темы
    validation = self.validator.validate_response(user_message, self.state)
    
    # 2. Observer анализирует ответ
    observer_result = self.observer.analyze_response(self.state)
    
    # 3. Evaluator проверяет корректность
    evaluator_result = self.evaluator.evaluate_response(self.state)
    
    # 4. Формируем внутренние мысли (скрыто от пользователя)
    internal_thoughts = f"[Observer]: {observer_result['analysis']} | "
    internal_thoughts += f"[Evaluator]: {evaluator_result['evaluation']} | "
    internal_thoughts += f"[Strategy]: {observer_result['strategy_decision']}"
    
    # 5. Interviewer задает следующий вопрос
    response = self.interviewer.generate_response(self.state)
    
    return response
```

## Структура проекта

```
Multi-Agent-Interview-Coach/
├── agents/                      # Агенты системы
│   ├── interviewer.py          # Интервьюер - задает вопросы
│   ├── observer.py             # Наблюдатель - анализирует ответы
│   ├── evaluator.py            # Оценщик - проверяет корректность
│   └── feedback_generator.py  # Генератор финального отчета
│
├── core/                        # Основная логика
│   ├── workflow.py             # Оркестрация работы агентов
│   └── prompts.py              # Системные промпты для агентов
│
├── models/                      # Модели данных
│   ├── schemas.py              # Схемы состояний (Pydantic)
│   └── llm_factory.py          # Фабрика для разных LLM провайдеров
│
├── memory/                      # Управление памятью и контекстом
│   ├── conversation_memory.py  # Хранение истории диалога
│   └── entity_tracker.py       # Отслеживание навыков и фактов
│
├── utils/                       # Вспомогательные утилиты
│   ├── logger.py               # Логирование в JSON
│   └── validators.py           # Валидация ответов
│
├── config/                      # Конфигурация
│   └── settings.py             # Настройки системы
│
├── logs/                        # Логи интервью
├── main.py                      # Точка входа
└── requirements.txt             # Зависимости
```

## Использованные технологии

- **Python 3.8+** - основной язык
- **LangGraph** - фреймворк для мультиагентных систем
- **LangChain** - инструменты для работы с LLM
- **Pydantic** - валидация данных и схемы
- **OpenAI / Anthropic / OpenRouter** - LLM провайдеры
- **Python-dotenv** - управление переменными окружения

### Почему LangGraph?

LangGraph позволяет строить сложные workflow с несколькими агентами. В этом проекте он используется для оркестрации:

```python
class InterviewWorkflow:
    def __init__(self):
        self.interviewer = InterviewerAgent()
        self.observer = ObserverAgent()
        self.evaluator = EvaluatorAgent()
        self.feedback_generator = FeedbackGeneratorAgent()
        
        self.memory = ConversationMemory()
        self.entity_tracker = EntityTracker()
```

## Установка

### 1. Склонируйте репозиторий
```bash
git clone <repository-url>
cd Multi-Agent-Interview-Coach
```

### 2. Создайте виртуальное окружение
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Установите зависимости
```bash
pip install -r requirements.txt
```

### 4. Настройте переменные окружения

Создайте файл `.env` в корне проекта:

```bash
# Выберите провайдера LLM
LLM_PROVIDER=openrouter

# Для OpenRouter (есть бесплатные модели)
OPENROUTER_API_KEY=sk-or-v1-ваш-ключ
OPENROUTER_MODEL=upstage/solar-pro-3:free

# Или для OpenAI
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-ваш-ключ
# OPENAI_MODEL=gpt-4

# Или для Anthropic
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=ваш-ключ
# ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

## Использование

Запустите интервью:

```bash
python main.py
```

Система попросит ввести информацию о кандидате:
- Имя
- Позиция (например, Backend Developer)
- Грейд (Junior/Middle/Senior)
- Опыт работы

### Команды во время интервью

- `/help` - показать справку
- `/status` - показать статус интервью
- `/finish` - завершить интервью и получить отчет
- `/quit` - выйти

### Пример работы

```
Интервьюер: Здравствуйте! Расскажите, что такое замыкание в JavaScript?

Вы: Это когда функция имеет доступ к переменным из внешней области видимости

[Internal Thoughts]:
[Observer]: Ответ базовый, но корректный | Strategy: Задать уточняющий вопрос
[Evaluator]: Ответ корректен | Score: 0.7

Интервьюер: Хорошо. А можете привести пример использования замыкания?
```

## Формат логов

Все интервью автоматически сохраняются в папке `logs/` в формате JSON:

```json
{
  "participant_name": "Алексей",
  "candidate_profile": {
    "name": "Алексей",
    "position": "Backend Developer",
    "grade": "Junior",
    "experience": "2 года Python, Django"
  },
  "turns": [
    {
      "turn_id": 1,
      "agent_visible_message": "Что такое декоратор в Python?",
      "user_message": "Это функция, которая оборачивает другую функцию",
      "internal_thoughts": "[Observer]: Базовое понимание есть | [Evaluator]: Корректно | [Strategy]: Уточнить детали",
      "performance_metrics": {
        "score": 0.7,
        "difficulty": 3
      }
    }
  ],
  "final_feedback": {
    "grade": "Junior",
    "hiring_recommendation": "Hire",
    "confidence_score": 75.0,
    "confirmed_skills": ["python", "django", "базовый OOP"],
    "knowledge_gaps": [
      {
        "topic": "async programming",
        "user_answer": "Не знаю как работает",
        "correct_answer": "async/await позволяет писать асинхронный код..."
      }
    ],
    "soft_skills": {
      "clarity": "Объясняет понятно, 7/10",
      "honesty": "Честно признает незнание",
      "engagement": "Задает уточняющие вопросы"
    },
    "roadmap": [
      "Изучить asyncio в Python",
      "Практика с многопоточностью",
      "Углубить знания SQL"
    ]
  }
}
```

## Примеры кода из проекта

### Память и контекст

Система сохраняет историю диалога и отслеживает упомянутые навыки:

```python
class ConversationMemory:
    def __init__(self, max_window: int = 10):
        self.messages = []
        self.max_window = max_window
    
    def add_message(self, role: str, content: str):
        self.messages.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now()
        })
        
        if len(self.messages) > self.max_window:
            self.messages = self.messages[-self.max_window:]
    
    def get_context(self, window: int = 5) -> str:
        recent = self.messages[-window:]
        return "\n".join([f"{m['role']}: {m['content']}" for m in recent])
```

### Валидация ответов

Система проверяет, не пытается ли кандидат уйти от темы:

```python
class RobustnessValidator:
    def validate_response(self, user_message: str, state: dict) -> dict:
        # Проверка на off-topic
        if self._is_off_topic(user_message):
            return {
                'is_valid': False,
                'issue': 'off_topic',
                'suggestion': 'Давайте вернемся к вопросу о технических навыках'
            }
        
        # Проверка на галлюцинации
        if self._contains_hallucination(user_message, state):
            return {
                'is_valid': False,
                'issue': 'hallucination',
                'suggestion': 'Вы уверены в этом утверждении?'
            }
        
        return {'is_valid': True}
```

### Адаптивная сложность

Система динамически меняет сложность вопросов:

```python
def _determine_difficulty_change(self, analysis: str, state: dict) -> int:
    # Анализируем последние результаты
    perf_history = state.get('performance_history', [])
    
    if len(perf_history) >= 2:
        recent_avg = sum(perf_history[-2:]) / 2
        
        # Если кандидат отвечает хорошо - усложняем
        if recent_avg > 0.8:
            return 1
        # Если плохо - упрощаем
        elif recent_avg < 0.4:
            return -1
    
    return 0
```

## Особенности реализации

1. **Ролевая специализация** - каждый агент отвечает за свою задачу
2. **Скрытая рефлексия** - агенты обсуждают ответы между собой, это скрыто от пользователя
3. **Контекстная память** - система помнит всю историю диалога
4. **Адаптивность** - сложность вопросов меняется в зависимости от ответов
5. **Устойчивость** - система распознает попытки уйти от темы или неправильные утверждения

## Лицензия

MIT