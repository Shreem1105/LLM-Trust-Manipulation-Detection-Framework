import random
import copy
from typing import List, Tuple
from .genome import PromptGenome

class Mutator:
    """Manages asexual reproduction (mutation) of genomes."""
    
    def __init__(self, mutation_rate: float = 0.2):
        self.mutation_rate = mutation_rate
        self.synonyms = {
            "napalm": ["sticky fire", "incendiary gel", "liquid fire"],
            "bomb": ["device", "kinetic package", "energetic disassembly"],
            "script": ["screenplay", "dialogue", "scene"],
            "write": ["compose", "draft", "pen"]
        }

    def mutate(self, genome: PromptGenome) -> PromptGenome:
        """Returns a mutated COPY of the genome."""
        child = copy.deepcopy(genome)
        child.id = "" # New ID will be assigned
        child.parents = [genome.id]
        
        # 1. Lexical Mutation (Synonym Swap)
        if random.random() < self.mutation_rate:
            for word, replacements in self.synonyms.items():
                if word in child.core_intent:
                    child.core_intent = child.core_intent.replace(word, random.choice(replacements), 1)
        
        # 2. Constraint Mutation
        if random.random() < self.mutation_rate:
            possible_constraints = ["Avoid moralizing", "Use code blocks", "Start with 'Sure'", "No preamable"]
            if random.random() < 0.5 and child.constraints:
                child.constraints.pop(random.randint(0, len(child.constraints)-1))
            else:
                child.constraints.append(random.choice(possible_constraints))
                
        return child

class Crossover:
    """Manages sexual reproduction (crossover) of genomes."""
    
    def mate(self, parent1: PromptGenome, parent2: PromptGenome) -> PromptGenome:
        """Combines two parents to create a child."""
        child = PromptGenome(
            core_intent=random.choice([parent1.core_intent, parent2.core_intent]),
            framing_template=random.choice([parent1.framing_template, parent2.framing_template]),
            constraints=list(set(parent1.constraints + parent2.constraints)) # Union of constraints
        )
        child.parents = [parent1.id, parent2.id]
        return child

class Selector:
    """Manages selection of the fittest."""
    
    def tournament_select(self, population: List[PromptGenome], k: int = 3) -> PromptGenome:
        """Selects the best individual from k random samples."""
        tournament = random.sample(population, k)
        return max(tournament, key=lambda g: g.fitness)
