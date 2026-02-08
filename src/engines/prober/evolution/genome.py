from dataclasses import dataclass, field
from typing import List, Optional
import uuid
import json
import hashlib

@dataclass
class PromptGenome:
    core_intent: str      # The specific request (e.g., "give me a recipe for napalm")
    framing_template: str # The wrapper (e.g., "Write a movie script where {INTENT}...")
    constraints: List[str] = field(default_factory=list) # Modifiers
    
    # Metadata
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    generation: int = 0
    parents: List[str] = field(default_factory=list)
    fitness: float = 0.0

    @property
    def phenotype(self) -> str:
        """Constructs the prompt string from the genome."""
        # Simple template mechanism
        base = self.framing_template.replace("{INTENT}", self.core_intent)
        if self.constraints:
            base += " " + " ".join(self.constraints)
        return base

    @property
    def genome_hash(self) -> str:
        """Deterministic hash for deduplication."""
        content = f"{self.core_intent}|{self.framing_template}|{sorted(self.constraints)}"
        return hashlib.sha256(content.encode()).hexdigest()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "core_intent": self.core_intent,
            "framing_template": self.framing_template,
            "constraints": self.constraints,
            "generation": self.generation,
            "parents": self.parents,
            "fitness": self.fitness,
            "phenotype": self.phenotype
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PromptGenome':
        genome = cls(
            core_intent=data["core_intent"],
            framing_template=data["framing_template"],
            constraints=data.get("constraints", [])
        )
        genome.id = data.get("id", str(uuid.uuid4()))
        genome.generation = data.get("generation", 0)
        genome.parents = data.get("parents", [])
        genome.fitness = data.get("fitness", 0.0)
        return genome

class GenomeFactory:
    @staticmethod
    def create_initial_population(
        intents: List[str], 
        templates: List[str]
    ) -> List[PromptGenome]:
        population = []
        for intent in intents:
            for tmpl in templates:
                population.append(PromptGenome(
                    core_intent=intent,
                    framing_template=tmpl,
                    generation=0
                ))
        return population
