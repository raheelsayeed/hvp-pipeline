from typing import Optional
import boto3, logging, os, json
from botocore.exceptions import ClientError
from .base import LLM
from pydantic import create_model, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Claude(LLM):



    # max tokens = 200k
    @staticmethod
    def v37():
        model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
        anthropic_version = "bedrock-2023-05-31"
        return Claude(model_name=model_id, model_version=anthropic_version)
    
    def _setup(self) -> None:
        session = boto3.Session(profile_name=os.environ.get("AWS_LOGIN_PROFILE_NAME"))
        self.client = session.client("bedrock-runtime", region_name="us-east-2")
    

    def format_response(self, response: dict) -> str:
        content = response.get('content')
        if content:
            return content[0]['text']
        else:
            return None

    def chat(self,
             system_prompt: str,
             user_prompt: str,
             temperature: Optional[float] = 0.7,
             max_tokens: Optional[int] = 300) -> dict:


        body=json.dumps({
            "anthropic_version": self.model_version,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_prompt,  # System prompt here
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        })

        try:
            response = self.client.invoke_model(
                modelId=self.model_name,
                body=body,
                contentType="application/json",
                accept="application/json",
            )
            
            response_dict = json.loads(response['body'].read())

            return Claude.dict_to_model(response_dict)
        
        except ClientError as e:
            raise e