# Proactive Daily Assistant Prototype

An LLM-orchestrated system that acts as a lightweight, background intelligent companion, generating proactive, context-aware nudges based on user data from multiple sources (calendar, emails, fitness metrics, music preferences).

## 🎯 Key Features

- **LLM Orchestration**: LangGraph-based multi-step workflow with conditional flows
- **Context Management**: Benchmarking of Vector DB (FAISS) vs KV Cache with data-driven decision
- **Performance Optimization**: Sub-500ms latency target with comprehensive tracking
- **Evaluation Pipeline**: Automated accuracy, latency, and cost trade-off analysis
- **On-Device Inference**: Edge deployment simulation using Hugging Face Transformers
- **Production API**: FastAPI server with comprehensive endpoints
- **Interactive UI**: Streamlit dashboard for real-time demo and visualization

## 🏗️ Architecture

```
User Data → Data Ingestion → Context Retrieval → LLM Analysis → Nudge Generation → Output
                ↓                    ↓                ↓              ↓
         (Calendar, Email,    (Vector DB /      (Mood/Needs    (Personalized
          Fitness, Music)      KV Cache)        Inference)      Suggestions)
```

### Orchestration Graph (LangGraph)

1. **Ingest Data**: Process and structure user data from multiple sources
2. **Retrieve Context**: Semantic search (Vector DB) or keyword matching (KV Cache)
3. **Analyze Context**: LLM infers mood, stress level, and immediate needs
4. **Generate Nudge**: Create personalized, actionable suggestions

## 📦 Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd Nudger
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

4. **Download NLTK data** (for evaluation):
```python
import nltk
nltk.download('punkt')
```

## 🚀 Quick Start

### 1. Generate Fake Data
```python
from data_generators import DataGenerator

generator = DataGenerator()
data = generator.generate_day_data()
generator.save_day_data("my_day.json")
```

### 2. Run Benchmarks
```bash
python main.py
```

This will:
- Generate test data
- Benchmark context managers (Vector DB vs KV Cache)
- Run orchestrator benchmarks
- Generate performance reports and visualizations
- Run evaluation pipeline
- Compare configurations

### 3. Start API Server
```bash
python api_server.py
```

The API will be available at `http://localhost:8000`

### 4. Launch Streamlit UI
```bash
streamlit run streamlit_app.py
```

Open `http://localhost:8501` in your browser.

## 📊 API Endpoints

### `POST /generate_nudge`
Generate a single proactive nudge.

**Request**:
```json
{
  "user_data": {
    "calendar": [...],
    "emails": [...],
    "fitness": [...],
    "music": [...]
  },
  "use_vector_db": true
}
```

**Response**:
```json
{
  "nudge": "You've been working hard! Take a moment to breathe...",
  "latency_breakdown": {...},
  "total_latency_ms": 342.5,
  "cost_usd": 0.000123,
  "cost_tokens": {"input": 500, "output": 230}
}
```

### `POST /simulate_day`
Simulate a full day with multiple nudges.

### `GET /metrics`
Get performance metrics summary.

### `GET /metrics/report`
Generate comprehensive metrics report with visualizations.

## 🔬 Evaluation & Benchmarks

### Context Management Decision

The system benchmarks both Vector DB (FAISS) and KV Cache approaches:

- **Vector DB (FAISS)**: 
  - Pros: Semantic search, better for fuzzy matches, handles diverse data
  - Cons: Higher latency (~200-300ms), requires embeddings
  - Best for: Email analysis, mood inference from text

- **KV Cache**:
  - Pros: Very fast (~50-150ms), exact lookups, low memory
  - Cons: Keyword-based, less flexible
  - Best for: Calendar lookups, time-based queries

**Decision Logic**: Vector DB is chosen if relevance is >10% better; otherwise KV Cache for speed.

### Performance Targets

- **End-to-End Latency**: <500ms (target)
- **Context Retrieval**: <200ms
- **P95 Latency**: <500ms
- **Cost per Query**: ~$0.0001-0.0002

### Metrics Tracked

- Latency breakdown by component
- Token usage and cost
- Accuracy (semantic similarity, ROUGE scores)
- Configuration comparisons

## 📈 Visualizations

The system generates several visualizations:

