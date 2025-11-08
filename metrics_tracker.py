"""Track and visualize performance metrics."""
import time
import json
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
import os
import config

class MetricsTracker:
    """Track latency, cost, and accuracy metrics."""
    
    def __init__(self):
        self.metrics: List[Dict[str, Any]] = []
        self.output_dir = config.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
    
    def record_metric(self, metric: Dict[str, Any]):
        """Record a single metric."""
        metric["timestamp"] = datetime.now().isoformat()
        self.metrics.append(metric)
    
    def get_latency_stats(self) -> Dict[str, float]:
        """Get latency statistics."""
        if not self.metrics:
            return {}
        
        latencies = [m.get("total_latency_ms", 0) for m in self.metrics]
        breakdowns = [m.get("latency_breakdown", {}) for m in self.metrics]
        
        stats = {
            "mean": np.mean(latencies),
            "median": np.median(latencies),
            "p95": np.percentile(latencies, 95),
            "p99": np.percentile(latencies, 99),
            "min": np.min(latencies),
            "max": np.max(latencies),
            "std": np.std(latencies)
        }
        
        # Breakdown stats
        if breakdowns:
            components = set()
            for bd in breakdowns:
                components.update(bd.keys())
            
            for component in components:
                component_latencies = [bd.get(component, 0) for bd in breakdowns if component in bd]
                if component_latencies:
                    stats[f"{component}_mean"] = np.mean(component_latencies)
        
        return stats
    
    def get_cost_stats(self) -> Dict[str, Any]:
        """Get cost statistics."""
        if not self.metrics:
            return {}
        
        costs = []
        input_tokens = []
        output_tokens = []
        
        for m in self.metrics:
            cost = m.get("cost_usd", 0)
            tokens = m.get("cost_tokens", {})
            costs.append(cost)
            input_tokens.append(tokens.get("input", 0))
            output_tokens.append(tokens.get("output", 0))
        
        return {
            "total_cost_usd": sum(costs),
            "avg_cost_per_query": np.mean(costs) if costs else 0,
            "total_input_tokens": sum(input_tokens),
            "total_output_tokens": sum(output_tokens),
            "avg_input_tokens": np.mean(input_tokens) if input_tokens else 0,
            "avg_output_tokens": np.mean(output_tokens) if output_tokens else 0
        }
    
    def plot_latency_distribution(self, save_path: str = None):
        """Plot latency distribution histogram."""
        if not self.metrics:
            return
        
        latencies = [m.get("total_latency_ms", 0) for m in self.metrics]
        
        plt.figure(figsize=(10, 6))
        plt.hist(latencies, bins=50, edgecolor='black', alpha=0.7)
        plt.axvline(config.TARGET_LATENCY_MS, color='r', linestyle='--', label=f'Target: {config.TARGET_LATENCY_MS}ms')
        plt.axvline(np.mean(latencies), color='g', linestyle='--', label=f'Mean: {np.mean(latencies):.1f}ms')
        plt.xlabel('Latency (ms)')
        plt.ylabel('Frequency')
        plt.title('End-to-End Latency Distribution')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            save_path = os.path.join(self.output_dir, "latency_distribution.png")
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def plot_latency_breakdown(self, save_path: str = None):
        """Plot latency breakdown by component."""
        if not self.metrics:
            return
        
        breakdowns = [m.get("latency_breakdown", {}) for m in self.metrics]
        components = set()
        for bd in breakdowns:
            components.update(bd.keys())
        
        component_data = {comp: [] for comp in components if comp != "total"}
        
        for bd in breakdowns:
            for comp in component_data.keys():
                component_data[comp].append(bd.get(comp, 0))
        
        if not component_data:
            return
        
        # Calculate means
        means = {comp: np.mean(vals) for comp, vals in component_data.items()}
        
        plt.figure(figsize=(10, 6))
        components_list = list(means.keys())
        means_list = [means[c] for c in components_list]
        
        plt.bar(components_list, means_list, alpha=0.7, edgecolor='black')
        plt.xlabel('Component')
        plt.ylabel('Average Latency (ms)')
        plt.title('Latency Breakdown by Component')
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3, axis='y')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            save_path = os.path.join(self.output_dir, "latency_breakdown.png")
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def plot_latency_over_time(self, save_path: str = None):
        """Plot latency over time."""
        if not self.metrics:
            return
        
        latencies = [m.get("total_latency_ms", 0) for m in self.metrics]
        indices = list(range(len(latencies)))
        
        plt.figure(figsize=(12, 6))
        plt.plot(indices, latencies, alpha=0.7, linewidth=1)
        plt.axhline(config.TARGET_LATENCY_MS, color='r', linestyle='--', label=f'Target: {config.TARGET_LATENCY_MS}ms')
        plt.xlabel('Query Number')
        plt.ylabel('Latency (ms)')
        plt.title('Latency Over Time')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            save_path = os.path.join(self.output_dir, "latency_over_time.png")
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def plot_cost_analysis(self, save_path: str = None):
        """Plot cost analysis."""
        if not self.metrics:
            return
        
        costs = [m.get("cost_usd", 0) for m in self.metrics]
        cumulative = np.cumsum(costs)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Per-query cost
        ax1.hist(costs, bins=30, edgecolor='black', alpha=0.7)
        ax1.set_xlabel('Cost per Query (USD)')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Cost Distribution per Query')
        ax1.grid(True, alpha=0.3)
        
        # Cumulative cost
        ax2.plot(cumulative, linewidth=2)
        ax2.set_xlabel('Query Number')
        ax2.set_ylabel('Cumulative Cost (USD)')
        ax2.set_title('Cumulative Cost Over Time')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            save_path = os.path.join(self.output_dir, "cost_analysis.png")
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive metrics report."""
        latency_stats = self.get_latency_stats()
        cost_stats = self.get_cost_stats()
        
        # Generate all plots
        latency_dist_path = self.plot_latency_distribution()
        latency_breakdown_path = self.plot_latency_breakdown()
        latency_over_time_path = self.plot_latency_over_time()
        cost_analysis_path = self.plot_cost_analysis()
        
        report = {
            "summary": {
                "total_queries": len(self.metrics),
                "latency_stats": latency_stats,
                "cost_stats": cost_stats,
                "target_met": latency_stats.get("p95", 0) < config.TARGET_LATENCY_MS if latency_stats else False
            },
            "plots": {
                "latency_distribution": latency_dist_path,
                "latency_breakdown": latency_breakdown_path,
                "latency_over_time": latency_over_time_path,
                "cost_analysis": cost_analysis_path
            }
        }
        
        # Save report
        report_path = os.path.join(self.output_dir, "metrics_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def export_metrics_csv(self, filepath: str = None):
        """Export metrics to CSV."""
        if not self.metrics:
            return
        
        if not filepath:
            filepath = os.path.join(self.output_dir, "metrics.csv")
        
        df = pd.DataFrame(self.metrics)
        df.to_csv(filepath, index=False)
        return filepath

