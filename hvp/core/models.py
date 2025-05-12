
from dataclasses import dataclass, field
from datetime import datetime
import re
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from pydantic import BaseModel
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
    



