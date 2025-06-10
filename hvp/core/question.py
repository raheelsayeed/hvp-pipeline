from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field 
import uuid

from hvp.core.participant import Participant, ParticipantType

from .answeroption import AnswerOption, AnswerSet
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
    subject: SubjectType = SubjectType.HEALTHCARE_PROVIDER
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
            type=getattr(QuestionTypes, data['type'], None),
            tags=data.get('tags', None),
            subject=SubjectType(data['subject']),
            canonical_identifier=data.get("canonical_identifier"),
            publisher=data.get("publisher"),
            derived_from=None,  # Handle separately if needed
            date_created=datetime.fromisoformat(data.get("date_created")),
            identifier=data.get("identifier", str(uuid.uuid4())),
            instruct_llm=data.get("instruct_llm", None),
            instruct_human=data.get("instruct_human", None)
        )
    


    def display_item(self, answer_set: Optional[AnswerSet] = None, participant: Optional[Participant] = None, omit_metadata=False) -> str:
        
        question_item = ""
        if not omit_metadata:
            question_item += f"\n_Category: {self.type.name}, tags: {', '.join(self.tags)}_\n\n"
        
        question_item += f"{self.text}\n\n"

        if participant:
            instruction = self.instruct_llm if participant.type == ParticipantType.LLM else self.instruct_human
            question_item += f"Instruction: {instruction}\n\n" if instruction else ""
        else:
            question_item += f"Instruct Human: {self.instruct_human or '-'}\n\nInstruct LLM: {self.instruct_llm or '-'}\n\n"

        if answer_set:
            question_item += f"\n**{answer_set.text or 'Please select one answer'}:**\n\n"
            for option in answer_set.options:
                question_item += f"- {option.text}\n"
        else:
            for index, answer_set in enumerate(self.answers, start=1):
                question_item += f"\n**{answer_set.text or 'Please select one answer'}:**\n"
                for option in answer_set.options:
                    question_item += f"- {option.text}\n"
        
        
        return question_item


    def to_markdown(self, file_path: Optional[str] = None) -> str:

        markdown = self.display_item()
        # markdown = f"{self.text}\n\n"
        
        # for index, answer_set in enumerate(self.answers, start=1):
        #     markdown += f"\n**{answer_set.text or 'Please select one answer'}:**\n"
        #     for option in answer_set.options:
        #         markdown += f"- {option.text}\n"

        
        # Optionally save to a file
        if file_path:
            with open(file_path, 'w') as file:
                file.write(markdown)
        
        return markdown


    def to_json(self) -> dict:
        return {
            "text": self.text,
            "type": self.type.value,
            "subject": self.subject.value,
            "canonical_identifier": self.canonical_identifier,
            "publisher": self.publisher,
            "derived_from": self.derived_from.identifier if self.derived_from else None,
            "identifier": self.identifier,
            "instruct_human": self.instruct_human,
            "instruct_llm": self.instruct_llm,
            "answers": [opts.model_dump() for opts in self.answers],
            "date_created": self.date_created.isoformat(),
        }

class QuestionSet(IdentifiableUUID):
    title: str
    questions: List[Question]
    