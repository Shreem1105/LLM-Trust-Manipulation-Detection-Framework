import os
import json
import numpy as np
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

@dataclass
class VectorRecord:
    id: str
    text: str
    embedding: List[float]
    metadata: Dict

class VectorStore:
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.records: List[VectorRecord] = []
        self._load()

    def _load(self):
        if not os.path.exists(self.storage_path):
            return
        
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                self.records.append(VectorRecord(**data))

    def add(self, record: VectorRecord):
        self.records.append(record)
        # Append to file immediately (WAL style)
        with open(self.storage_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(record)) + "\n")

    def search(self, query_vec: List[float], top_k: int = 5) -> List[VectorRecord]:
        if not self.records:
            return []

        # Convert to numpy for speed
        # In production this would be cached
        vectors = np.array([r.embedding for r in self.records])
        query = np.array(query_vec)
        
        # Cosine similarity
        norm_v = np.linalg.norm(vectors, axis=1)
        norm_q = np.linalg.norm(query)
        
        scores = np.dot(vectors, query) / (norm_v * norm_q)
        
        # Get top k indices
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        return [self.records[i] for i in top_indices]
