from enum import Enum, auto

class SubjectType(Enum):
    PATIENT = "patient"
    CLINICIAN = "clinician"
    ETHICIST = "ethicist"
    POLICYMAKER = "policymaker"
    PUBLIC = "public"

class SurveyType(Enum):
    CHOICE = "discrete_choice"
    OPEN_CHOICE = "open_choice"
    RANKING = "ranking"
    SCENARIO = "scenario_based"

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

class QuestionType(Enum):
    DISCRETE_CHOICE = "discrete_choice"
    RANKING = "ranking"
    OPEN_ENDED = "open_ended"
    LIKERT = "likert"
    SCENARIO = "scenario"

class ResponseQuality(Enum):
    VALID = "valid"
    SUSPECT = "suspect"
    INVALID = "invalid"
    INCOMPLETE = "incomplete"