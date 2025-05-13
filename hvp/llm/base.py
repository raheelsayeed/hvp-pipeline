from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional
from pydantic import BaseModel, Field
import logging

from hvp.core.response import QuestionResponse


logger = logging.getLogger(__name__)

class LLM(BaseModel, ABC):
    model_name: str
    model_version: str
    api_key: Optional[str] = Field(None, exclude=True)
    api_endpoint: Optional[str] = None
    retry_count: int = 3
    retry_delay: float = 1.0
    timeout: float = 30.0
    client: Optional[Any] = Field(None, exclude=True)
    temperature: float = 0.7

    def __init__(self, **data):
        super().__init__(**data)
        self._setup()

    @abstractmethod
    def _setup(self) -> None:
        """Set up the LLM client."""
        pass

    @abstractmethod
    def format_response(self, response) -> str:
        """Format the response from the LLM."""
        pass
    
    def chat(self, 
             system_prompt: str, 
             user_prompt: str, 
             max_tokens: Optional[int] = None) -> QuestionResponse:
        """Synchronously get a chat response from the LLM."""
        pass
    

    class Config:
        arbitrary_types_allowed = True