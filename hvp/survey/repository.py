from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Tuple
import json
import os

from hvp.core.enums import SubjectType, SurveyType
from hvp.survey.generator import Survey
from hvp.core.models import Participant
from hvp.survey.triagequestion import QuestionSet, TriageQuestion

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


class Repository:
    """Repository for storing and retrieving triage questions."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        self.question_sets: Dict[str, QuestionSet] = {}
        self.storage_dir = storage_dir
        if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
    
    def add_question_set(self, question_set: QuestionSet) -> str:
        """
        Add a question set to the repository.
        
        Args:
            question_set: The question set to add
            
        Returns:
            The set ID
        """
        self.question_sets[question_set.set_id] = question_set
        self._save_question_set(question_set)
        return question_set.set_id
    
    def get_question_set(self, set_id: str) -> Optional[QuestionSet]:
        """Get a question set by its ID."""
        if set_id in self.question_sets:
            return self.question_sets[set_id]
        
        # Try to load from storage
        loaded_set = self._load_question_set(set_id)
        if loaded_set:
            self.question_sets[set_id] = loaded_set
            return loaded_set
            
        return None
    
    def get_all_sets(self) -> List[QuestionSet]:
        """Get all question sets in the repository."""
        return list(self.question_sets.values())
    
    def _save_question_set(self, question_set: QuestionSet) -> None:
        """Save a question set to persistent storage."""
        if not self.storage_dir:
            return
            
        file_path = os.path.join(self.storage_dir, f"{question_set.set_id}.json")
        
        # Convert to dict for serialization
        data = {
            "set_id": question_set.set_id,
            "name": question_set.name,
            "description": question_set.description,
            "author": question_set.author,
            "created_date": question_set.created_date.isoformat(),
            "questions": [q.to_dict() for q in question_set.questions]
        }
        
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def _load_question_set(self, set_id: str) -> Optional[QuestionSet]:
        """Load a question set from persistent storage."""
        if not self.storage_dir:
            return None
            
        file_path = os.path.join(self.storage_dir, f"{set_id}.json")
        
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                
            # Create question set
            question_set = QuestionSet(
                set_id=data["set_id"],
                name=data["name"],
                description=data["description"],
                author=data.get("author", ""),
                created_date=datetime.fromisoformat(data["created_date"])
            )
            
            # Add questions
            for q_data in data["questions"]:
                question = TriageQuestion.from_dict(q_data)
                question_set.questions.append(question)
                
            return question_set
                
        except Exception as e:
            print(f"Error loading question set {set_id}: {e}")
            return None

class SurveyRepository:
    """Repository for storing and retrieving surveys."""
    
    def __init__(self, storage_dir: str = None):
        self.surveys: Dict[str, Survey] = {}
        self.storage_dir = storage_dir
        if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
    
    def add_survey(self, survey: Survey) -> None:
        """Add a survey to the repository."""
        self.surveys[survey.survey_id] = survey
        self._save_survey(survey)
    
    def get_survey(self, survey_id: str) -> Optional[Survey]:
        """Get a survey by its ID."""
        if survey_id in self.surveys:
            return self.surveys[survey_id]
        
        # Try to load from storage
        loaded_survey = self._load_survey(survey_id)
        if loaded_survey:
            self.surveys[survey_id] = loaded_survey
            return loaded_survey
            
        return None
    
    def get_surveys_for_subject_type(self, subject_type: SubjectType) -> List[Survey]:
        """Get all surveys for a specific subject type."""
        return [
            survey for survey in self.surveys.values()
            if survey.subject_type == subject_type
        ]
    
    def get_all_surveys(self) -> List[Survey]:
        """Get all surveys in the repository."""
        return list(self.surveys.values())
    
    def delete_survey(self, survey_id: str) -> bool:
        """Delete a survey from the repository."""
        if survey_id in self.surveys:
            del self.surveys[survey_id]
            
            if self.storage_dir:
                file_path = os.path.join(self.storage_dir, f"{survey_id}.json")
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
            return True
        return False
    
    def _save_survey(self, survey: Survey) -> None:
        """Save a survey to persistent storage."""
        if not self.storage_dir:
            return
            
        file_path = os.path.join(self.storage_dir, f"{survey.survey_id}.json")
        
        # Convert survey to dict for serialization
        survey_dict = {
            "survey_id": survey.survey_id,
            "title": survey.title,
            "description": survey.description,
            "canonical_url": survey.canonical_url,
            "publisher": survey.publisher,
            "version": survey.version,
            "created_date": survey.created_date.isoformat(),
            "subject_type": survey.subject_type.value,
            "survey_type": survey.survey_type.value,
            "estimated_completion_minutes": survey.estimated_completion_minutes,
            "language_code": survey.language_code,
            "metadata": survey.metadata,
            "questions": [
                {
                    "canonical_id": q.canonical_id,
                    "question_text": q.question_text,
                    "question_type": q.question_type.value,
                    "answer_choices": [
                        {"text": c.text, "value": c.value, "display_order": c.display_order}
                        for c in q.answer_choices
                    ],
                    "publisher": q.publisher,
                    "version": q.version,
                }
                for q in survey.questions
            ]
        }
        
        with open(file_path, "w") as f:
            json.dump(survey_dict, f, indent=2)
    
    def _load_survey(self, survey_id: str) -> Optional[Survey]:
        """Load a survey from persistent storage."""
        if not self.storage_dir:
            return None
            
        file_path = os.path.join(self.storage_dir, f"{survey_id}.json")
        
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, "r") as f:
                survey_dict = json.load(f)
                
            # Recreate Survey object from dict
            # This is simplified and would need proper deserialization in a real implementation
            from hvp.core.enums import SubjectType, SurveyType, QuestionType
            from hvp.survey.questions import QuestionItem, AnswerChoice
            
            questions = []
            for q_dict in survey_dict.get("questions", []):
                question = QuestionItem(
                    question_text=q_dict["question_text"],
                    answer_choices=[
                        AnswerChoice(
                            text=c["text"],
                            value=c["value"],
                            display_order=c.get("display_order", 0)
                        )
                        for c in q_dict.get("answer_choices", [])
                    ],
                    question_type=QuestionType(q_dict["question_type"]),
                    publisher=q_dict["publisher"],
                    canonical_id=q_dict["canonical_id"],
                    version=q_dict.get("version", "1.0")
                )
                questions.append(question)
                
            survey = Survey(
                questions=questions,
                canonical_url=survey_dict["canonical_url"],
                survey_id=survey_dict["survey_id"],
                title=survey_dict["title"],
                description=survey_dict.get("description", ""),
                publisher=survey_dict["publisher"],
                version=survey_dict["version"],
                created_date=datetime.fromisoformat(survey_dict["created_date"]),
                subject_type=SubjectType(survey_dict["subject_type"]),
                survey_type=SurveyType(survey_dict["survey_type"]),
                estimated_completion_minutes=survey_dict["estimated_completion_minutes"],
                language_code=survey_dict.get("language_code", "en"),
                metadata=survey_dict.get("metadata", {})
            )
            
            return survey
            
        except Exception as e:
            print(f"Error loading survey {survey_id}: {e}")
            return None


class SurveyResponseRepository:
    """Repository for storing and retrieving survey responses."""
    
    def __init__(self, storage_dir: str = None):
        self.responses: Dict[Tuple[str, str], SurveyResponse] = {}  # (survey_id, participant_id) -> response
        self.storage_dir = storage_dir
        if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
    
    def add_response(self, response: SurveyResponse) -> None:
        """Add a response to the repository."""
        key = (response.survey_id, response.participant_id)
        self.responses[key] = response
        self._save_response(response)
    
    def update_response(self, response: SurveyResponse) -> None:
        """Update an existing response."""
        key = (response.survey_id, response.participant_id)
        if key in self.responses:
            self.responses[key] = response
            self._save_response(response)
    
    def get_response(self, survey_id: str, participant_id: str):
        pass