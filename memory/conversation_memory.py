from typing import List, Dict
from models.schemas import Turn


class ConversationMemory:
    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.all_turns: List[Turn] = []
    
    def add_turn(self, turn: Turn):
        self.all_turns.append(turn)
    
    def get_recent_context(self, n: int = None) -> List[Turn]:
        n = n or self.window_size
        return self.all_turns[-n:] if self.all_turns else []
    
    def get_all_turns(self) -> List[Turn]:
        return self.all_turns
    
    def get_conversation_summary(self) -> str:
        """Generate a summary of the conversation.
        
        Returns:
            Formatted summary string
        """
        if not self.all_turns:
            return "Нет истории разговора"
        
        summary_parts = [
            f"Всего ходов: {len(self.all_turns)}",
            f"\nПоследние {min(3, len(self.all_turns))} обмена:"
        ]
        
        for turn in self.all_turns[-3:]:
            summary_parts.append(f"\nХод {turn.turn_id}:")
            summary_parts.append(f"  Q: {turn.agent_visible_message[:100]}...")
            summary_parts.append(f"  A: {turn.user_message[:100]}...")
        
        return "\n".join(summary_parts)
    
    def search_turns_by_keyword(self, keyword: str) -> List[Turn]:
        """Search turns containing a specific keyword.
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            List of matching Turn objects
        """
        keyword_lower = keyword.lower()
        matching_turns = []
        
        for turn in self.all_turns:
            if (keyword_lower in turn.user_message.lower() or 
                keyword_lower in turn.agent_visible_message.lower()):
                matching_turns.append(turn)
        
        return matching_turns
    
    def has_discussed_topic(self, topic: str) -> bool:
        """Check if a topic has been discussed.
        
        Args:
            topic: Topic to check
            
        Returns:
            True if topic appears in conversation
        """
        topic_lower = topic.lower()
        
        for turn in self.all_turns:
            if (topic_lower in turn.user_message.lower() or 
                topic_lower in turn.agent_visible_message.lower()):
                return True
        
        return False
    
    def get_question_at_turn(self, turn_id: int) -> str:
        """Get the question asked at a specific turn.
        
        Args:
            turn_id: Turn ID to retrieve
            
        Returns:
            Question text or empty string
        """
        for turn in self.all_turns:
            if turn.turn_id == turn_id:
                return turn.agent_visible_message
        
        return ""
    
    def clear(self):
        """Clear all conversation history."""
        self.all_turns = []
