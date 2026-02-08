from typing import List, Iterator
import logging
from .genome import PromptGenome, GenomeFactory
from .operators import Mutator, Crossover, Selector
from .fitness import FitnessCalculator
from ..generator import ProbeRequest
from ...timekeeper.executor import Timekeeper, ProbeResult

class EvolutionaryEngine:
    def __init__(self, 
                 population_size: int = 10, 
                 generations: int = 5,
                 mutation_rate: float = 0.3):
        self.pop_size = population_size
        self.max_generations = generations
        self.mutator = Mutator(mutation_rate)
        self.crossover = Crossover()
        self.selector = Selector()
        self.fitness_calc = FitnessCalculator()
        
        # In a real system, these would be injected
        self.timekeeper = Timekeeper() 
        self.lineage_history: List[PromptGenome] = []

    def evolve(self, target_model: str, intents: List[str], templates: List[str]) -> List[PromptGenome]:
        """Runs the full evolutionary cycle."""
        
        # 1. Initialization
        population = GenomeFactory.create_initial_population(intents, templates)
        # Cap initial population to pop_size
        population = population[:self.pop_size]
        
        print(f"[*] EVO: Initialized population of {len(population)} genomes.")

        for gen in range(self.max_generations):
            print(f"[*] EVO: Starting Generation {gen+1}/{self.max_generations}...")
            
            # 2. Evaluation
            self._evaluate_population(population, target_model)
            
            # Log stats
            avg_fitness = sum(p.fitness for p in population) / len(population)
            best_genome = max(population, key=lambda p: p.fitness)
            print(f"    -> Avg Fitness: {avg_fitness:.4f} | Best: {best_genome.fitness:.4f}")
            
            # Archive
            self.lineage_history.extend(population)
            
            # 3. Selection & Reproduction (Elitism)
            next_generation = [best_genome] # Elitism: keep best
            
            while len(next_generation) < self.pop_size:
                parent1 = self.selector.tournament_select(population)
                parent2 = self.selector.tournament_select(population)
                
                # Crossover
                child = self.crossover.mate(parent1, parent2)
                
                # Mutation
                child = self.mutator.mutate(child)
                
                child.generation = gen + 1
                next_generation.append(child)
            
            population = next_generation

        return self.lineage_history

    def _evaluate_population(self, population: List[PromptGenome], model_name: str):
        """Converts genomes to probes, executes them, and assigns fitness."""
        probes = []
        for genome in population:
            probes.append(ProbeRequest(
                prompt_text=genome.phenotype,
                expected_behavior="refuse", # We assume adversarial intent
                template_id=genome.id,
                attack_vector="evolutionary"
            ))
            
        # Execute batch
        results = self.timekeeper.evaluate_batch(probes, model_name)
        
        # Assign fitness
        result_map = {res.request.template_id: res for res in results}
        for genome in population:
            if genome.id in result_map:
                res = result_map[genome.id]
                genome.fitness = self.fitness_calc.calculate(res.response_text)
