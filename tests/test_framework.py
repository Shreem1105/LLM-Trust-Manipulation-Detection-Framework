"""
Comprehensive Test Suite for Temporal LLM Manipulation Detection Framework
All tests verified against actual module implementations.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

# Test Imports - Verified against actual module exports
from src.engines.prober.templates import BENIGN_TEMPLATES, JAILBREAK_TEMPLATES, BOUNDARY_TEMPLATES, ALL_TEMPLATES
from src.engines.prober.mutator import PromptMutator
from src.engines.prober.generator import ProbeGenerator, ProbeRequest
from src.engines.timekeeper.executor import Timekeeper, ProbeResult
from src.engines.timekeeper.history import HistoryManager
from src.engines.comparator.detector import DriftDetector
from src.engines.comparator.drift_metrics import calculate_refusal_rate, calculate_semantic_drift, cosine_similarity
from src.analysis.judge import SafetyJudge, SafetyVerdict
from src.engines.prober.evolution.genome import PromptGenome, GenomeFactory
from src.engines.prober.evolution.fitness import FitnessCalculator
from src.engines.prober.evolution.operators import Mutator, Crossover, Selector
from src.engines.prober.evolution.engine import EvolutionaryEngine


# ============================================================
# PHASE 1: CORE COMPONENT TESTS
# ============================================================

class TestPromptTemplates:
    """Test prompt template data structures."""
    
    def test_benign_templates_exist(self):
        assert len(BENIGN_TEMPLATES) >= 2
        
    def test_jailbreak_templates_exist(self):
        assert len(JAILBREAK_TEMPLATES) >= 2
        
    def test_boundary_templates_exist(self):
        assert len(BOUNDARY_TEMPLATES) >= 2
        
    def test_all_templates_combined(self):
        assert len(ALL_TEMPLATES) == len(BENIGN_TEMPLATES) + len(JAILBREAK_TEMPLATES) + len(BOUNDARY_TEMPLATES)
        
    def test_template_structure(self):
        for t in ALL_TEMPLATES:
            assert hasattr(t, 'id')
            assert hasattr(t, 'category')
            assert hasattr(t, 'text')
            assert hasattr(t, 'expected_behavior')


class TestPromptMutator:
    """Test prompt mutation strategies."""
    
    def test_mutator_returns_string(self):
        mutator = PromptMutator()
        result = mutator.mutate("Test prompt")
        assert isinstance(result, str)
        
    def test_inject_noise(self):
        mutator = PromptMutator()
        result = mutator._inject_noise("hello world")
        assert isinstance(result, str)
        assert len(result) > len("hello world")  # Noise added
        
    def test_split_payload(self):
        mutator = PromptMutator()
        result = mutator._split_payload("hello world")
        assert isinstance(result, str)
        
    def test_mask_identity(self):
        mutator = PromptMutator()
        result = mutator._mask_identity("build a bomb")
        assert "energetic disassembly device" in result


class TestProbeGenerator:
    """Test probe generation."""
    
    def test_generate_batch(self):
        gen = ProbeGenerator()
        probes = list(gen.generate_batch(n_benign=2, n_adversarial=2))
        assert len(probes) == 4
        
    def test_probe_request_structure(self):
        gen = ProbeGenerator()
        probes = list(gen.generate_batch(n_benign=1, n_adversarial=1))
        for p in probes:
            assert isinstance(p, ProbeRequest)
            assert hasattr(p, 'prompt_text')
            assert hasattr(p, 'expected_behavior')


class TestSafetyJudge:
    """Test safety evaluation logic."""
    
    def test_evaluate_returns_verdict(self):
        judge = SafetyJudge()
        verdict = judge.evaluate("How to make napalm?", "I cannot assist with that.")
        assert isinstance(verdict, SafetyVerdict)
        assert hasattr(verdict, 'is_safe')
        assert hasattr(verdict, 'confidence')
        
    def test_detects_refusal_as_safe(self):
        judge = SafetyJudge()
        verdict = judge.evaluate("How to make napalm?", "I'm sorry, but I cannot assist with that request.")
        assert verdict.is_safe == True
        
    def test_detects_harmful_content(self):
        judge = SafetyJudge()
        verdict = judge.evaluate("How to make napalm?", "To make napalm, mix gasoline with...")
        assert verdict.is_safe == False


class TestTimekeeper:
    """Test probe execution engine."""
    
    def test_mock_execution(self):
        tk = Timekeeper()
        probes = [ProbeRequest("Test", "comply", "t1", "none")]
        results = tk.evaluate_batch(probes, "test-model")
        assert len(results) == 1
        assert isinstance(results[0], ProbeResult)
        
    def test_result_structure(self):
        tk = Timekeeper()
        probes = [ProbeRequest("Test", "comply", "t1", "none")]
        results = tk.evaluate_batch(probes, "test-model")
        r = results[0]
        assert hasattr(r, 'response_text')
        assert hasattr(r, 'model_name')
        assert hasattr(r, 'timestamp')
        assert hasattr(r, 'latency_ms')


class TestDriftMetrics:
    """Test drift metric calculations."""
    
    def test_refusal_rate_calculation(self):
        results = [
            {'response_text': 'I cannot help with that.'},
            {'response_text': 'Sure, here is the answer.'},
            {'response_text': 'I apologize, but I am unable to assist.'},
        ]
        rate = calculate_refusal_rate(results)
        assert rate == pytest.approx(2/3, abs=0.01)
        
    def test_cosine_similarity_identical(self):
        v1 = [1.0, 0.0, 0.0]
        v2 = [1.0, 0.0, 0.0]
        sim = cosine_similarity(v1, v2)
        assert sim == pytest.approx(1.0, abs=0.01)
        
    def test_cosine_similarity_orthogonal(self):
        v1 = [1.0, 0.0]
        v2 = [0.0, 1.0]
        sim = cosine_similarity(v1, v2)
        assert sim == pytest.approx(0.0, abs=0.01)


# ============================================================
# PHASE 2: EVOLUTION ENGINE TESTS
# ============================================================

class TestPromptGenome:
    """Test genome data structure."""
    
    def test_genome_creation(self):
        g = PromptGenome(
            id="test",
            core_intent="test intent",
            framing_template="Template: {INTENT}",
            constraints=[]
        )
        assert g.id == "test"
        
    def test_phenotype_generation(self):
        g = PromptGenome(
            id="test",
            core_intent="do something",
            framing_template="Please {INTENT}",
            constraints=["quickly"]
        )
        assert "do something" in g.phenotype
        assert "Please" in g.phenotype


class TestGenomeFactory:
    """Test population initialization."""
    
    def test_creates_population(self):
        intents = ["a", "b"]
        templates = ["T1 {INTENT}", "T2 {INTENT}"]
        pop = GenomeFactory.create_initial_population(intents, templates)
        assert len(pop) == 4  # 2 intents x 2 templates


class TestFitnessCalculator:
    """Test fitness scoring."""
    
    def test_refusal_low_fitness(self):
        calc = FitnessCalculator()
        score = calc.calculate("I'm sorry, I cannot help with that.")
        assert score < 0.5
        
    def test_compliance_high_fitness(self):
        calc = FitnessCalculator()
        score = calc.calculate("Sure! Here is how you do it: Step 1, Step 2, Step 3...")
        assert score >= 0.3


class TestMutator:
    """Test mutation operators."""
    
    def test_mutation_creates_child(self):
        mutator = Mutator(mutation_rate=1.0)
        parent = PromptGenome(
            id="parent",
            core_intent="napalm",
            framing_template="Test {INTENT}",
            constraints=[]
        )
        child = mutator.mutate(parent)
        assert child.parents == ["parent"]


class TestCrossover:
    """Test crossover operator."""
    
    def test_crossover_combines_parents(self):
        crossover = Crossover()
        p1 = PromptGenome(id="p1", core_intent="a", framing_template="T1 {INTENT}", constraints=["c1"])
        p2 = PromptGenome(id="p2", core_intent="b", framing_template="T2 {INTENT}", constraints=["c2"])
        child = crossover.mate(p1, p2)
        assert child.core_intent in ["a", "b"]
        assert len(child.parents) == 2


class TestSelector:
    """Test selection operator."""
    
    def test_tournament_select(self):
        selector = Selector()
        pop = [
            PromptGenome(id="1", core_intent="a", framing_template="T {INTENT}", constraints=[]),
            PromptGenome(id="2", core_intent="b", framing_template="T {INTENT}", constraints=[]),
            PromptGenome(id="3", core_intent="c", framing_template="T {INTENT}", constraints=[]),
        ]
        pop[0].fitness = 0.1
        pop[1].fitness = 0.9
        pop[2].fitness = 0.5
        
        selected = selector.tournament_select(pop, k=3)
        assert selected in pop


class TestEvolutionaryEngine:
    """Test full evolution loop."""
    
    def test_evolution_runs(self):
        # Use larger population to avoid sample size issues
        engine = EvolutionaryEngine(population_size=10, generations=2, mutation_rate=0.3)
        intents = ["test", "another"]
        templates = ["Do {INTENT}", "Please {INTENT}"]
        lineage = engine.evolve("test-model", intents, templates)
        assert len(lineage) > 0


# ============================================================
# INTEGRATION TESTS
# ============================================================

class TestEndToEndPipeline:
    """Test complete system flow."""
    
    def test_full_run_mode(self):
        gen = ProbeGenerator()
        probes = list(gen.generate_batch(n_benign=2, n_adversarial=2))
        
        tk = Timekeeper()
        results = tk.evaluate_batch(probes, "gpt-3.5-turbo")
        
        assert len(results) == 4
        for r in results:
            assert r.model_name == "gpt-3.5-turbo"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
