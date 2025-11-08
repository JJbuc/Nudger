# Proactive Daily Assistant

A production-grade LLM-orchestrated system that generates proactive, context-aware nudges based on user data from multiple sources (calendar, emails, fitness metrics, music preferences).

## 🎯 Overview

This system acts as an intelligent background companion that analyzes your day and suggests helpful actions before you even ask. Instead of reactive assistance, it proactively notices patterns and provides timely, personalized suggestions.

### Example
> "You just finished a workout and have a stressful deadline email. Consider taking 5 minutes to hydrate and breathe before tackling that task - your body needs recovery time."

## 🏗️ Architecture

```
User Data → Data Ingestion → Context Retrieval → LLM Analysis → Nudge Generation
   ↓              ↓                  ↓                ↓              ↓
Calendar    (Structured)    (Vector DB /      (Mood/Needs    (Personalized
Emails                      KV Cache)         Inference)      Suggestions)
Fitness
Music
```

### Key Components

1. **Data Generators** - Creates realistic fake data for testing
2. **Context Managers** - Vector DB (FAISS) for semantic search or KV Cache for fast lookups
3. **LLM Orchestrator** - LangGraph-based multi-step workflow
4. **Metrics Tracker** - Performance monitoring and visualization
5. **Evaluator** - Accuracy and quality assessment
6. **FastAPI Server** - Production-ready API
7. **Streamlit UI** - Interactive demo interface

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Groq API key ([Get one here](https://console.groq.com/))

### Installation

1. **Clone and navigate to the project**:
```bash
cd Nudger
```

2. **Create virtual environment**:
```bash
python -m venv venv
```

3. **Activate virtual environment**:
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

4. **Install dependencies**:
```bash
pip install -r requirements.txt
```

5. **Set up environment variables**:
   - Create a `.env` file in the project root
   - Add: `GROQ_API_KEY=your_groq_api_key_here`
   - Get your key from: https://console.groq.com/

6. **Download NLTK data**:
```bash
python -c "import nltk; nltk.download('punkt')"
```

### Running the Application

**Terminal 1 - Start API Server**:
```bash
python api_server.py
```

**Terminal 2 - Start Streamlit UI**:
```bash
streamlit run streamlit_app.py
```

Open http://localhost:8501 in your browser.

## 📊 Features

### LLM Orchestration
- **LangGraph workflow** with explicit state management
- **Multi-step reasoning**: Ingest → Retrieve → Analyze → Generate
- **Conditional flows** and error handling
- **Latency tracking** at each step

### Context Management
- **Vector DB (FAISS)**: Semantic search for fuzzy matching
- **KV Cache**: Fast keyword-based lookups
- **Automatic benchmarking** to choose the best approach
- **Sub-200ms retrieval** target

### Performance Optimization
- **Sub-500ms end-to-end latency** target
- **Detailed latency breakdown** by component
- **Cost tracking** per query
- **Performance visualizations** (histograms, line graphs)

### Evaluation
- **Golden dataset** for accuracy measurement
- **Semantic similarity** scoring
- **ROUGE scores** for text quality
- **Trade-off analysis** (latency vs accuracy vs cost)

### Production API
- **FastAPI** server with comprehensive endpoints
- **CORS support** for web integration
- **Health checks** and metrics endpoints
- **Interactive API docs** at `/docs`

## 📁 Project Structure

```
Nudger/
├── api_server.py          # FastAPI server
├── streamlit_app.py       # Streamlit UI
├── main.py                # Benchmark script
├── config.py              # Configuration
├── data_generators.py     # Fake data generation
├── llm_orchestrator.py    # LangGraph orchestration
├── context_manager.py     # Vector DB & KV Cache
├── metrics_tracker.py     # Performance tracking
├── evaluator.py           # Evaluation pipeline
├── requirements.txt       # Dependencies
├── .env                   # Environment variables (create this)
├── data/                  # Generated data
└── outputs/               # Reports & visualizations
```

## 🔧 Configuration

Edit `config.py` to customize:
- **Model selection**: Change `GROQ_MODEL`
- **Latency targets**: Modify `TARGET_LATENCY_MS`
- **Cost estimation**: Update pricing constants
- **Evaluation parameters**: Adjust dataset sizes

## 📈 API Endpoints

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
  "nudge": "Personalized suggestion...",
  "latency_breakdown": {...},
  "total_latency_ms": 213.74,
  "cost_usd": 0.000123,
  "cost_tokens": {"input": 500, "output": 230}
}
```

### `GET /metrics`
Get performance metrics summary.

### `GET /metrics/report`
Generate comprehensive metrics report with visualizations.

### `GET /docs`
Interactive API documentation.

## 🎓 Key Decisions

### Context Management
- **Chosen**: Vector DB (FAISS) for better semantic understanding
- **Rationale**: User data is diverse, requiring semantic search
- **Trade-off**: ~100ms latency increase for 15-20% better relevance

### LLM Selection
- **Chosen**: Groq API (Llama-3.3-70b)
- **Rationale**: Fast inference (<200ms), cost-effective, production-ready

### Orchestration
- **Chosen**: LangGraph
- **Rationale**: Explicit workflow, easy to debug, supports conditional flows

## 📊 Performance Metrics

- **Mean Latency**: ~200-300ms (well under 500ms target)
- **P95 Latency**: ~250-350ms
- **Cost per Query**: ~$0.0001-0.0002
- **Accuracy**: Measured via semantic similarity and ROUGE scores

## 🧪 Running Benchmarks

```bash
python main.py
```

This will:
- Generate test data
- Benchmark context managers
- Run orchestrator tests
- Generate performance visualizations
- Create evaluation reports

Results are saved to the `outputs/` directory.

## 🚢 Deployment

The FastAPI server is production-ready. Deploy to:
- **Render**: Connect GitHub repo, auto-deploys
- **Railway**: One-click deployment
- **AWS/GCP**: Use Docker container

For Streamlit UI:
- **Streamlit Cloud**: Free hosting
- **Hugging Face Spaces**: Free with GPU option

## 📝 License

MIT License

## 🙏 Acknowledgments

- Groq for fast LLM inference
- LangChain/LangGraph for orchestration
- Hugging Face for transformers
- FAISS for vector search

---

**Built to demonstrate production-grade LLM orchestration with rigorous performance metrics**
