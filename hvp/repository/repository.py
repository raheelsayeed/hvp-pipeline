from typing import Dict, List, Optional, Any, Set
import json
import os
from datetime import datetime
import uuid

from hvp.core.enums import SubjectType, ParticipantStatus
from .models import Participant, Organization

class ParticipantRepository:
    """Repository for storing and retrieving participant information."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        self.participants: Dict[str, Participant] = {}
        self.storage_dir = storage_dir
        if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
    
    def add_participant(self, participant: Participant) -> str:
        """
        Add a participant to the repository.
        
        Args:
            participant: The participant to add
            
        Returns:
            The participant's ID
        """
        # Generate ID if not present
        if not participant.participant_id:
            participant.participant_id = str(uuid.uuid4())
            
        self.participants[participant.participant_id] = participant
        self._save_participant(participant)
        return participant.participant_id
    
    def get_participant(self, participant_id: str) -> Optional[Participant]:
        """Get a participant by their ID."""
        if participant_id in self.participants:
            return self.participants[participant_id]
        
        # Try to load from storage
        loaded_participant = self._load_participant(participant_id)
        if loaded_participant:
            self.participants[participant_id] = loaded_participant
            return loaded_participant
            
        return None
    
    def update_participant(self, participant: Participant) -> bool:
        """Update an existing participant."""
        if participant.participant_id not in self.participants:
            return False
            
        self.participants[participant.participant_id] = participant
        self._save_participant(participant)
        return True
    
    def get_all_participants(self) -> List[Participant]:
        """Get all participants in the repository."""
        return list(self.participants.values())
    
    def get_by_subject_type(self, subject_type: SubjectType) -> List[Participant]:
        """Get all participants of a specific subject type."""
        return [
            participant for participant in self.participants.values()
            if participant.subject_type == subject_type
        ]
    
    def get_by_status(self, status: ParticipantStatus) -> List[Participant]:
        """Get all participants with a specific status."""
        return [
            participant for participant in self.participants.values()
            if participant.status == status
        ]
    
    def search(self, **kwargs) -> List[Participant]:
        """
        Search for participants matching specified criteria.
        
        Example:
            repo.search(country="US", age_min=30, age_max=50)
        """
        results = list(self.participants.values())
        
        # Filter by exact match attributes
        exact_match_attrs = ["country", "city", "subject_type", "status", "sex", "geo_context"]
        for attr in exact_match_attrs:
            if attr in kwargs:
                results = [p for p in results if getattr(p, attr, None) == kwargs[attr]]
                
        # Filter by age range
        if "age_min" in kwargs:
            results = [p for p in results if p.age and p.age >= kwargs["age_min"]]
            
        if "age_max" in kwargs:
            results = [p for p in results if p.age and p.age <= kwargs["age_max"]]
            
        # Filter by tags
        if "tag" in kwargs:
            results = [p for p in results if kwargs["tag"] in p.tags]
            
        # Filter by organization
        if "organization_id" in kwargs:
            results = [
                p for p in results 
                if p.organization and p.organization.canonical_id == kwargs["organization_id"]
            ]
            
        return results
    
    def get_demographics_summary(self) -> Dict[str, Any]:
        """Get a summary of participant demographics."""
        summary = {
            "total": len(self.participants),
            "by_subject_type": {},
            "by_country": {},
            "by_status": {},
            "age_stats": {
                "min": None,
                "max": None,
                "avg": None
            }
        }
        
        # Skip if no participants
        if not self.participants:
            return summary
            
        # Count by subject type
        for subject_type in SubjectType:
            count = len([p for p in self.participants.values() if p.subject_type == subject_type])
            if count > 0:
                summary["by_subject_type"][subject_type.value] = count
                
        # Count by country
        countries = {}
        for p in self.participants.values():
            if p.country:
                countries[p.country] = countries.get(p.country, 0) + 1
        summary["by_country"] = countries
        
        # Count by status
        for status in ParticipantStatus:
            count = len([p for p in self.participants.values() if p.status == status])
            if count > 0:
                summary["by_status"][status.value] = count
                
        # Calculate age statistics
        ages = [p.age for p in self.participants.values() if p.age is not None]
        if ages:
            summary["age_stats"]["min"] = min(ages)
            summary["age_stats"]["max"] = max(ages)
            summary["age_stats"]["avg"] = sum(ages) / len(ages)
            
        return summary
    
    def _save_participant(self, participant: Participant) -> None:
        """Save a participant to persistent storage."""
        if not self.storage_dir:
            return
            
        file_path = os.path.join(self.storage_dir, f"{participant.participant_id}.json")
        
        # Convert to dict for serialization
        participant_dict = participant.to_dict()
        
        # Add additional fields that may not be in to_dict
        if participant.llm_persona:
            participant_dict["llm_persona"] = participant.llm_persona
        
        if participant.tags:
            participant_dict["tags"] = participant.tags
            
        if participant.metadata:
            participant_dict["metadata"] = participant.metadata
            
        with open(file_path, "w") as f:
            json.dump(participant_dict, f, indent=2)
    
    def _load_participant(self, participant_id: str) -> Optional[Participant]:
        """Load a participant from persistent storage."""
        if not self.storage_dir:
            return None
            
        file_path = os.path.join(self.storage_dir, f"{participant_id}.json")
        
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                
            # Create participant from data
            from hvp.core.enums import SubjectType, ParticipantStatus, GeoContext
            
            # Build optional organization if it exists
            org = None
            if "organization" in data:
                org_data = data["organization"]
                org = Organization(
                    name=org_data["name"],
                    canonical_id=org_data["canonical_id"],
                    contact_email=org_data.get("contact_email"),
                    country=org_data.get("country")
                )
            
            participant = Participant(
                participant_id=data["participant_id"],
                subject_type=SubjectType(data["subject_type"]),
                name=data.get("name", ""),
                age=data.get("age"),
                sex=data.get("sex"),
                country=data.get("country"),
                city=data.get("city"),
                geo_context=GeoContext(data["geo_context"]) if "geo_context" in data else None,
                preferred_language=data.get("preferred_language", "en"),
                llm_persona=data.get("llm_persona", ""),
                organization=org,
                status=ParticipantStatus(data["status"]),
                enrollment_date=datetime.fromisoformat(data["enrollment_date"]),
                completed_surveys=data.get("completed_surveys", []),
                tags=data.get("tags", []),
                contact_email=data.get("contact_email"),
                metadata=data.get("metadata", {})
            )
            
            if "last_activity_date" in data:
                participant.last_activity_date = datetime.fromisoformat(data["last_activity_date"])
                
            return participant
                
        except Exception as e:
            print(f"Error loading participant {participant_id}: {e}")
            return None