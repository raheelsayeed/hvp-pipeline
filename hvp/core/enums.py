from enum import Enum, auto

class SubjectType(str, Enum):
    HEALTHCARE_PROVIDER = "healthcare provider"
    PATIENT = "patient"
    ETHICIST = "ethicist"
    POLICYMAKER = "policymaker"
    PUBLIC = "public"

class GeoContext(str, Enum):
    RURAL = "rural"
    URBAN = "urban"
    SUBURBAN = "suburban"   
    TELEMEDICINE = "telemedicine"

class ProviderTypeEnum(str, Enum):
    PHYSICIAN = "Doctor"
    NURSE_PRACTITIONER = "Nurse Practitioner"
    PHYSICIAN_ASSISTANT = "Physician Assistant"

class HealthcareSystem(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    QUATERNARY = "quaternary"


class ParticipantStatus(str, Enum):
    ENROLLED = "enrolled"
    ACTIVE = "active"
    COMPLETED = "completed"
    WITHDRAWN = "withdrawn"
    EXCLUDED = "excluded"