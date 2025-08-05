from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator, validator, ValidationError
import uuid
from .response import ResponseRecord

from hvp.core.enums import * 


class Participant(BaseModel):
    
    email: str
    first_name: str
    last_name: str
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None 
    race_ethnicity: Optional[str] = None 
    profession: Optional[str] = None 
    instruction: Optional[str] = None
    geo_context: Optional[GeoContext] = None
    healthcare_system: Optional[HealthcareSystem] = None
    lat: Optional[int] = None 
    long: Optional[int] = None 
    country: Optional[str] = None 
    city: Optional[str] = None
    responses: list[ResponseRecord] = None
    status: ParticipantStatus = ParticipantStatus.ACTIVE
    subject_type: Optional[SubjectType] = None 
    provider_type: Optional[ProviderTypeEnum] = None
    geo_context: Optional[GeoContext] = None
    clinical_field: Optional[list[str]] = None
    career_stage: Optional[str] = None 
    academic_teaching_affiliation: Optional[bool] = None
    graduation_year: Optional[int] = None 
    practice_setting: Optional[str] = None 

    @property 
    def identifier(self) -> str:
        return self.email

    @model_validator(mode="after")
    def check_human_requirements(self):
        if self.email is None:
            raise ValueError("Email is required for human participants.")
        return self
    
    @model_validator(mode="before")
    def _coerce_inputs(cls, data: dict) -> dict:

        for coord in ("lat", "long"):
            v = data.get(coord)
            if isinstance(v, str):
                try:
                    data[coord] = int(float(v))
                except ValueError:
                    data[coord] = None
        return data
    
    @property
    def display_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property 
    def format_response(self, response) -> str:
        pass

    
