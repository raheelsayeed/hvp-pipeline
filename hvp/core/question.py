from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field 
import uuid

from .answeroption import AnswerOption, AnswerSet
from .patient import PatientVignettes
from .primitive import *
from .enums import SubjectType

class QuestionType(PrimitiveType):
    name: str

@add_from_json_method(QuestionType, 'categories.json')
class QuestionTypes(Enum):
    pass


class Question(IdentifiableUUID):
    text: str
    answers: List[AnswerSet]  # List of AnswerSet
    type: QuestionType
    subject: SubjectType = SubjectType.CLINICIAN
    canonical_identifier: Optional[str] = None
    publisher: Optional[str] = None
    derived_from: Optional['Question'] = None
    instruct_human: Optional[str] = None
    instruct_llm: Optional[str] = None


    def validate_answers(self):
        """
        Validates that each set of answers contains valid options.
        """
        for option_set in self.answers:
            if not option_set:
                raise ValueError("Each option set must contain at least one AnswerOption.")
            for option in option_set:
                if not isinstance(option, AnswerSet):
                    raise TypeError("Each option must be an instance of AnswerSet.")

    @classmethod
    def from_json(cls, data: dict) -> 'Question':

        return cls(
            text=data["text"],
            answers=[AnswerSet(**opts) for opts in data["answers"]],
            # answers=[[AnswerSet(**opt) for opt in option_set] for option_set in data["answers"]["option_sets"]],
            type=getattr(QuestionTypes, data['type'], None),
            tags=data.get('tags', None),

            subject=SubjectType(data['subject']),
            canonical_identifier=data.get("canonical_identifier"),
            publisher=data.get("publisher"),
            derived_from=None,  # Handle separately if needed
            date_created=datetime.fromisoformat(data.get("date_created")),
            identifier=data.get("identifier", str(uuid.uuid4()))
        )
    
    def to_json(self) -> dict:
        return {
            "text": self.text,
            "answers": [opts.model_dump() for opts in self.answers],
            "type": self.type.value,
            "subject": self.subject.value,
            "canonical_identifier": self.canonical_identifier,
            "publisher": self.publisher,
            "derived_from": self.derived_from.identifier if self.derived_from else None,
            "identifier": self.identifier
        }


    def to_markdown(self, file_path: Optional[str] = None) -> str:

        markdown = f"{self.text}\n\n"
        # Iterate over each AnswerSet
        for index, answer_set in enumerate(self.answers, start=1):
            markdown += f"\n**{answer_set.text or 'Please select one answer'}:**\n"
            for option in answer_set.options:
                markdown += f"- {option.text}\n"
        
        markdown += f"\n_Category: {self.type.name}, tags: {', '.join(self.tags)}_"
        
        # Optionally save to a file
        if file_path:
            with open(file_path, 'w') as file:
                file.write(markdown)
        
        return markdown



class QuestionSet(IdentifiableUUID):
    title: str
    questions: List[Question]
    