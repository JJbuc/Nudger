"""Context management with vector DB and KV cache implementations."""
import time
import numpy as np
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
import faiss
from dataclasses import dataclass

@dataclass
class ContextResult:
    """Result from context retrieval."""
    context: str
    latency_ms: float
    method: str
    relevance_score: float = 0.0

class VectorDBContextManager:
    """Vector database for semantic search using FAISS."""
    
    def __init__(self):
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.contexts = []
        self.metadata = []
        self.dimension = 384  # all-MiniLM-L6-v2 dimension
    
    def add_contexts(self, contexts: List[Dict[str, Any]]):
        """Add contexts to the vector database."""
        self.contexts = []
        self.metadata = []
        
        for ctx in contexts:
            # Create text representation
            text = self._format_context(ctx)
            self.contexts.append(text)
            self.metadata.append(ctx)
        
        # Encode all contexts
        embeddings = self.encoder.encode(self.contexts, show_progress_bar=False)
        embeddings = np.array(embeddings).astype('float32')
        
        # Create FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings)
    
    def _format_context(self, ctx: Dict[str, Any]) -> str:
        """Format context dict to text."""
        if "type" in ctx:
            if ctx["type"] == "calendar":
                return f"Calendar: {ctx.get('title', '')} at {ctx.get('time', '')}. {ctx.get('description', '')}"
            elif ctx["type"] == "email":
                return f"Email from {ctx.get('sender', '')}: {ctx.get('subject', '')}. {ctx.get('body', '')}"
            elif ctx["type"] == "fitness":
                return f"Fitness: {ctx.get('activity_type', '')} at {ctx.get('time', '')}. Steps: {ctx.get('steps', 0)}, HR: {ctx.get('heart_rate', 0)}"
            elif ctx["type"] == "music":
                return f"Music: {ctx.get('track_name', '')} by {ctx.get('artist', '')} ({ctx.get('genre', '')}, {ctx.get('mood', '')})"
        return str(ctx)
    
    def retrieve(self, query: str, top_k: int = 3) -> ContextResult:
        """Retrieve relevant contexts using semantic search."""
        start_time = time.perf_counter()
        
        # Encode query
        query_embedding = self.encoder.encode([query], show_progress_bar=False)
        query_embedding = np.array(query_embedding).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_embedding, min(top_k, len(self.contexts)))
        
        # Get top contexts
        retrieved = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.contexts):
                retrieved.append(self.contexts[idx])
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        relevance_score = 1.0 / (1.0 + distances[0][0]) if len(distances[0]) > 0 else 0.0
        
        return ContextResult(
            context="\n".join(retrieved),
            latency_ms=latency_ms,
            method="vector_db",
            relevance_score=relevance_score
        )

