import logging
from groq import Groq
from cerebras.cloud.sdk import Cerebras
from backend.config import settings

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.groq_key = settings.GROQ_API_KEY
        self.cerebras_key = settings.CEREBRAS_API_KEY
        
        self.groq_client = None
        self.cerebras_client = None
        
        if self.groq_key:
            try:
                self.groq_client = Groq(api_key=self.groq_key)
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                
        if self.cerebras_key:
            try:
                self.cerebras_client = Cerebras(api_key=self.cerebras_key)
            except Exception as e:
                logger.error(f"Failed to initialize Cerebras client: {e}")

    def generate(self, messages: list, temperature: float = None, response_format: dict = None) -> str:
        temp = temperature if temperature is not None else settings.TEMPERATURE
        
        # Try Groq (Primary)
        if self.groq_client:
            try:
                model = settings.DEFAULT_MODEL or "llama-3.3-70b-versatile"
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "temperature": temp,
                }
                if response_format:
                    kwargs["response_format"] = response_format
                
                response = self.groq_client.chat.completions.create(**kwargs)
                if response.choices and len(response.choices) > 0:
                    return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"Groq API call failed, falling back to Cerebras. Error: {e}")
                
        # Try Cerebras (Fallback)
        if self.cerebras_client:
            try:
                # Cerebras uses "llama3.3-70b" or "llama3.1-70b"
                model = "llama3.3-70b"
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "temperature": temp,
                }
                # Cerebras SDK might not support all response_format styles, so if it fails, try without it
                if response_format:
                    try:
                        kwargs["response_format"] = response_format
                        response = self.cerebras_client.chat.completions.create(**kwargs)
                    except Exception as json_err:
                        logger.warning(f"Cerebras call with response_format failed ({json_err}). Retrying without response_format.")
                        kwargs.pop("response_format", None)
                        response = self.cerebras_client.chat.completions.create(**kwargs)
                else:
                    response = self.cerebras_client.chat.completions.create(**kwargs)
                
                if response.choices and len(response.choices) > 0:
                    return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Cerebras API call failed as well. Error: {e}")
                raise RuntimeError(f"All LLM providers failed. Last error: {e}")
                
        raise RuntimeError("No LLM client is configured or available.")

# Global client instance
llm_client = LLMClient()