1. **Latency Distribution**: Histogram of end-to-end latencies
2. **Latency Breakdown**: Component-wise latency analysis
3. **Latency Over Time**: Trend analysis
4. **Cost Analysis**: Per-query and cumulative cost

All visualizations are saved to `outputs/` directory.

## 🔧 Configuration

Edit `config.py` to customize:

- Model selection (Groq API)
- Performance targets
- Cost estimation
- Evaluation parameters

## 📱 On-Device Inference

The system includes a pilot for on-device inference using Hugging Face Transformers:

- Model: `microsoft/Phi-3-mini-4k-instruct`
- Quantized for faster inference
- Zero network cost, higher latency
- Useful for offline scenarios

## 🧪 Testing

Run the benchmark suite:
```bash
python main.py
```

This will:
1. Generate test data
2. Benchmark context managers
3. Run orchestrator with multiple configurations
4. Generate evaluation reports
5. Create visualizations

## 📁 Project Structure

```
Nudger/
├── api_server.py          # FastAPI server
├── streamlit_app.py       # Streamlit UI
├── main.py                # Benchmark script
├── config.py              # Configuration
├── data_generators.py     # Fake data generation
├── context_manager.py     # Vector DB & KV Cache
├── llm_orchestrator.py    # LangGraph orchestration
├── on_device_inference.py # Edge inference
├── metrics_tracker.py     # Performance tracking
├── evaluator.py           # Evaluation pipeline
├── requirements.txt       # Dependencies
├── data/                  # Generated data
├── outputs/               # Reports & visualizations
└── models/                # Local models (if any)
```

## 🎓 Key Decisions & Trade-offs

### 1. Context Management
- **Chosen**: Vector DB (FAISS) for better semantic understanding
- **Rationale**: User data is diverse (emails, calendar, fitness) requiring semantic search
- **Trade-off**: ~100ms latency increase for 15-20% better relevance

### 2. LLM Selection
- **Chosen**: Groq API (Llama-3.1-70b)
- **Rationale**: Fast inference (<200ms), cost-effective, production-ready
- **Alternative**: On-device for offline, but 2-3x slower

### 3. Orchestration
- **Chosen**: LangGraph
- **Rationale**: Explicit workflow, easy to debug, supports conditional flows
- **Benefits**: Clear latency breakdown, easy to optimize individual steps

### 4. Evaluation Metrics
- **Semantic Similarity**: Captures meaning beyond exact words
- **ROUGE Scores**: Standard NLP evaluation
- **Overall Score**: Weighted combination for balanced assessment

## 🚢 Production Deployment

The FastAPI server is production-ready with:
- CORS middleware
- Error handling
- Health checks
- Metrics endpoints
- Comprehensive logging

Deploy to:
- **Vercel**: Use serverless functions
- **Render**: Direct deployment
- **Hugging Face Spaces**: For Streamlit UI
- **Docker**: Containerize for any platform

## 📝 Example Output

```
🚀 Starting Proactive Daily Assistant Benchmark Suite
============================================================

1. Generating fake data...
   ✓ Generated data with 5 calendar events, 8 emails, 6 fitness readings, 10 music tracks

2. Benchmarking context managers...
   Vector DB - Avg Latency: 245.32ms, Avg Relevance: 0.847
   KV Cache - Avg Latency: 89.12ms, Avg Relevance: 0.723
   ✓ Decision: Using Vector DB

3. Running orchestrator benchmarks...
   Running 10 nudge generations...
   Progress: 5/10
   Progress: 10/10
   ✓ Benchmark complete

4. Generating metrics report...
   Mean Latency: 387.45ms
   P95 Latency: 456.23ms
   Target Met (<500ms): True
   Total Cost: $0.001234
   Avg Cost per Query: $0.000123
```

## 🔮 Future Enhancements

- Fine-tuning on domain-specific data
- Multi-modal inputs (images, audio)
- Real-time streaming updates
- Advanced caching strategies
- A/B testing framework
- User feedback loop

## 📄 License

MIT License

## 🙏 Acknowledgments

- Groq for fast LLM inference
- LangChain/LangGraph for orchestration
- Hugging Face for transformers
- FAISS for vector search

---

**Built with ❤️ for production-grade LLM orchestration**

