
from dataclasses import dataclass, field
from datetime import datetime
import re
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from .enums import *

@dataclass
class Organization:
    name: str
    identifier: str
    contact_email: str
    contact_name: Optional[str] = None
    country: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"{self.name} ({self.identifier})"
    


@dataclass
class Participant:
    """
    Represents a participant in the Human Values Project study.
    Contains demographic information and LLM persona for simulation.
    """
    participant_id: str
    subject_type: SubjectType
    name: str = ""  # Can be empty for anonymized data
    age: Optional[int] = None
    sex: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    geo_context: Optional[GeoContext] = None
    preferred_language: str = "en"
    llm_persona: str = ""  # Description to feed into LLM for persona simulation
    organization: Optional[Organization] = None
    status: ParticipantStatus = ParticipantStatus.ENROLLED
    enrollment_date: datetime = field(default_factory=datetime.now)
    last_activity_date: Optional[datetime] = None
    completed_surveys: List[str] = field(default_factory=list)  # List of survey_ids
    tags: List[str] = field(default_factory=list)
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize additional fields after dataclass initialization."""
        if not self.participant_id:
            self.participant_id = str(uuid.uuid4())
            
        # Create a default LLM persona if none provided
        if not self.llm_persona:
            self._generate_default_persona()
    
    def _generate_default_persona(self) -> None:
        """Generate a default LLM persona based on participant attributes."""
        persona_parts = []
        
        if self.subject_type == SubjectType.CLINICIAN:
            persona_parts.append("a healthcare professional")
            if "specialty" in self.metadata:
                persona_parts.append(f"specializing in {self.metadata['specialty']}")
        elif self.subject_type == SubjectType.PATIENT:
            persona_parts.append("a patient")
            if "condition" in self.metadata:
                persona_parts.append(f"with {self.metadata['condition']}")
        elif self.subject_type == SubjectType.ETHICIST:
            persona_parts.append("a healthcare ethicist")
        elif self.subject_type == SubjectType.POLICYMAKER:
            persona_parts.append("a healthcare policy professional")
        else:
            persona_parts.append("a member of the general public")
            
        if self.age:
            if self.age < 30:
                persona_parts.append("in their twenties")
            elif self.age < 40:
                persona_parts.append("in their thirties")
            elif self.age < 50:
                persona_parts.append("in their forties")
            elif self.age < 60:
                persona_parts.append("in their fifties")
            else:
                persona_parts.append("who is 60+ years old")
                
        if self.country:
            persona_parts.append(f"from {self.country}")
        
        if self.geo_context:
            persona_parts.append(f"in a {self.geo_context.value} setting")
            
        self.llm_persona = " ".join(persona_parts)
    
    def update_status(self, new_status: ParticipantStatus) -> None:
        """Update the participant's status."""
        self.status = new_status
        self.last_activity_date = datetime.now()
    
    def add_completed_survey(self, survey_id: str) -> None:
        """Mark a survey as completed by this participant."""
        if survey_id not in self.completed_surveys:
            self.completed_surveys.append(survey_id)
            self.last_activity_date = datetime.now()
    
    def has_completed_survey(self, survey_id: str) -> bool:
        """Check if the participant has completed a specific survey."""
        return survey_id in self.completed_surveys
    
    def get_completion_rate(self) -> float:
        """Calculate the percentage of assigned surveys that have been completed."""
        total_assigned = self.metadata.get("assigned_survey_count", 0)
        if total_assigned == 0:
            return 0.0
        return len(self.completed_surveys) / total_assigned * 100
    
    def is_active(self) -> bool:
        """Check if the participant is currently active."""
        return self.status == ParticipantStatus.ACTIVE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert participant data to dictionary for serialization."""
        result = {
            "participant_id": self.participant_id,
            "subject_type": self.subject_type.value,
            "name": self.name,
            "country": self.country,
            "city": self.city,
            "preferred_language": self.preferred_language,
            "status": self.status.value,
            "enrollment_date": self.enrollment_date.isoformat(),
            "completed_surveys": self.completed_surveys,
        }
        
        # Add optional fields if they exist
        if self.age:
            result["age"] = self.age
        if self.sex:
            result["sex"] = self.sex
        if self.geo_context:
            result["geo_context"] = self.geo_context.value
        if self.organization:
            result["organization"] = {
                "name": self.organization.name,
                "canonical_id": self.organization.canonical_id
            }
        if self.last_activity_date:
            result["last_activity_date"] = self.last_activity_date.isoformat()
        if self.contact_email:
            result["contact_email"] = self.contact_email
        
        return result
    
    def get_demographics_summary(self) -> str:
        """Get a human-readable summary of participant demographics."""
        parts = []
        
        parts.append(f"Type: {self.subject_type.value.capitalize()}")
        
        if self.age:
            parts.append(f"Age: {self.age}")
        
        if self.sex:
            parts.append(f"Sex: {self.sex}")
            
        if self.country:
            location = self.country
            if self.city:
                location = f"{self.city}, {self.country}"
            parts.append(f"Location: {location}")
            
        if self.organization and self.organization.name:
            parts.append(f"Organization: {self.organization.name}")
            
        return ", ".join(parts)
    
    @property
    def short_id(self) -> str:
        """Get a shortened ID for display purposes."""
        return self.participant_id[:8] if self.participant_id else ""
    

@dataclass
class Patient:
    """Represents a patient case with relevant clinical information."""
    description: str
    age: Optional[int] = None
    sex: Optional[str] = None
    conditions: List[str] = field(default_factory=list)
    medications: List[str] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)
    vital_signs: Dict[str, Any] = field(default_factory=dict)
    labs: Dict[str, Any] = field(default_factory=dict)
    urgency_factors: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Extract structured data from description if not explicitly provided."""
        if self.description and (not self.age or not self.sex or not self.conditions):
            self._parse_description()
    
    def _parse_description(self):
        """Parse the patient description to extract structured data."""
        # Extract age and sex
        age_sex_pattern = r"(\d+)[\s-]*(?:year|y)[- ]*old\s+((?:fe)?male)"
        age_sex_match = re.search(age_sex_pattern, self.description, re.IGNORECASE)
        if age_sex_match:
            if not self.age:
                try:
                    self.age = int(age_sex_match.group(1))
                except ValueError:
                    pass
            if not self.sex:
                self.sex = age_sex_match.group(2).lower()
        
        # Extract conditions (simple pattern matching)
        condition_keywords = [
            "diabetes", "hypertension", "asthma", "COPD", "heart failure",
            "depression", "anxiety", "cancer", "arthritis", "obesity"
        ]
        for condition in condition_keywords:
            if re.search(r"\b" + condition + r"\b", self.description, re.IGNORECASE):
                if condition not in self.conditions:
                    self.conditions.append(condition)
    
    def get_summary(self) -> str:
        """Generate a concise summary of the patient."""
        parts = []
        
        # Add demographics
        demo = []
        if self.age:
            demo.append(f"{self.age}y/o")
        if self.sex:
            demo.append(self.sex)
        if demo:
            parts.append(" ".join(demo))
        
        # Add conditions
        if self.conditions:
            parts.append(f"Conditions: {', '.join(self.conditions)}")
        
        # Add medications if present
        if self.medications:
            parts.append(f"Meds: {', '.join(self.medications[:3])}" + 
                         (f" + {len(self.medications) - 3} more" if len(self.medications) > 3 else ""))
        
        # Add key findings
        if self.findings:
            parts.append(f"Findings: {', '.join(self.findings[:2])}" +
                         (f" + {len(self.findings) - 2} more" if len(self.findings) > 2 else ""))
        
        # Add vital signs if abnormal
        abnormal_vitals = []
        for key, value in self.vital_signs.items():
            # Simple thresholds for demonstration
            if (key == "BP systolic" and (value > 140 or value < 90)) or \
               (key == "BP diastolic" and (value > 90 or value < 60)) or \
               (key == "HR" and (value > 100 or value < 60)) or \
               (key == "Temp" and value > 38.0) or \
               (key == "O2" and value < 95):
                abnormal_vitals.append(f"{key}={value}")
                
        if abnormal_vitals:
            parts.append(f"Vitals: {', '.join(abnormal_vitals)}")
            
        return " | ".join(parts)