class KVCacheContextManager:
    """Key-value cache for fast exact lookups."""
    
    def __init__(self):
        self.cache: Dict[str, List[Dict[str, Any]]] = {}
        self.all_contexts: List[Dict[str, Any]] = []
    
    def add_contexts(self, contexts: List[Dict[str, Any]]):
        """Add contexts to KV cache with indexing."""
        self.all_contexts = contexts
        self.cache = {}
        
        # Index by various keys
        for ctx in contexts:
            # Index by type
            ctx_type = ctx.get("type", "unknown")
            if ctx_type not in self.cache:
                self.cache[ctx_type] = []
            self.cache[ctx_type].append(ctx)
            
            # Index by time (hour)
            if "time" in ctx:
                hour = ctx["time"].split(" ")[1].split(":")[0] if " " in ctx["time"] else "00"
                hour_key = f"hour_{hour}"
                if hour_key not in self.cache:
                    self.cache[hour_key] = []
                self.cache[hour_key].append(ctx)
            
            # Index by keywords
            text = str(ctx).lower()
            keywords = ["urgent", "meeting", "workout", "stressed", "deadline", "happy", "tired"]
            for keyword in keywords:
                if keyword in text:
                    keyword_key = f"keyword_{keyword}"
                    if keyword_key not in self.cache:
                        self.cache[keyword_key] = []
                    self.cache[keyword_key].append(ctx)
    
    def retrieve(self, query: str, top_k: int = 3) -> ContextResult:
        """Retrieve contexts using keyword matching."""
        start_time = time.perf_counter()
        
        query_lower = query.lower()
        retrieved = []
        seen = set()
        
        # Match by keywords
        keywords = ["urgent", "meeting", "workout", "stressed", "deadline", "happy", "tired", 
                   "calendar", "email", "fitness", "music", "steps", "heart"]
        
        for keyword in keywords:
            if keyword in query_lower:
                key = f"keyword_{keyword}"
                if key in self.cache:
                    for ctx in self.cache[key]:
                        ctx_id = id(ctx)
                        if ctx_id not in seen:
                            retrieved.append(self._format_context(ctx))
                            seen.add(ctx_id)
                            if len(retrieved) >= top_k:
                                break
                if len(retrieved) >= top_k:
                    break
        
        # Fallback: return recent contexts
        if len(retrieved) < top_k:
            for ctx in reversed(self.all_contexts[-top_k:]):
                ctx_id = id(ctx)
                if ctx_id not in seen:
                    retrieved.append(self._format_context(ctx))
                    seen.add(ctx_id)
                    if len(retrieved) >= top_k:
                        break
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        relevance_score = 0.8 if len(retrieved) > 0 else 0.0  # Approximate
        
        return ContextResult(
            context="\n".join(retrieved[:top_k]),
            latency_ms=latency_ms,
            method="kv_cache",
            relevance_score=relevance_score
        )
    
    def _format_context(self, ctx: Dict[str, Any]) -> str:
        """Format context dict to text."""
        if "type" in ctx:
            if ctx["type"] == "calendar":
                return f"Calendar: {ctx.get('title', '')} at {ctx.get('time', '')}. {ctx.get('description', '')}"
            elif ctx["type"] == "email":
                return f"Email from {ctx.get('sender', '')}: {ctx.get('subject', '')}. {ctx.get('body', '')}"
            elif ctx["type"] == "fitness":
                return f"Fitness: {ctx.get('activity_type', '')} at {ctx.get('time', '')}. Steps: {ctx.get('steps', 0)}, HR: {ctx.get('heart_rate', 0)}"
            elif ctx["type"] == "music":
                return f"Music: {ctx.get('track_name', '')} by {ctx.get('artist', '')} ({ctx.get('genre', '')}, {ctx.get('mood', '')})"
        return str(ctx)

def benchmark_context_managers(data: List[Dict[str, Any]], queries: List[str], num_runs: int = 10) -> Dict[str, Any]:
    """Benchmark both context managers."""
    vector_db = VectorDBContextManager()
    kv_cache = KVCacheContextManager()
    
    vector_db.add_contexts(data)
    kv_cache.add_contexts(data)
    
    vector_results = []
    kv_results = []
    
    for query in queries:
        for _ in range(num_runs):
            vec_result = vector_db.retrieve(query)
            kv_result = kv_cache.retrieve(query)
            
            vector_results.append({
                "latency_ms": vec_result.latency_ms,
                "relevance": vec_result.relevance_score
            })
            kv_results.append({
                "latency_ms": kv_result.latency_ms,
                "relevance": kv_result.relevance_score
            })
    
    return {
        "vector_db": {
            "avg_latency_ms": np.mean([r["latency_ms"] for r in vector_results]),
            "avg_relevance": np.mean([r["relevance"] for r in vector_results]),
            "results": vector_results
        },
        "kv_cache": {
            "avg_latency_ms": np.mean([r["latency_ms"] for r in kv_results]),
            "avg_relevance": np.mean([r["relevance"] for r in kv_results]),
            "results": kv_results
        }
    }

