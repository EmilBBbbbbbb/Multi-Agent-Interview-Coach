import json
from pathlib import Path
from typing import Optional
from models.schemas import Turn, InterviewLog, FinalFeedback, CandidateProfile


class InterviewLogger:
    def __init__(self, filepath: str = "logs/interview_log.json"):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self.log = InterviewLog(participant_name="", turns=[], final_feedback=None)
    
    def initialize(self, participant_name: str, candidate_profile: CandidateProfile):
        self.log.participant_name = participant_name
        self.log.candidate_profile = candidate_profile
        self.log.turns = []
        self.log.final_feedback = None
        self._save()
    
    def add_turn(self, turn: Turn):
        self.log.turns.append(turn)
        self._save()
    
    def set_final_feedback(self, feedback: FinalFeedback):
        self.log.final_feedback = feedback
        self._save()
    
    def _save(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            log_dict = self.log.model_dump(mode='json')
            json.dump(log_dict, f, indent=2, ensure_ascii=False)
    
    def get_log(self) -> InterviewLog:
        return self.log
    
    @classmethod
    def load_log(cls, filepath: str) -> InterviewLog:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return InterviewLog(**data)
