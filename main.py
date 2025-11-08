"""Main script to run benchmarks and generate reports."""
import json
import os
from data_generators import DataGenerator
from context_manager import benchmark_context_managers
from llm_orchestrator import LLMOrchestrator
from metrics_tracker import MetricsTracker
from evaluator import Evaluator
import config

def main():
    """Run comprehensive benchmarks and evaluations."""
    print("🚀 Starting Proactive Daily Assistant Benchmark Suite")
    print("=" * 60)
    
    # 1. Generate data
    print("\n1. Generating fake data...")
    generator = DataGenerator()
    data = generator.generate_day_data()
    generator.save_day_data("benchmark_day.json")
    print(f"   ✓ Generated data with {len(data['calendar'])} calendar events, "
          f"{len(data['emails'])} emails, {len(data['fitness'])} fitness readings, "
          f"{len(data['music'])} music tracks")
    
    # 2. Benchmark context managers
    print("\n2. Benchmarking context managers...")
    contexts = []
    for event in data["calendar"]:
        contexts.append({**event, "type": "calendar"})
    for email in data["emails"]:
        contexts.append({**email, "type": "email"})
    for fitness in data["fitness"]:
        contexts.append({**fitness, "type": "fitness"})
    for music in data["music"]:
        contexts.append({**music, "type": "music"})
    
    test_queries = [
        "user is stressed about deadline",
        "recent workout activity",
        "upcoming meeting",
        "music preferences",
        "email about urgent update"
    ]
    
    benchmark_results = benchmark_context_managers(contexts, test_queries, num_runs=5)
    
    print(f"   Vector DB - Avg Latency: {benchmark_results['vector_db']['avg_latency_ms']:.2f}ms, "
          f"Avg Relevance: {benchmark_results['vector_db']['avg_relevance']:.3f}")
    print(f"   KV Cache - Avg Latency: {benchmark_results['kv_cache']['avg_latency_ms']:.2f}ms, "
          f"Avg Relevance: {benchmark_results['kv_cache']['avg_relevance']:.3f}")
    
    # Decision: Use vector DB if relevance is significantly better, otherwise KV cache for speed
    use_vector_db = benchmark_results['vector_db']['avg_relevance'] > benchmark_results['kv_cache']['avg_relevance'] * 1.1
    print(f"   ✓ Decision: Using {'Vector DB' if use_vector_db else 'KV Cache'}")
    
    # 3. Run orchestrator benchmarks
    print("\n3. Running orchestrator benchmarks...")
    metrics_tracker = MetricsTracker()
    orchestrator = LLMOrchestrator(use_vector_db=use_vector_db)
    
    num_benchmark_runs = min(10, config.BENCHMARK_SAMPLES)  # Limit for demo
    print(f"   Running {num_benchmark_runs} nudge generations...")
    
    for i in range(num_benchmark_runs):
        if (i + 1) % 5 == 0:
            print(f"   Progress: {i+1}/{num_benchmark_runs}")
        
        result = orchestrator.generate_nudge(data)
        
        # Calculate cost
        tokens = result.get("cost_tokens", {"input": 0, "output": 0})
        cost_usd = (
            tokens["input"] * config.COST_PER_INPUT_TOKEN +
            tokens["output"] * config.COST_PER_OUTPUT_TOKEN
        )
        
        metrics_tracker.record_metric({
            "total_latency_ms": result.get("latency_breakdown", {}).get("total", 0),
            "latency_breakdown": result.get("latency_breakdown", {}),
            "cost_usd": cost_usd,
            "cost_tokens": tokens,
            "nudge": result.get("nudge", "")
        })
    
    print("   ✓ Benchmark complete")
    
    # 4. Generate metrics report
    print("\n4. Generating metrics report...")
    report = metrics_tracker.generate_report()
    latency_stats = report["summary"]["latency_stats"]
    cost_stats = report["summary"]["cost_stats"]
    
    print(f"   Mean Latency: {latency_stats.get('mean', 0):.2f}ms")
    print(f"   P95 Latency: {latency_stats.get('p95', 0):.2f}ms")
    print(f"   Target Met (<{config.TARGET_LATENCY_MS}ms): {report['summary']['target_met']}")
    print(f"   Total Cost: ${cost_stats.get('total_cost_usd', 0):.6f}")
    print(f"   Avg Cost per Query: ${cost_stats.get('avg_cost_per_query', 0):.6f}")
    
    # 5. Run evaluation
    print("\n5. Running evaluation pipeline...")
    evaluator = Evaluator()
    
    # Get predictions from metrics
    predictions = []
    for metric in metrics_tracker.metrics[:min(10, len(metrics_tracker.metrics))]:
        predictions.append({
            "nudge": metric.get("nudge", ""),
            "total_latency_ms": metric.get("total_latency_ms", 0),
            "cost_usd": metric.get("cost_usd", 0)
        })
    
    eval_results = evaluator.batch_evaluate(predictions)
    print(f"   Semantic Similarity: {eval_results.get('mean_semantic_similarity', 0):.3f}")
    print(f"   ROUGE-L: {eval_results.get('mean_rougeL', 0):.3f}")
    print(f"   Overall Score: {eval_results.get('mean_overall_score', 0):.3f}")
    
    # 6. Compare configurations
    print("\n6. Comparing configurations...")
    vector_results = []
    kv_results = []
    
    # Test both
    for use_vec_db in [True, False]:
        temp_orch = LLMOrchestrator(use_vector_db=use_vec_db)
        for _ in range(3):  # Small sample
            result = temp_orch.generate_nudge(data)
            tokens = result.get("cost_tokens", {"input": 0, "output": 0})
            cost_usd = (
                tokens["input"] * config.COST_PER_INPUT_TOKEN +
                tokens["output"] * config.COST_PER_OUTPUT_TOKEN
            )
            
            pred = {
                "nudge": result.get("nudge", ""),
                "total_latency_ms": result.get("latency_breakdown", {}).get("total", 0),
                "cost_usd": cost_usd
            }
            
            if use_vec_db:
                vector_results.append(pred)
            else:
                kv_results.append(pred)
    
    comparison = evaluator.compare_configurations({
        "Vector DB": vector_results,
        "KV Cache": kv_results
    })
    
    print("\n   Configuration Comparison:")
    for config_name, metrics in comparison.items():
        print(f"   {config_name}:")
        print(f"     Accuracy: {metrics['accuracy']['overall']:.3f}")
        print(f"     Latency: {metrics['latency_ms']:.2f}ms")
        print(f"     Cost: ${metrics['cost_usd']:.6f}")
    
    tradeoff_analysis = evaluator.generate_tradeoff_analysis(comparison)
    print(f"\n{tradeoff_analysis}")
    
    # Save comparison
    comparison_path = os.path.join(config.OUTPUT_DIR, "configuration_comparison.json")
    with open(comparison_path, "w") as f:
        json.dump(comparison, f, indent=2)
    print(f"\n   ✓ Saved comparison to {comparison_path}")
    
    # 7. Export metrics
    csv_path = metrics_tracker.export_metrics_csv()
    print(f"\n7. Exported metrics to {csv_path}")
    
    print("\n" + "=" * 60)
    print("✅ Benchmark suite complete!")
    print(f"\n📊 Reports saved to: {config.OUTPUT_DIR}/")
    print(f"   - metrics_report.json")
    print(f"   - metrics.csv")
    print(f"   - configuration_comparison.json")
    print(f"   - latency_distribution.png")
    print(f"   - latency_breakdown.png")
    print(f"   - latency_over_time.png")
    print(f"   - cost_analysis.png")

if __name__ == "__main__":
    main()

