from typing import List, Optional
from .answeroption import AnswerSet
from .primitive import *
from .enums import SubjectType

class Question(IdentifiableUUID):
    text: str
    answers: List[AnswerSet]  # List of AnswerSet
    type: str
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


class QuestionSet(IdentifiableUUID):
    title: str
    questions: List[Question]
    