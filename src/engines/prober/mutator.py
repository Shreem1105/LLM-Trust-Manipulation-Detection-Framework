import random
import string

class PromptMutator:
    """
    Evolves prompts to bypass safety filters using various strategies.
    In a full production system, this would use a 'Red Team LLM' to rewrite prompts.
    """
    
    def mutate(self, text: str, strategy: str = "random_noise") -> str:
        if strategy == "random_noise":
            return self._inject_noise(text)
        elif strategy == "payload_splitting":
            return self._split_payload(text)
        elif strategy == "identity_masking":
             return self._mask_identity(text)
        else:
            return text

    def _inject_noise(self, text: str) -> str:
        """Injects random zero-width spaces or invisible characters."""
        # Simple simulation: add a random char suffix
        noise = "".join(random.choices(string.ascii_letters, k=3))
        return f"{text} [{noise}]"

    def _split_payload(self, text: str) -> str:
        """Splits sensitive words to break keyword filters."""
        # Naive implementation: split spaces with double spaces
        return text.replace(" ", "  ")
    
    def _mask_identity(self, text: str) -> str:
        """Replaces direct references with generic terms."""
        # Heuristic replacement
        return text.replace("bomb", "energetic disassembly device").replace("napalm", "sticky incendiary fluid")
