from pydantic import BaseModel

class PatientVignettes(BaseModel):
    identifier: str
    description: str