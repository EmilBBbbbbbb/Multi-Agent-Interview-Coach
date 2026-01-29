from typing import Set, Dict, List


class EntityTracker:
    def __init__(self):
        self.skills_claimed: Set[str] = set()
        self.skills_verified: Dict[str, str] = {}
        self.topics_covered: Set[str] = set()
        self.topics_to_cover: List[str] = []
        self.candidate_attributes: Dict[str, any] = {}
    
    def claim_skill(self, skill: str):
        self.skills_claimed.add(skill.lower())
    
    def verify_skill(self, skill: str, status: str):
        self.skills_verified[skill.lower()] = status
    
    def add_topic(self, topic: str):
        self.topics_covered.add(topic.lower())
    
    def add_topics_to_cover(self, topics: List[str]):
        self.topics_to_cover.extend([t.lower() for t in topics])
    
    def is_topic_covered(self, topic: str) -> bool:
        """Check if a topic has been covered.
        
        Args:
            topic: Topic name
            
        Returns:
            True if topic has been covered
        """
        return topic.lower() in self.topics_covered
    
    def get_next_topic(self) -> str:
        """Get the next topic to cover.
        
        Returns:
            Next topic name or empty string
        """
        for topic in self.topics_to_cover:
            if topic not in self.topics_covered:
                return topic
        
        return ""
    
    def get_unverified_skills(self) -> Set[str]:
        """Get skills that were claimed but not yet verified.
        
        Returns:
            Set of unverified skill names
        """
        return self.skills_claimed - set(self.skills_verified.keys())
    
    def get_verified_good_skills(self) -> List[str]:
        """Get skills verified as good.
        
        Returns:
            List of skill names with 'good' status
        """
        return [skill for skill, status in self.skills_verified.items() 
                if status == 'good']
    
    def get_weak_skills(self) -> List[str]:
        """Get skills verified as weak.
        
        Returns:
            List of skill names with 'weak' status
        """
        return [skill for skill, status in self.skills_verified.items() 
                if status == 'weak']
    
    def set_attribute(self, key: str, value: any):
        """Set a candidate attribute.
        
        Args:
            key: Attribute name
            value: Attribute value
        """
        self.candidate_attributes[key] = value
    
    def get_attribute(self, key: str, default: any = None) -> any:
        """Get a candidate attribute.
        
        Args:
            key: Attribute name
            default: Default value if not found
            
        Returns:
            Attribute value or default
        """
        return self.candidate_attributes.get(key, default)
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract potential skills from text (basic keyword matching).
        
        Args:
            text: Text to analyze
            
        Returns:
            List of detected skill keywords
        """
        # Common programming skills/technologies
        skill_keywords = [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#',
            'sql', 'nosql', 'mongodb', 'postgresql', 'mysql',
            'django', 'flask', 'fastapi', 'react', 'vue', 'angular',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'git', 'ci/cd', 'rest', 'api', 'microservices',
            'oop', 'async', 'multithreading', 'testing'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skill_keywords:
            if skill in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def extract_topics_from_text(self, text: str) -> List[str]:
        """Extract potential topics from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of detected topic keywords
        """
        # Common interview topics
        topic_keywords = [
            'data structures', 'algorithms', 'oop', 'functional programming',
            'databases', 'sql', 'design patterns', 'testing', 'debugging',
            'architecture', 'scalability', 'security', 'performance',
            'async', 'concurrency', 'networking', 'api design'
        ]
        
        text_lower = text.lower()
        found_topics = []
        
        for topic in topic_keywords:
            if topic in text_lower:
                found_topics.append(topic)
        
        return found_topics
    
    def get_coverage_summary(self) -> Dict[str, any]:
        """Get summary of coverage statistics.
        
        Returns:
            Dictionary with coverage statistics
        """
        return {
            'skills_claimed': len(self.skills_claimed),
            'skills_verified': len(self.skills_verified),
            'skills_good': len(self.get_verified_good_skills()),
            'skills_weak': len(self.get_weak_skills()),
            'topics_covered': len(self.topics_covered),
            'topics_remaining': len([t for t in self.topics_to_cover 
                                    if t not in self.topics_covered])
        }
