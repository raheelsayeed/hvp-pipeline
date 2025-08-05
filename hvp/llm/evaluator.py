from pydantic import BaseModel

from ..core.answeroption import AnswerSet

from ..core.question import Question
from ..core.response import ResponseRecord
from .base import LLM

class LLMEval(BaseModel):
    questions: list[Question]
    llm: LLM
    
    def construct_prompt(self, question: Question, answer_set: AnswerSet) -> str:
        prompt = "## Question\n\n" 
        prompt += question.display_item(
            answer_set=answer_set,
            participant=self.llm,
            omit_metadata=True
        )
        return prompt
    
    def run(self):
        responses = [] 
        errors = [] 
        for i, question in enumerate(self.questions): 
            for answer_set in question.answers: 
                prompt = self.construct_prompt(question, answer_set) 
                print(prompt)
                try: 
                    response = self.llm.chat(prompt=prompt)
                    response_dict = response.model_dump()
                    responses.append(response_dict)
                    print(i, response_dict)
                except Exception as e: 
                    print('error', i)

                    errors.append((question.identifier, answer_set.identifier, e))

        return (responses, errors)  



