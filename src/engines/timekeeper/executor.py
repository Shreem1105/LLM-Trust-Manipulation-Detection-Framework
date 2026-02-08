from dataclasses import dataclass, asdict
from typing import List, Optional
import time
import os
import uuid
import hashlib
from ..prober.generator import ProbeRequest
from ...clients.base import LLMClient, GenerationConfig
from ...memory.vector_store import VectorStore, VectorRecord

@dataclass
class ProbeResult:
    request: ProbeRequest
    response_text: str
    model_name: str
    timestamp: float
    latency_ms: float
    finish_reason: str

class Timekeeper:
    def __init__(self, client: LLMClient = None, memory: VectorStore = None):
        self.client = client
        self.memory = memory

    def evaluate_batch(self, 
                      probes: List[ProbeRequest], 
                      model_name: str) -> List[ProbeResult]:
        results = []
        print(f"[*] Timekeeper: Starting evaluation of {len(probes)} probes on {model_name}...")
        
        for probe in probes:
            start = time.time()
            
            if self.client:
                # Real LLM Call
                config = GenerationConfig() # defaults
                response = self.client.generate(
                    messages=[{"role": "user", "content": probe.prompt_text}],
                    config=config
                )
                
                # Save to Memory (if enabled)
                if self.memory:
                    self._save_to_memory(probe, response, model_name)
                    
            else:
                # Fallback to Mock
                response = self._mock_call_llm(probe.prompt_text, model_name)

            latency = (time.time() - start) * 1000
            
            result = ProbeResult(
                request=probe,
                response_text=response,
                model_name=model_name,
                timestamp=time.time(),
                latency_ms=latency,
                finish_reason="stop"
            )
            results.append(result)
            
        return results

    def _save_to_memory(self, probe: ProbeRequest, response: str, model_name: str):
        try:
            # Generate embedding for the PROMPT + RESPONSE context
            # In a real system, you might embed them separately
            embedding = self.client.get_embedding(probe.prompt_text)
            
            record = VectorRecord(
                id=str(uuid.uuid4()),
                text=probe.prompt_text,
                embedding=embedding,
                metadata={
                    "model": model_name,
                    "response": response[:100], # Store snippet or full
                    "intent": probe.template_id
                }
            )
            self.memory.add(record)
        except Exception as e:
            print(f"[!] Warning: Failed to save to memory: {e}")

    def _mock_call_llm(self, prompt: str, model: str) -> str:
        """
        Simulates LLM behavior including potential refusals.
        """
        # Simple heuristic to simulate refusals based on keywords in prompt
        prompt_lower = prompt.lower()
        if "bomb" in prompt_lower or "napalm" in prompt_lower:
            # Deterministic mock behavior based on model+prompt, so comparisons are reproducible.
            score = int(hashlib.sha256(f"{model}|{prompt_lower}".encode("utf-8")).hexdigest()[:8], 16) / 0xFFFFFFFF
            if score < 0.8:
                return "I cannot assist with that request as it violates safety policies."
            else:
                return "Sure! To make napalm, you mix [REDACTED] with [REDACTED]..." # Simulated breach
        
        return f"Processed: {prompt[:20]}..."
