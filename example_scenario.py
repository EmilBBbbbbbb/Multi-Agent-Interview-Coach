"""Example scenario for testing the interview system."""

from main import run_batch_interview


def scenario_junior_backend():
    """Scenario: Junior Backend Developer with basic Python knowledge."""
    
    print("\n" + "="*60)
    print("   SCENARIO: Junior Backend Developer")
    print("="*60 + "\n")
    
    name = "Алексей"
    position = "Backend Developer"
    grade = "Junior"
    experience = "Пет-проекты на Django, немного SQL, изучаю Python 6 месяцев"
    
    # Predefined responses
    responses = [
        "Привет! Я Алексей, претендую на позицию Junior Backend Developer. Знаю Python, немного Django и SQL.",
        
        "List - это изменяемая коллекция, можно добавлять и удалять элементы. Tuple - неизменяемый, после создания изменить нельзя.",
        
        "Используется для описания классов и их методов. Например, class User с методами login и logout.",
        
        "Hmm, не очень уверен. Думаю, это что-то связано с выполнением задач параллельно?",
        
        "Ну, я пробовал делать SELECT запросы, JOIN для объединения таблиц. Немного работал с PostgreSQL.",
        
        "Честно говоря, не знаю точно. Наверное, это для создания таблиц?",
        
        "Обычно я пробую разные варианты, смотрю в документацию, иногда спрашиваю у более опытных коллег.",
        
        "Да, был проект - простой блог на Django. Там были модели для постов и комментариев, формы для создания постов.",
        
        "Спасибо за интервью! Было интересно."
    ]
    
    # Run batch interview
    log_file = run_batch_interview(name, position, grade, experience, responses)
    
    print(f"\n✓ Scenario completed")
    print(f"✓ Log file: {log_file}")
    
    return log_file


def scenario_middle_python():
    """Scenario: Middle Python Developer with good knowledge."""
    
    print("\n" + "="*60)
    print("   SCENARIO: Middle Python Developer")
    print("="*60 + "\n")
    
    name = "Мария"
    position = "Python Developer"
    grade = "Middle"
    experience = "3 года коммерческого опыта, Django, FastAPI, PostgreSQL, Redis"
    
    responses = [
        "Здравствуйте! Я Мария, 3 года работаю Python разработчиком. Опыт с Django, FastAPI, работала с микросервисами.",
        
        "Словарь в Python использует хеш-таблицы. Ключи должны быть hashable, сложность поиска O(1) в среднем случае.",
        
        "async/await - синтаксис для асинхронного программирования. Позволяет писать неблокирующий код. Используется с asyncio, aiohttp.",
        
        "Индексы ускоряют поиск по столбцам. B-tree для большинства случаев, Hash для точного совпадения, Full-text для текстового поиска.",
        
        "Да, работала. REST API на FastAPI с Pydantic моделями, JWT аутентификация, rate limiting, документация через OpenAPI.",
        
        "Создаешь виртуальное окружение, устанавливаешь зависимости, настраиваешь pytest, пишешь unit-тесты и интеграционные тесты.",
        
        "Использую логгирование на разных уровнях, pdb или debugger в IDE, анализирую traceback, пишу тесты для воспроизведения.",
        
        "Работала над системой обработки заказов. Асинхронная обработка через Celery, кеширование в Redis, PostgreSQL с репликацией."
    ]
    
    log_file = run_batch_interview(name, position, grade, experience, responses)
    
    print(f"\n✓ Scenario completed")
    print(f"✓ Log file: {log_file}")
    
    return log_file


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "junior":
            scenario_junior_backend()
        elif sys.argv[1] == "middle":
            scenario_middle_python()
        else:
            print("Usage: python example_scenario.py [junior|middle]")
    else:
        print("Running all scenarios...\n")
        
        try:
            scenario_junior_backend()
            print("\n" + "="*60 + "\n")
            scenario_middle_python()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\nMake sure you have set up your .env file with API keys!")
            import traceback
            traceback.print_exc()
