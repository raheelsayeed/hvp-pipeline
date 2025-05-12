
from hvp.core.response import QuestionResponse
from ..core.participant import Participant, ParticipantType
from .base import LLM


class LLMParticipant(Participant):
    model: LLM

    def __init__(self, **data):
        super().__init__(**data)
        self.type = ParticipantType.LLM

    def send_prompt_to_llm(self, prompt: str) -> str:
        response = self.model.chat(
            system_prompt=self.instruction,
            user_prompt=prompt,
            temperature=0.7
        )
        return response
    

    
    def format_response(self, response) -> str:
        return self.model.format_response(response=response)
    
        

    


