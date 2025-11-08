"""FastAPI server for production-like deployment."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
from llm_orchestrator import LLMOrchestrator
from metrics_tracker import MetricsTracker
from evaluator import Evaluator
import config

app = FastAPI(title="Proactive Daily Assistant API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
orchestrator = None
metrics_tracker = MetricsTracker()
evaluator = Evaluator()

class UserData(BaseModel):
    calendar: List[Dict[str, Any]] = []
    emails: List[Dict[str, Any]] = []
    fitness: List[Dict[str, Any]] = []
    music: List[Dict[str, Any]] = []

class NudgeRequest(BaseModel):
    user_data: UserData
    use_vector_db: bool = True

class NudgeResponse(BaseModel):
    nudge: str
    latency_breakdown: Dict[str, float]
    total_latency_ms: float
    cost_usd: float
    cost_tokens: Dict[str, int]
    context: Optional[str] = None
    analysis: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize orchestrator on startup."""
    global orchestrator
    orchestrator = LLMOrchestrator(use_vector_db=True)
    print("Orchestrator initialized")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Proactive Daily Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "/generate_nudge": "POST - Generate a proactive nudge",
            "/simulate_day": "POST - Simulate a full day of nudges",
            "/metrics": "GET - Get performance metrics",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "orchestrator_loaded": orchestrator is not None}

@app.post("/generate_nudge", response_model=NudgeResponse)
async def generate_nudge(request: NudgeRequest):
    """Generate a single proactive nudge."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        # Create orchestrator with specified context manager
        temp_orchestrator = LLMOrchestrator(use_vector_db=request.use_vector_db)
        
        user_data_dict = request.user_data.dict()
        result = temp_orchestrator.generate_nudge(user_data_dict)
        
        # Calculate cost
        tokens = result.get("cost_tokens", {"input": 0, "output": 0})
        cost_usd = (
            tokens["input"] * config.COST_PER_INPUT_TOKEN +
            tokens["output"] * config.COST_PER_OUTPUT_TOKEN
        )
        
        # Record metric
        metrics_tracker.record_metric({
            "total_latency_ms": result.get("latency_breakdown", {}).get("total", 0),
            "latency_breakdown": result.get("latency_breakdown", {}),
            "cost_usd": cost_usd,
            "cost_tokens": tokens,
            "nudge": result.get("nudge", "")
        })
        
        return NudgeResponse(
            nudge=result.get("nudge", "No nudge generated"),
            latency_breakdown=result.get("latency_breakdown", {}),
            total_latency_ms=result.get("latency_breakdown", {}).get("total", 0),
            cost_usd=cost_usd,
            cost_tokens=tokens,
            context=result.get("context"),
            analysis=result.get("analysis")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating nudge: {str(e)}")

@app.post("/simulate_day")
async def simulate_day(request: NudgeRequest):
    """Simulate a full day with multiple nudges."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        user_data_dict = request.user_data.dict()
        temp_orchestrator = LLMOrchestrator(use_vector_db=request.use_vector_db)
        
        # Generate nudges at different times
        nudges = []
        all_results = []
        
        # Simulate 5 nudges throughout the day
        for i in range(5):
            result = temp_orchestrator.generate_nudge(user_data_dict)
            
            tokens = result.get("cost_tokens", {"input": 0, "output": 0})
            cost_usd = (
                tokens["input"] * config.COST_PER_INPUT_TOKEN +
                tokens["output"] * config.COST_PER_OUTPUT_TOKEN
            )
            
            nudge_data = {
                "nudge": result.get("nudge", ""),
                "latency_ms": result.get("latency_breakdown", {}).get("total", 0),
                "cost_usd": cost_usd,
                "timestamp": f"Day {i+1}"
            }
            nudges.append(nudge_data)
            all_results.append({**result, "cost_usd": cost_usd})
            
            # Record metric
            metrics_tracker.record_metric({
                "total_latency_ms": result.get("latency_breakdown", {}).get("total", 0),
                "latency_breakdown": result.get("latency_breakdown", {}),
                "cost_usd": cost_usd,
                "cost_tokens": tokens
            })
        
        return {
            "nudges": nudges,
            "total_nudges": len(nudges),
            "total_cost_usd": sum(n["cost_usd"] for n in nudges),
            "avg_latency_ms": sum(n["latency_ms"] for n in nudges) / len(nudges) if nudges else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error simulating day: {str(e)}")

@app.get("/metrics")
async def get_metrics():
    """Get performance metrics."""
    latency_stats = metrics_tracker.get_latency_stats()
    cost_stats = metrics_tracker.get_cost_stats()
    
    return {
        "latency": latency_stats,
        "cost": cost_stats,
        "total_queries": len(metrics_tracker.metrics)
    }

@app.get("/metrics/report")
async def get_metrics_report():
    """Generate and return comprehensive metrics report."""
    report = metrics_tracker.generate_report()
    return report

@app.post("/evaluate")
async def evaluate_nudges(predictions: List[Dict[str, Any]]):
    """Evaluate nudges against golden dataset."""
    results = evaluator.batch_evaluate(predictions)
    return results

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

