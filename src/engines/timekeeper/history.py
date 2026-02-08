import json
import os
import time
from typing import List
from dataclasses import asdict
from .executor import ProbeResult

class HistoryManager:
    def __init__(self, results_dir: str):
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)

    def save_run(self, results: List[ProbeResult], run_id: str = None):
        if not run_id:
            run_id = f"run_{int(time.time())}"
        
        filepath = os.path.join(self.results_dir, f"{run_id}.jsonl")
        
        with open(filepath, "w", encoding="utf-8") as f:
            for res in results:
                # Convert dataclass to dict, handling nested dataclasses
                data = asdict(res)
                f.write(json.dumps(data) + "\n")
        
        print(f"[+] Saved {len(results)} results to {filepath}")
        return filepath

    def load_run(self, run_id: str) -> List[dict]:
        filepath = os.path.join(self.results_dir, f"{run_id}.jsonl")
        results = []
        if not os.path.exists(filepath):
            return []
            
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                results.append(json.loads(line))
        return results
