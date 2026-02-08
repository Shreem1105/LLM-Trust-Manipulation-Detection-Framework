from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class GenerationConfig:
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 1.0

class LLMClient(ABC):
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], config: GenerationConfig) -> str:
        """
        Generates a response from the LLM.
        messages: [{"role": "user", "content": "..."}]
        """
        pass

    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """
        Returns the vector embedding for the text.
        """
        pass
