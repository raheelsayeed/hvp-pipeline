from enum import Enum, auto


class SubjectType(str, Enum):
    HEALTHCARE_PROVIDER = "healthcare provider"
    PATIENT = "patient"
    ETHICIST = "ethicist"
    POLICYMAKER = "policymaker"
    PUBLIC = "public"

class CountryEnum(str, Enum):
    India = "India"
    Israel = "Israel"
    UnitedStates = "United States"
    Other = "Other"

class ClinicalField(str, Enum):
    PRIMARY_CARE = "Primary Care"
    EMERGENCY_MEDICINE = "Emergency Medicine"
    INTERNAL_MEDICINE = "Internal Medicine"
    CARDIOLOGY = "Cardiology"
    ONCOLOGY = "Oncology"
    NEUROLOGY = "Neurology"
    PEDIATRICS = "Pediatrics"
    GERIATRICS = "Geriatrics"
    PSYCHIATRY = "Psychiatry"
    OBSTETRICS_GYNECOLOGY = "Obstetrics/Gynecology"
    TRANSPLANT = "Transplant" 
    RARE_DISEASES = "Rare diseases"
    ENDOCRINOLOGY = "Endocrinology"


class GeoContext(str, Enum):
    RURAL = "rural"
    URBAN = "urban"
    SUBURBAN = "suburban"   
    TELEMEDICINE = "telemedicine"

class ProviderTypeEnum(str, Enum):
    PHYSICIAN = "Doctor"
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