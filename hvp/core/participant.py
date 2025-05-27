from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator, validator, ValidationError
import uuid

# Define the ParticipantType Enum
class ParticipantType(Enum):
    HUMAN = "Human"
    LLM = "LLM"

class Participant(BaseModel):
    
    email: str
    first_name: str
    last_name: str
    name: Optional[str] = None
    type: ParticipantType = ParticipantType.HUMAN
    age: Optional[int] = None
    gender: Optional[str] = None 
    race_ethnicity: Optional[str] = None 
    profession: Optional[str] = None 
    instruction: Optional[str] = None
    geo_context: Optional[GeoContext] = None
    healthcare_system: Optional[HealthcareSystem] = None 
    status: ParticipantStatus = ParticipantStatus.ACTIVE

    @property 
    def identifier(self) -> str:
        return self.email

    @model_validator(mode="after")
    def check_human_requirements(self):
        if self.type == ParticipantType.HUMAN:
            # if self.age is None:
            #     raise ValueError("Age is required for human participants.")
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

    @property
    def survey_filename(self, serial_num: int = None) -> str:
        return f"survey_{self.email}.json"
    
    @property
    def response_filename(self, serial_num: int = None) -> str:
        return f"response_{self.email}.json"
    
