from pydantic import BaseModel

from ..core.answeroption import AnswerSet
from ..core.survey import Survey
from ..core.question import Question
from ..core.response import QuestionResponse, SurveyResponse 

from ..core.participant import ParticipantType
from .llmparticipant import LLMParticipant


class LLMSurveyProcessor(BaseModel):

    survey: Survey

    def __init__(self, **data):
        super().__init__(**data)

        if self.survey.participant.type != ParticipantType.LLM:
            raise ValueError("Participant is not of type LLM.")
        

        
    def construct_prompt(self, question: Question, answer_set: AnswerSet) -> str:

        prompt = "## Question\n\n" 
        prompt += question.display_item(
            answer_set=answer_set,
            participant=self.survey.participant,
            omit_metadata=True
        )
        return prompt

    

    def run(self) -> SurveyResponse:
        
        responses = []
        for i, question in enumerate(self.survey.questions):
            for answer_set in question.answers:
                prompt = self.construct_prompt(question, answer_set)
                try:
                    response = self.survey.participant.send_prompt_to_llm(prompt)
                    response_dict = response.model_dump() 
                    print(f'>{i+1} Participant: {self.survey.participant.display_name}   AnswerSet_id:{answer_set.identifier} QuestionId: {question.identifier}')
                    response = QuestionResponse(
                        question_identifier=question.identifier,
                        answer_set_identifier=answer_set.identifier,
                        response=response_dict,
                        prompt=prompt
                    )
                    responses.append(response)
                except Exception as e:

                    print(f"Error processing question {question.identifier} with answer set {answer_set.identifier}: {e}")
                    responses.append(
                        QuestionResponse(
                                question_identifier=question.identifier,
                                answer_set_identifier=answer_set.identifier,
                                response=None,
                                prompt=prompt
                            )
                        )
            
                    
        return SurveyResponse(
            survey=self.survey,
            responses=responses
        )
            

