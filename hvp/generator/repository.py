from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Tuple
import json
import os

from hvp.core.enums import SubjectType, SurveyType
from hvp.generator.generator import Survey
from hvp.core.models import Participant

@dataclass
class SurveyResponse:
    survey_id: str
    participant_id: str
    responses: Dict[str, Any]  # question_id -> response
    start_time: datetime = field(default_factory=datetime.now)
    completion_time: Optional[datetime] = None
    completion_duration_seconds: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def mark_completed(self) -> None:
        """Mark the survey as completed."""
        self.completion_time = datetime.now()
        if self.start_time:
            delta = self.completion_time - self.start_time
            self.completion_duration_seconds = int(delta.total_seconds())
    
    def is_complete(self) -> bool:
        """Check if the survey is complete."""
        return self.completion_time is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the response to a dictionary."""
        return {
            "survey_id": self.survey_id,
            "participant_id": self.participant_id,
            "responses": self.responses,
            "start_time": self.start_time.isoformat(),
            "completion_time": self.completion_time.isoformat() if self.completion_time else None,
            "completion_duration_seconds": self.completion_duration_seconds,
            "metadata": self.metadata
        }

