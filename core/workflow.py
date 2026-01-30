"""Main interview workflow using LangGraph."""

from typing import Dict, Any
from models.schemas import InterviewState, Turn, CandidateProfile
from agents import InterviewerAgent, ObserverAgent, EvaluatorAgent, FeedbackGeneratorAgent
from memory import ConversationMemory, EntityTracker
from utils.logger import InterviewLogger
from utils.validators import RobustnessValidator
from config import settings


class InterviewWorkflow:
    """Orchestrates the multi-agent interview process."""
    
    def __init__(self, log_filepath: str = "logs/interview_log.json"):
        """Initialize the interview workflow.
        
        Args:
            log_filepath: Path to save interview logs
        """
        # Initialize agents
        self.interviewer = InterviewerAgent()
        self.observer = ObserverAgent()
        self.evaluator = EvaluatorAgent()
        self.feedback_generator = FeedbackGeneratorAgent()
        
        # Initialize memory
        self.memory = ConversationMemory()
        self.entity_tracker = EntityTracker()
        
        # Initialize logger
        self.logger = InterviewLogger(log_filepath)
        
        # Initialize validator
        self.validator = RobustnessValidator()
        
        # State
        self.state: Dict[str, Any] = {}
    
    def initialize_interview(self, name: str, position: str, grade: str, experience: str):
        """Initialize a new interview session.
        
        Args:
            name: Candidate name
            position: Position applying for
            grade: Grade level (Junior, Middle, Senior)
            experience: Experience description
        """
        # Create candidate profile
        profile = CandidateProfile(
            name=name,
            position=position,
            grade=grade,
            experience=experience
        )
        
        # Extract skills from experience
        skills = self.entity_tracker.extract_skills_from_text(experience)
        for skill in skills:
            self.entity_tracker.claim_skill(skill)
        
        # Initialize state
        self.state = {
            'candidate_profile': profile,
            'turns': [],
            'current_turn_id': 0,
            'user_message': '',
            'agent_message': '',
            'internal_thoughts': '',
            'current_difficulty': 3,  # Start at medium
            'performance_history': [],
            'cumulative_score': 0.0,
            'topics_covered': set(),
            'topics_to_cover': self._get_initial_topics(position),
            'should_continue': True,
            'interview_complete': False,
            'off_topic_count': 0,
            'observer_analysis': '',
            'evaluator_feedback': '',
            'strategy_decision': 'Начните интервью с приветствия и первого вопроса'
        }
        
        # Initialize logger
        self.logger.initialize(name, profile)
        
        print(f"Интервью инициализировано для {name} на позицию {position} ({grade})")
    
    def start_interview(self) -> str:
        """Start the interview with a greeting.
        
        Returns:
            Initial greeting message
        """
        greeting = self.interviewer.generate_greeting(self.state)
        self.state['agent_message'] = greeting
        
        print(f"\n[Интервьюер]: {greeting}\n")
        
        return greeting
    
    def process_turn(self, user_message: str) -> str:
        """Process a single conversation turn.
        
        Args:
            user_message: User's response
            
        Returns:
            Agent's next question/response
        """
        self.state['user_message'] = user_message
        self.state['current_turn_id'] += 1
        
        # --- HIDDEN REFLECTION STAGE (Internal Agent Communication) ---
        
        # 1. Check for robustness issues - но НЕ блокируем встречные вопросы
        is_question = '?' in user_message
        if self.validator.is_off_topic(user_message) and not is_question:
            self.state['off_topic_count'] += 1
            
            # Даем больше свободы - возвращаем только после 3-х попыток
            if self.state['off_topic_count'] >= 3:
                response = self.validator.get_redirect_message()
                internal_thoughts = "[Observer]: Candidate going off-topic repeatedly. Redirecting."
                self._save_turn(response, internal_thoughts, 0.0)
                return response
        
        # 2. Observer analyzes response (HIDDEN)
        observer_result = self.observer.analyze_response(self.state)
        self.state['observer_analysis'] = observer_result['analysis']
        self.state['strategy_decision'] = observer_result['strategy_decision']
        
        # Get the last question asked
        last_question = ""
        if self.state['turns']:
            last_question = self.state['turns'][-1].agent_visible_message
        
        # 3. Evaluator checks facts (HIDDEN)
        if not self.validator.should_skip_evaluation(user_message):
            evaluator_result = self.evaluator.evaluate_response(self.state, last_question)
            self.state['evaluator_feedback'] = evaluator_result['feedback']
            performance_score = evaluator_result['score']
        else:
            evaluator_result = {'score': 0.3, 'feedback': 'Insufficient answer', 'correct_answer': ''}
            performance_score = 0.3
        
        # Update performance history
        self.state['performance_history'].append(performance_score)
        self.state['cumulative_score'] = sum(self.state['performance_history']) / len(self.state['performance_history'])
        
        # 4. Adjust difficulty based on observer's recommendation
        difficulty_change = observer_result['difficulty_change']
        old_difficulty = self.state['current_difficulty']
        new_difficulty = max(settings.DIFFICULTY_MIN, 
                            min(settings.DIFFICULTY_MAX, 
                                old_difficulty + difficulty_change))
        
        if new_difficulty != old_difficulty:
            self.state['current_difficulty'] = new_difficulty
        
        # 5. Extract and track topics
        topics = self.entity_tracker.extract_topics_from_text(user_message + " " + last_question)
        for topic in topics:
            self.entity_tracker.add_topic(topic)
            self.state['topics_covered'].add(topic)
        
        # --- END HIDDEN REFLECTION ---
        
        # 6. Generate internal thoughts summary (for logging)
        internal_thoughts = self._compile_internal_thoughts(
            observer_result['analysis'],
            evaluator_result['feedback'],
            observer_result['strategy_decision'],
            performance_score
        )
        
        # 7. Check if interview should end
        if self.observer.check_interview_completion(self.state):
            self.state['should_continue'] = False
            self.state['interview_complete'] = True
            
            # Generate final response
            response = "Спасибо за ваши ответы! Это был последний вопрос. Сейчас я подготовлю для вас финальный фидбэк."
            self._save_turn(response, internal_thoughts, performance_score)
            
            return response
        
        # 8. Interviewer generates next question (USER-FACING)
        response = self.interviewer.generate_response(self.state)
        
        # Check if response is empty
        if not response or not response.strip():
            response = "Прошу прощения, могу ли вы повторить ваш ответ? Не совсем понял."
        
        self.state['agent_message'] = response
        
        # 9. Save turn to log
        self._save_turn(response, internal_thoughts, performance_score)
        
        print(f"\n[Интервьюер]: {response}\n")
        
        return response
    
    def generate_final_feedback(self) -> str:
        """Generate final feedback report.
        
        Returns:
            Feedback summary
        """
        # Generate feedback
        feedback = self.feedback_generator.generate_feedback(self.state)
        
        # Save to logger
        self.logger.set_final_feedback(feedback)
        
        # Print summary
        print("\n" + "="*60)
        print("ФИНАЛЬНЫЙ ОТЧЕТ")
        print("="*60)
        print(f"\nВЕРДИКТ:")
        print(f"  Грейд: {feedback.grade}")
        print(f"  Рекомендация: {feedback.hiring_recommendation}")
        print(f"  Уверенность: {feedback.confidence_score}%")
        
        print(f"\nПОДТВЕРЖДЕННЫЕ НАВЫКИ:")
        for skill in feedback.confirmed_skills[:5]:
            print(f"  + {skill}")
        
        print(f"\nПРОБЕЛЫ В ЗНАНИЯХ:")
        for gap in feedback.knowledge_gaps[:3]:
            print(f"  - {gap.topic}")
            print(f"    Ваш ответ: {gap.user_answer[:60]}...")
            print(f"    Правильно: {gap.correct_answer[:60]}...")
        
        print(f"\nROADMAP ДЛЯ РАЗВИТИЯ:")
        for item in feedback.roadmap[:5]:
            print(f"  > {item}")
        
        print("\n" + "="*60)
        print(f"Полный отчет сохранен в: {self.logger.filepath}")
        print("="*60 + "\n")
        
        return self.feedback_generator.generate_quick_summary(self.state)
    
    def _save_turn(self, agent_message: str, internal_thoughts: str, score: float):
        """Save a turn to memory and log.
        
        Args:
            agent_message: Message shown to user
            internal_thoughts: Internal agent communications
            score: Performance score for this turn
        """
        turn = Turn(
            turn_id=self.state['current_turn_id'],
            agent_visible_message=agent_message,
            user_message=self.state['user_message'],
            internal_thoughts=internal_thoughts,
            performance_metrics={'score': score}
        )
        
        # Save to memory
        self.memory.add_turn(turn)
        self.state['turns'].append(turn)
        
        # Save to log file
        self.logger.add_turn(turn)
    
    def _compile_internal_thoughts(self, observer_analysis: str, 
                                   evaluator_feedback: str,
                                   strategy: str, score: float) -> str:
        """Compile internal thoughts from all agents.
        
        Args:
            observer_analysis: Observer's analysis
            evaluator_feedback: Evaluator's feedback
            strategy: Strategic decision
            score: Performance score
            
        Returns:
            Formatted internal thoughts string
        """
        thoughts = []
        
        thoughts.append(f"[Observer]: {observer_analysis}")
        thoughts.append(f"[Evaluator]: {evaluator_feedback} | Score: {score:.2f}")
        thoughts.append(f"[Strategy]: {strategy}")
        
        return " | ".join(thoughts)
    
    def _get_initial_topics(self, position: str) -> list:
        """Get initial topics to cover based on position.
        
        Args:
            position: Position name
            
        Returns:
            List of topics
        """
        # Common topics for technical positions
        common_topics = [
            'programming basics',
            'data structures',
            'algorithms',
            'oop',
            'testing',
            'debugging'
        ]
        
        position_lower = position.lower()
        
        if 'backend' in position_lower or 'server' in position_lower:
            common_topics.extend(['databases', 'api design', 'architecture'])
        elif 'frontend' in position_lower:
            common_topics.extend(['html/css', 'javascript', 'frameworks'])
        elif 'fullstack' in position_lower or 'full stack' in position_lower:
            common_topics.extend(['databases', 'api design', 'frontend frameworks'])
        
        return common_topics
    
    def is_complete(self) -> bool:
        """Check if interview is complete.
        
        Returns:
            True if interview is finished
        """
        return self.state.get('interview_complete', False)
