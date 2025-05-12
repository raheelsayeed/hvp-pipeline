from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator, validator, ValidationError
import uuid



# Define the ParticipantType Enum
class ParticipantType(Enum):
    HUMAN = "Human"
    LLM = "LLM"

class Participant(BaseModel):
    identifier: str = Field(default_factory=lambda: str(uuid.uuid4()))
    first_name: str
    last_name: str
    type: ParticipantType
    age: Optional[int] = None
    email: Optional[str] = None
    instruction: Optional[str] = None

    @model_validator(mode="after")
    def check_human_requirements(self):
        if self.type == ParticipantType.HUMAN:
            if self.age is None:
                raise ValueError("Age is required for human participants.")
            if self.email is None:
                raise ValueError("Email is required for human participants.")
        return self



    def __post_init__(self):
        # Initialize default instructions based on participant type
        if self.type == ParticipantType.HUMAN:
            self.instruction = "Please read the survey carefully and answer all questions to the best of your ability."
        elif self.type == ParticipantType.LLM:
            self.instruction = "Please generate responses based on the input data and available context."

    @property
    def display_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property 
    def format_response(self, response) -> str:
        pass


    
