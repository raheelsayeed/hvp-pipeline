import os
import time
import asyncio
import logging
from typing import Optional, Dict, Any

import openai
from openai import AzureOpenAI, AsyncAzureOpenAI

from .base import LLM, LLMResponse

logger = logging.getLogger(__name__)

class AzureOpenAILLM(LLM):
    """Azure OpenAI LLM implementation."""

    @staticmethod 
    def GPT4o(): 
        # Azure OpenAI
        return AzureOpenAILLM(
            model_name="gpt-4o",
        )
    
    def __init__(self, 
                 model_name: str,
                 api_key: Optional[str] = None,
                 endpoint: Optional[str] = "https://azure-ai-dev.hms.edu",
                 api_version: str = "2024-02-15-preview",
                 retry_count: int = 3,
                 retry_delay: float = 1.0,
                 timeout: float = 30.0):
        self.model_name = model_name
        self.api_key = api_key
        self.endpoint = endpoint
        self.api_version = api_version
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.timeout = timeout
        self._setup()
    
    def _setup(self) -> None:
        """Set up the Azure OpenAI client."""
        self.api_key = self.api_key or os.environ.get("AZURE_OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Azure OpenAI API key is required")
        
        self.endpoint = self.endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT")
        if not self.endpoint:
            raise ValueError("Azure OpenAI endpoint is required")
        
        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )
        
        self.async_client = AsyncAzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )
        
        logger.info(f"Azure OpenAI client initialized with model: {self.model_name}")
    
    async def chat_async(self, 
                   system_prompt: str, 
                   user_prompt: str, 
                   temperature: float = 0.7,
                   max_tokens: Optional[int] = None) -> LLMResponse:
        """Asynchronously get a chat response from Azure OpenAI."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        for attempt in range(self.retry_count):
            try:
                response = await self.async_client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=self.timeout
                )
                
                return LLMResponse(
                    content=response.choices[0].message.content,
                    model=self.model_name,
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                    request_id=response.id,
                    metadata={
                        "finish_reason": response.choices[0].finish_reason,
                        "provider": "azure",
                        "endpoint": self.endpoint.split("https://")[1].split(".")[0] if self.endpoint else None
                    }
                )
            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed: {str(e)}")
                if attempt < self.retry_count - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"All attempts failed: {str(e)}")
                    raise
    
    def chat(self, 
             system_prompt: str, 
             user_prompt: str, 
             temperature: float = 0.7,
             max_tokens: Optional[int] = None) -> LLMResponse:
        """Synchronously get a chat response from Azure OpenAI."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        for attempt in range(self.retry_count):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=self.timeout
                )
                
                return LLMResponse(
                    content=response.choices[0].message.content,
                    model=self.model_name,
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                    request_id=response.id,
                    metadata={
                        "finish_reason": response.choices[0].finish_reason,
                        "provider": "azure",
                        "endpoint": self.endpoint.split("https://")[1].split(".")[0] if self.endpoint else None
                    }
                )
            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed: {str(e)}")
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"All attempts failed: {str(e)}")
                    raise

    def get_deployment_info(self) -> Dict[str, Any]:
        """Get information about the Azure OpenAI deployment."""
        try:
            # This would typically be an API call to get deployment info
            # Since Azure OpenAI client doesn't have a direct method for this,
            # we'll return what we know
            return {
                "provider": "Azure OpenAI",
                "model": self.model_name,
                "endpoint": self.endpoint,
                "api_version": self.api_version
            }
        except Exception as e:
            logger.error(f"Error getting deployment info: {str(e)}")
            return {
                "provider": "Azure OpenAI",
                "model": self.model_name,
                "error": str(e)
            }