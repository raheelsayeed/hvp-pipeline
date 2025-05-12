from typing import List, Callable, Optional
from pydantic import BaseModel
import uuid

# Assuming these imports are correctly set up in your project
from ..core.question import Question, QuestionSet
from ..core.survey import Survey
from ..core.participant import Participant  # Ensure this import is correct
class SurveyGenerator(BaseModel):

    def create_and_assign(self, 
                      num_questions: int, 
                      question_set: QuestionSet,
                      participant: Participant,
                      filter_func: Optional[Callable[[Question, Participant], bool]] = None) -> Survey:

        filtered_questions = question_set.questions

        if filter_func:
            filtered_questions = [q for q in filtered_questions if filter_func(q, participant)]

        if len(filtered_questions) < num_questions:
            raise ValueError(f"Not enough questions generated. Required: {num_questions}, Available: {len(filtered_questions)}")

        filtered_questions = filtered_questions[:num_questions]

        if not filtered_questions:
            raise ValueError("No questions were generated based on the provided criteria.")

        survey = Survey(
            title=f"Survey for {participant.display_name}",
            questions=filtered_questions,
            participant=participant
        )

        return survey


    class Config:
        arbitrary_types_allowed = True