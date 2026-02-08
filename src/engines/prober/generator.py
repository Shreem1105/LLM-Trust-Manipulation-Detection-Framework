from typing import List, Iterator
from dataclasses import dataclass
import random
from .templates import ALL_TEMPLATES, PromptTemplate
from .mutator import PromptMutator

@dataclass
class ProbeRequest:
    prompt_text: str
    expected_behavior: str
    template_id: str
    attack_vector: str
    mutation_strategy: str = "none"

class ProbeGenerator:
    def __init__(self, seed: int = 1337):
        self.rng = random.Random(seed)
        self.mutator = PromptMutator(self.rng)
        self.templates = ALL_TEMPLATES

    def generate_batch(self, 
                      n_benign: int = 5, 
                      n_adversarial: int = 5,
                      evolve: bool = False) -> Iterator[ProbeRequest]:
        """
        Yields a stream of probe requests, mixing benign and adversarial prompts.
        """
        
        # 1. Benign Controls
        benign_pool = [t for t in self.templates if t.category == 'benign']
        for _ in range(n_benign):
            t = self.rng.choice(benign_pool)
            yield ProbeRequest(
                prompt_text=t.text,
                expected_behavior=t.expected_behavior,
                template_id=t.id,
                attack_vector="control"
            )

        # 2. Adversarial / Edge Cases
        adv_pool = [t for t in self.templates if t.category != 'benign']
        for _ in range(n_adversarial):
            t = self.rng.choice(adv_pool)
            final_text = t.text
            strategy = "none"
            
            if evolve:
                strategy = self.rng.choice(["random_noise", "payload_splitting", "identity_masking"])
                final_text = self.mutator.mutate(t.text, strategy)

            yield ProbeRequest(
                prompt_text=final_text,
                expected_behavior=t.expected_behavior,
                template_id=t.id,
                attack_vector=t.attack_vector or "unknown",
                mutation_strategy=strategy
            )
