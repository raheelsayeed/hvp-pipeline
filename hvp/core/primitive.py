from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Type, TypeVar
from pydantic import BaseModel, Field 
import importlib.resources as pkg_resources
import json, uuid
from pathlib import Path
import os, logging

log = logging.getLogger(__name__)

class PrimitiveType(BaseModel):
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    language: str = "en"  # Default language set to English
    version: str = "1.0"

class Identifiable(PrimitiveType):
    identifier: str

class IdentifiableUUID(PrimitiveType):
    identifier: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date_created: datetime = Field(default_factory=datetime.now)
    date_modified: Optional[datetime] = None


    
# Function to load JSON data from package resources

def load_json_from_package(file_name):
    with pkg_resources.open_text('hvp.presets', file_name) as file:
        data = json.load(file)
        log.debug(f"Loaded data from {file_name}: {data}")  # Debugging output
        return data

# Decorator to add a from_json class method
def add_from_json_method(model_cls, file_name):
    def from_json(cls):
        data = load_json_from_package(file_name)
        for item in data:
            member_name = item["name"].upper()
            instance = model_cls(**item)
            if member_name not in cls.__members__:
                setattr(cls, member_name, instance)
                log.debug(f"Added {member_name} to {cls.__name__}")  # Debugging output

    def decorator(cls):
        setattr(cls, 'from_json', classmethod(from_json))
        cls.from_json()
        return cls

    return decorator