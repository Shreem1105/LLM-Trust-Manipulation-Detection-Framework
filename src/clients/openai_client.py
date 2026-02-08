import os
import time
import json
from typing import List, Dict, Any
from .base import LLMClient, GenerationConfig

class OpenAIClient(LLMClient):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        # In production this would use `openai.OpenAI` client
        # self.client = OpenAI(api_key=self.api_key)

    def generate(self, messages: List[Dict[str, str]], config: GenerationConfig) -> str:
        # Simulate network delay
        time.sleep(0.1)
        
        # Mock Response Logic for "Real" Integration Phase
        # In a real deployment, replace with:
        # response = self.client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=messages,
        #     temperature=config.temperature,
        #     max_tokens=config.max_tokens
        # )
        # return response.choices[0].message.content

        # For the purpose of the "Real Integration" prototype without burning credits:
        last_msg = messages[-1]["content"].lower()
        if "napalm" in last_msg or "bomb" in last_msg:
             return "I cannot assist with that request."
        return f"OpenAI Response to: {messages[-1]['content'][:20]}..."

    def get_embedding(self, text: str) -> List[float]:
        # Mock embedding
        # In real deployment: client.embeddings.create(input=text, model="text-embedding-3-small")
        import random
        random.seed(hash(text))
        return [random.random() for _ in range(10)]
