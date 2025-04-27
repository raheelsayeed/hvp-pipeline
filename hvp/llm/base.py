from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import logging
import time
import uuid

logger = logging.getLogger(__name__)

@dataclass
class PromptTemplate:
    template: str
    variables: Dict[str, str] = field(default_factory=dict)
    
    def format(self, **kwargs) -> str:
        """Format the template with the given variables."""
        variables = {**self.variables, **kwargs}
        return self.template.format(**variables)

@dataclass
class LLMResponse:
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def cost(self) -> float:
        """Calculate estimated cost based on token usage."""
        # Implementation depends on model pricing
        return 0.0

class LLM(ABC):
    def __init__(self, 
                 model_name: str, 
                 model_version: str,
                 api_key: Optional[str] = None,
                 api_endpoint: str = None,
                 retry_count: int = 3,
                 retry_delay: float = 1.0,
                 timeout: float = 30.0):
        self.model_name = model_name
        self.api_key = api_key
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.model_version = model_version
        self.api_endpoint = api_endpoint
        self._setup()
    
    @abstractmethod
    def _setup(self) -> None:
        """Set up the LLM client."""
        pass
    
    @abstractmethod
    async def chat_async(self, 
                   system_prompt: str, 
                   user_prompt: str, 
                   temperature: float = 0.7,
                   max_tokens: Optional[int] = None) -> LLMResponse:
        """Asynchronously get a chat response from the LLM."""
        pass
    
    def chat(self, 
             system_prompt: str, 
             user_prompt: str, 
             temperature: float = 0.7,
             max_tokens: Optional[int] = None) -> LLMResponse:
        """Synchronously get a chat response from the LLM."""
        pass
    
    async def batch_process(self, 
                      prompts: List[Dict[str, str]], 
                      **kwargs) -> List[LLMResponse]:
        """Process a batch of prompts efficiently."""
        results = []
        for prompt in prompts:
            system = prompt.get("system", "")
            user = prompt.get("user", "")
            try:
                response = await self.chat_async(system, user, **kwargs)
                results.append(response)
            except Exception as e:
                logger.error(f"Error processing prompt: {e}")
                # Add a placeholder for failed requests
                results.append(None)
        return results