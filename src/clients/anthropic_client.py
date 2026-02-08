import os
import time
from typing import List, Dict, Any
from .base import LLMClient, GenerationConfig

class AnthropicClient(LLMClient):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        # self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate(self, messages: List[Dict[str, str]], config: GenerationConfig) -> str:
        time.sleep(0.1)
        # Real impl:
        # response = self.client.messages.create(
        #     model="claude-3-opus-20240229",
        #     max_tokens=config.max_tokens,
        #     messages=messages
        # )
        # return response.content[0].text
        
        last_msg = messages[-1]["content"].lower()
        return f"Claude Response to: {messages[-1]['content'][:20]}..."

    def get_embedding(self, text: str) -> List[float]:
         # Anthropic doesn't describe an embedding endpoint in the same way, usually use Voyage or similar
         # Mocking for uniformity
        import random
        random.seed(hash(text))
        return [random.random() for _ in range(10)]
