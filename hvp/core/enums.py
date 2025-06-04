from enum import Enum, auto

class SubjectType(Enum):
    PATIENT = "patient"
    CLINICIAN = "clinician"
    ETHICIST = "ethicist"
    POLICYMAKER = "policymaker"
    PUBLIC = "public"

class GeoContext(Enum):
    RURAL = "rural"
    URBAN = "urban"
    SUBURBAN = "suburban"
    REMOTE = "remote"

class HealthcareSystem(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    QUATERNARY = "quaternary"

class ParticipantStatus(Enum):
    ENROLLED = "enrolled"
    ACTIVE = "active"
    COMPLETED = "completed"
    WITHDRAWN = "withdrawn"
    EXCLUDED = "excluded"


