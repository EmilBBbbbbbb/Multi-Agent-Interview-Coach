from typing import List, Dict, Optional, Set, Any
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class Turn(BaseModel):
    turn_id: int
    agent_visible_message: str
    user_message: str
    internal_thoughts: str
    performance_metrics: Optional[Dict[str, float]] = None


class CandidateProfile(BaseModel):
    name: str
    position: str
    grade: str
    experience: str
    skills_claimed: List[str] = Field(default_factory=list)
    skills_verified: Dict[str, str] = Field(default_factory=dict)
    topics_covered: Set[str] = Field(default_factory=set)


class PerformanceMetrics(BaseModel):
    accuracy: float = 0.0
    completeness: float = 0.0
    communication_clarity: float = 0.0
    overall_score: float = 0.0


class KnowledgeGap(BaseModel):
    topic: str
    user_answer: str
    correct_answer: str


class FinalFeedback(BaseModel):
    grade: str
    hiring_recommendation: str
    confidence_score: float
    confirmed_skills: List[str] = Field(default_factory=list)
    knowledge_gaps: List[KnowledgeGap] = Field(default_factory=list)
    soft_skills: Dict[str, str] = Field(default_factory=dict)
    roadmap: List[str] = Field(default_factory=list)


class InterviewLog(BaseModel):
    participant_name: str
    candidate_profile: Optional[CandidateProfile] = None
    turns: List[Turn] = Field(default_factory=list)
    final_feedback: Optional[FinalFeedback] = None


class InterviewState(TypedDict, total=False):
    candidate_profile: CandidateProfile
    turns: List[Turn]
    current_turn_id: int
    user_message: str
    agent_message: str
    internal_thoughts: str
    current_difficulty: int
    performance_history: List[float]
    cumulative_score: float
    topics_covered: Set[str]
    topics_to_cover: List[str]
    should_continue: bool
    interview_complete: bool
    off_topic_count: int
    observer_analysis: str
    evaluator_feedback: str
    strategy_decision: str
