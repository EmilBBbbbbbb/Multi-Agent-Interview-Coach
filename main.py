import sys
from datetime import datetime
from core.workflow import InterviewWorkflow


def print_banner():
    print("\n" + "="*60)
    print("   MULTI-AGENT INTERVIEW COACH")
    print("="*60)
    print("   Система технического собеседования с AI-агентами")
    print("="*60 + "\n")


def get_candidate_info():
    print("Введите информацию о кандидате:\n")
    
    name = input("Имя кандидата: ").strip()
    if not name:
        name = "Кандидат"
    
    position = input("Позиция (например, Backend Developer): ").strip()
    if not position:
        position = "Developer"
    
    print("\nУровень (грейд):")
    print("  1. Junior")
    print("  2. Middle")
    print("  3. Senior")
    grade_choice = input("Выберите (1-3): ").strip()
    
    grade_map = {'1': 'Junior', '2': 'Middle', '3': 'Senior'}
    grade = grade_map.get(grade_choice, 'Junior')
    
    experience = input("\nОпыт работы (кратко): ").strip()
    if not experience:
        experience = "Начинающий разработчик"
    
    return name, position, grade, experience


def print_help():
    print("\nКоманды:")
    print("  /help    - Показать эту справку")
    print("  /status  - Показать статус интервью")
    print("  /finish  - Завершить интервью и получить фидбэк")
    print("  /quit    - Выйти без сохранения")
    print()


def run_interactive_interview():
    print_banner()
    
    # Get candidate information
    name, position, grade, experience = get_candidate_info()
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Clean name for filename - remove invalid characters
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).replace(' ', '_')
    log_filename = f"logs/interview_{timestamp}_{safe_name}.json"
    
    # Initialize workflow
    print("\n" + "-"*60)
    print("Инициализация системы...")
    print("-"*60)
    
    workflow = InterviewWorkflow(log_filepath=log_filename)
    workflow.initialize_interview(name, position, grade, experience)
    
    # Start interview
    print("\n" + "-"*60)
    print("Начало интервью")
    print("-"*60)
    
    greeting = workflow.start_interview()
    
    print_help()
    
    # Main interview loop
    turn_count = 0
    while not workflow.is_complete():
        # Get user input
        try:
            user_input = input("[Вы]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nИнтервью прервано пользователем.")
            break
        
        if not user_input:
            continue
        
        # Handle commands
        if user_input.startswith('/'):
            command = user_input.lower()
            
            if command == '/help':
                print_help()
                continue
            
            elif command == '/status':
                state = workflow.state
                print(f"\n--- Статус Интервью ---")
                print(f"Ходов: {len(state.get('turns', []))}")
                print(f"Сложность: {state.get('current_difficulty', 3)}/5")
                print(f"Средний балл: {state.get('cumulative_score', 0):.2f}")
                print(f"Темы: {', '.join(state.get('topics_covered', set()))}")
                print(f"----------------------\n")
                continue
            
            elif command == '/finish':
                print("\nЗавершение интервью...")
                workflow.state['interview_complete'] = True
                break
            
            elif command == '/quit':
                confirm = input("Вы уверены? Прогресс будет сохранен (y/n): ")
                if confirm.lower() == 'y':
                    print("\nВыход из программы.")
                    return
                continue
            
            else:
                print(f"Неизвестная команда: {command}")
                print("Введите /help для справки")
                continue
        
        # Process turn
        turn_count += 1
        response = workflow.process_turn(user_input)
        
        # Check if interview is complete
        if workflow.is_complete():
            break
    
    # Generate final feedback
    print("\n" + "="*60)
    print("Генерация финального отчета...")
    print("="*60 + "\n")
    
    summary = workflow.generate_final_feedback()
    
    print("\nИнтервью завершено!")
    print(f"Отчет сохранен: {log_filename}")
    print()


def run_batch_interview(name: str, position: str, grade: str, 
                       experience: str, responses: list):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Clean name for filename - remove invalid characters
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).replace(' ', '_')
    log_filename = f"logs/interview_{timestamp}_{safe_name}.json"
    
    workflow = InterviewWorkflow(log_filepath=log_filename)
    workflow.initialize_interview(name, position, grade, experience)
    
    print(f"\n[Batch Mode] Starting interview for {name}")
    
    # Start interview
    greeting = workflow.start_interview()
    
    # Process each response
    for i, response in enumerate(responses):
        if workflow.is_complete():
            break
        
        print(f"\n[Turn {i+1}] User: {response}")
        agent_response = workflow.process_turn(response)
        print(f"[Turn {i+1}] Agent: {agent_response[:100]}...")
    
    # Generate feedback
    workflow.generate_final_feedback()
    
    print(f"\n[Batch Mode] Interview complete. Log: {log_filename}")
    
    return log_filename


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            print("Usage:")
            print("  python main.py              - Interactive mode")
            print("  python main.py --help       - Show this help")
            print()
            return
    
    # Run interactive interview
    try:
        run_interactive_interview()
    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
