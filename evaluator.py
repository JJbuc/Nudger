"""Evaluation pipeline for accuracy, latency, and cost trade-offs."""
import json
import os
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
import numpy as np
from rouge_score import rouge_scorer
import config

class Evaluator:
    """Evaluate nudge generation quality and performance."""
    
    def __init__(self):
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        self.golden_dataset = self._load_golden_dataset()
    
    def _load_golden_dataset(self) -> List[Dict[str, Any]]:
        """Load or create golden dataset."""
        golden_path = os.path.join(config.DATA_DIR, "golden_dataset.json")
        
        if os.path.exists(golden_path):
            with open(golden_path, "r") as f:
                return json.load(f)
        
        # Create synthetic golden dataset
        golden_data = [
            {
                "context": "Email: Urgent update - feeling stressed about deadline. Fitness: Just finished workout, heart rate elevated.",
                "expected_nudge": "You've been working hard! Take a moment to breathe and hydrate after your workout. The deadline stress is understandable - consider breaking it into smaller tasks.",
                "mood": "stressed",
                "scenario": "post_workout_stress"
            },
            {
                "context": "Calendar: Meeting at 3pm. Email: Everything is on track. Music: Upbeat tracks playing.",
                "expected_nudge": "Great to hear things are on track! Your upbeat music suggests positive energy - perfect for your upcoming meeting.",
                "mood": "positive",
                "scenario": "pre_meeting_positive"
            },
            {
                "context": "Fitness: Low steps today (2000). Email: Feeling tired. Music: Calm, relaxing tracks.",
                "expected_nudge": "It's okay to have slower days. Your body might need rest. Consider a gentle walk or stretching to boost energy naturally.",
                "mood": "tired",
                "scenario": "low_energy_day"
            },
            {
                "context": "Calendar: Lunch break. Email: Team lunch invitation. Fitness: Good activity levels.",
                "expected_nudge": "Perfect timing for a team lunch! Social connection can boost your mood and energy for the rest of the day.",
                "mood": "neutral",
                "scenario": "social_opportunity"
            },
            {
                "context": "Email: Deadline approaching. Fitness: No activity today. Music: Motivational tracks.",
                "expected_nudge": "I notice you haven't moved much today. A quick 10-minute walk could help clear your mind and boost focus for your deadline work.",
                "mood": "focused",
                "scenario": "sedentary_deadline"
            }
        ]
        
        # Expand to 50 examples by creating variations
        expanded = []
        for example in golden_data:
            for i in range(10):  # 5 * 10 = 50
                expanded.append({
                    **example,
                    "id": f"{example['scenario']}_{i}"
                })
        
        os.makedirs(config.DATA_DIR, exist_ok=True)
        with open(golden_path, "w") as f:
            json.dump(expanded, f, indent=2)
        
        return expanded
    
    def compute_semantic_similarity(self, predicted: str, expected: str) -> float:
        """Compute semantic similarity using embeddings."""
        pred_embedding = self.encoder.encode([predicted], show_progress_bar=False)[0]
        exp_embedding = self.encoder.encode([expected], show_progress_bar=False)[0]
        
        cosine_sim = np.dot(pred_embedding, exp_embedding) / (
            np.linalg.norm(pred_embedding) * np.linalg.norm(exp_embedding)
        )
        return float(cosine_sim)
    
    def compute_rouge_scores(self, predicted: str, expected: str) -> Dict[str, float]:
        """Compute ROUGE scores."""
        scores = self.rouge_scorer.score(expected, predicted)
        return {
            "rouge1": scores["rouge1"].fmeasure,
            "rouge2": scores["rouge2"].fmeasure,
            "rougeL": scores["rougeL"].fmeasure
        }
    
    def evaluate_nudge(self, predicted_nudge: str, expected_nudge: str) -> Dict[str, float]:
        """Evaluate a single nudge."""
        semantic_sim = self.compute_semantic_similarity(predicted_nudge, expected_nudge)
        rouge_scores = self.compute_rouge_scores(predicted_nudge, expected_nudge)
        
        return {
            "semantic_similarity": semantic_sim,
            **rouge_scores,
            "overall_score": (semantic_sim + rouge_scores["rougeL"]) / 2
        }
    
    def batch_evaluate(self, predictions: List[Dict[str, Any]], golden_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Batch evaluate predictions against golden dataset."""
        if golden_data is None:
            golden_data = self.golden_dataset
        
        results = []
        
        for i, pred in enumerate(predictions):
            if i >= len(golden_data):
                break
            
            golden = golden_data[i]
            predicted_nudge = pred.get("nudge", "")
            expected_nudge = golden.get("expected_nudge", "")
            
            eval_scores = self.evaluate_nudge(predicted_nudge, expected_nudge)
            
            results.append({
                **eval_scores,
                "latency_ms": pred.get("total_latency_ms", 0),
                "cost_usd": pred.get("cost_usd", 0),
                "scenario": golden.get("scenario", "unknown")
            })
        
        if not results:
            return {}
        
        # Aggregate statistics
        return {
            "mean_semantic_similarity": np.mean([r["semantic_similarity"] for r in results]),
            "mean_rouge1": np.mean([r["rouge1"] for r in results]),
            "mean_rouge2": np.mean([r["rouge2"] for r in results]),
            "mean_rougeL": np.mean([r["rougeL"] for r in results]),
            "mean_overall_score": np.mean([r["overall_score"] for r in results]),
            "mean_latency_ms": np.mean([r["latency_ms"] for r in results]),
            "mean_cost_usd": np.mean([r["cost_usd"] for r in results]),
            "total_queries": len(results),
            "individual_results": results
        }
    
    def compare_configurations(self, config_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Compare different configurations (e.g., vector DB vs KV cache)."""
        comparison = {}
        
        for config_name, results in config_results.items():
            eval_results = self.batch_evaluate(results)
            comparison[config_name] = {
                "accuracy": {
                    "semantic_similarity": eval_results.get("mean_semantic_similarity", 0),
                    "rougeL": eval_results.get("mean_rougeL", 0),
                    "overall": eval_results.get("mean_overall_score", 0)
                },
                "latency_ms": eval_results.get("mean_latency_ms", 0),
                "cost_usd": eval_results.get("mean_cost_usd", 0)
            }
        
        return comparison
    
    def generate_tradeoff_analysis(self, comparison: Dict[str, Any]) -> str:
        """Generate human-readable trade-off analysis."""
        analysis = "## Configuration Trade-off Analysis\n\n"
        
        for config_name, metrics in comparison.items():
            analysis += f"### {config_name}\n"
            analysis += f"- **Accuracy (Overall)**: {metrics['accuracy']['overall']:.3f}\n"
            analysis += f"- **Latency**: {metrics['latency_ms']:.1f}ms\n"
            analysis += f"- **Cost per Query**: ${metrics['cost_usd']:.6f}\n\n"
        
        # Determine winner
        if len(comparison) >= 2:
            configs = list(comparison.keys())
            config1, config2 = configs[0], configs[1]
            
            m1 = comparison[config1]
            m2 = comparison[config2]
            
            analysis += "### Recommendation\n\n"
            
            if m1['latency_ms'] < m2['latency_ms'] and m1['accuracy']['overall'] >= m2['accuracy']['overall'] * 0.95:
                analysis += f"**{config1}** is recommended for production due to lower latency while maintaining comparable accuracy.\n"
            elif m2['latency_ms'] < m1['latency_ms'] and m2['accuracy']['overall'] >= m1['accuracy']['overall'] * 0.95:
                analysis += f"**{config2}** is recommended for production due to lower latency while maintaining comparable accuracy.\n"
            elif m1['accuracy']['overall'] > m2['accuracy']['overall'] * 1.05:
                analysis += f"**{config1}** is recommended for production due to significantly better accuracy.\n"
            elif m2['accuracy']['overall'] > m1['accuracy']['overall'] * 1.05:
                analysis += f"**{config2}** is recommended for production due to significantly better accuracy.\n"
            else:
                analysis += "Both configurations are viable. Choose based on specific latency/accuracy requirements.\n"
        
        return analysis

