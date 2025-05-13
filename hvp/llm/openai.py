from datetime import time
import os
import asyncio
import logging
from typing import Optional, Dict, Any

import openai

from openai import AzureOpenAI, ChatCompletion


from .base import LLM

logger = logging.getLogger(__name__)

class GPT(LLM):

    @staticmethod
    def v4o():
        return GPT(model_name="gpt-4o", model_version="2024-02-15-preview") 
    
    def _setup(self) -> None:
        """Set up the OpenAI client."""
        self.api_key = self.api_key or os.environ.get("AZURE_OPENAI_API_KEY")
        self.api_endpoint = self.api_endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        if not self.api_endpoint:
            raise ValueError("OpenAI/Azure Endpoint is required")
        self.client = openai.AzureOpenAI(
            azure_deployment=self.model_name,
            api_version=self.model_version,
            azure_endpoint=self.api_endpoint
        )
        
    def format_response(self, response: dict) -> str: 
        """Format the response from OpenAI."""
        print(f'===>{response}')
        if 'choices' in response and len(response['choices']) > 0:
            if 'message' in response['choices'][0] and 'content' in response['choices'][0]['message']:
                return response['choices'][0]['message']['content']
            else:
                raise ValueError("Invalid response format from OpenAI.")
        else:
            raise ValueError("Invalid response format from OpenAI.")   
    
    def chat(self, 
             system_prompt: str, 
             user_prompt: str,
             temperature: Optional[float] = 0.7,
             max_tokens: Optional[int] = None) -> Any:
        """Synchronously get a chat response from OpenAI."""
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

                return response
                

            except Exception as e:
                raise e
                logger.warning(f"Attempt {attempt+1} failed: {str(e)}")

