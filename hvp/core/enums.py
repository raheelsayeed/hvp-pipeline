from enum import Enum, auto


class SubjectType(str, Enum):
    PATIENT = "patient"
    HEALTHCARE_PROVIDER = "healthcare provider"
    ETHICIST = "ethicist"
    POLICYMAKER = "policymaker"
    PUBLIC = "public"

class CountryEnum(str, Enum):
    India = "India"
    Israel = "Israel"
    UnitedStates = "United States"
    Other = "Other"

class GeoContext(str, Enum):
    RURAL = "rural"
    URBAN = "urban"
    SUBURBAN = "suburban"
    REMOTE = "remote (online)"

class ProviderTypeEnum(str, Enum):
    PHSICIAN = "Doctor"
    NURSE_PRACTITIONER = "Nurse Practitioner"
    PHYSICIAN_ASSISTANT = "Physician Assistant"
    Other = "Other"


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

class CountryEnum(str, Enum):
    India = "India"
    Israel = "Israel"
    UnitedStates = "United States"
    Other = "Other"