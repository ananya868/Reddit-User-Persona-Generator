import os, json 
from dotenv import load_dotenv

from pydantic import BaseModel
from typing import Type, List, Dict, Any

import litellm
load_dotenv()


class LLMClient:
    """
    A client for interacting with a large language model using litellm.
    
    This client supports both standard text generation and structured output
    that conforms to a Pydantic schema.
    
    The model is configured via the 'LLM_MODEL' environment variable.
    API keys (e.g., OPENAI_API_KEY) must also be set in the .env file.
    """
    def __init__(self): 
        """Initializes the LLM client and loads the model configuration."""
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini") # Default to gpt-4o-mini 
        print(f"INFO: LLMClient initialized with model: {self.model}")

    def generate_response(self, prompt: str, temperature: float = 0.2, max_tokens: int = 2048, verbose: bool = False) -> str | None:
        """
        Gets a standard text response from the LLM.

        :param prompt: The text prompt to send to the LLM.
        :param temperature: Controls the randomness of the output.
        :param max_tokens: The maximum number of tokens to generate.
        :return: The generated text response or None if an error occurs.
        """
        messages = [{"role": "user", "content": prompt}]
        
        try:
            if verbose:
                print(f"INFO: Sending text prompt to LLM ({self.model})...")
            response = litellm.completion(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content
            return content.strip()
        except Exception as e:
            print(f"ERROR: An error occurred while getting text response from LLM: {e}")
            return None

    def generate_structured_response(self, prompt: str, pydantic_schema: BaseModel, verbose: bool = False) -> BaseModel | None:
        """
        Gets a structured JSON response from the LLM that conforms to a Pydantic schema.

        :param prompt: The text prompt to send to the LLM.
        :param pydantic_schema: The Pydantic schema class to validate the response.
        :param verbose: If True, print additional information.
        :return: An instance of the Pydantic schema with the structured content or None if an error occurs.
        """
        messages = [{"role": "user", "content": prompt}]
        
        try:
            if verbose:
                print(f"INFO: Sending structured prompt to LLM ({self.model})...")
            response = litellm.completion(
                model=self.model,
                messages=messages,
                response_format=pydantic_schema
            )
            response_data = response.choices[0].message.content
            if response_data: 
                structured_response = json.loads(response_data)
                return structured_response 
        except Exception as e:
            print(f"ERROR: An error occurred while getting structured response from LLM: {e}")
            return None
