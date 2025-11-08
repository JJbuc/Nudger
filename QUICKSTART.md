# Quick Start Guide

Get the Proactive Daily Assistant up and running in 5 minutes!

## Prerequisites

- Python 3.8+
- Groq API key ([Get one here](https://console.groq.com/))

## Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up environment**:
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

3. **Download NLTK data** (for evaluation):
```python
python -c "import nltk; nltk.download('punkt')"
```

## Running the Demo

### Option 1: Quick Demo Script (Recommended)

**Windows**:
```bash
run_demo.bat
```

**Linux/Mac**:
```bash
chmod +x run_demo.sh
./run_demo.sh
```

### Option 2: Manual Steps

1. **Generate sample data**:
```python
python -c "from data_generators import DataGenerator; DataGenerator().save_day_data()"
```

2. **Start API server** (in one terminal):
```bash
python api_server.py
```

3. **Start Streamlit UI** (in another terminal):
```bash
streamlit run streamlit_app.py
```

4. **Open browser**: Navigate to `http://localhost:8501`

## Running Benchmarks

To run comprehensive benchmarks and generate reports:

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

## Testing the API

### Generate a single nudge:
```bash
curl -X POST "http://localhost:8000/generate_nudge" \
  -H "Content-Type: application/json" \
  -d '{
    "user_data": {
      "calendar": [{"time": "2024-01-01 10:00:00", "title": "Meeting", "description": "Team sync"}],
      "emails": [{"time": "2024-01-01 09:00:00", "subject": "Urgent", "body": "Need help", "sender": "boss@company.com", "priority": "high"}],
      "fitness": [{"time": "2024-01-01 08:00:00", "steps": 5000, "heart_rate": 120, "calories_burned": 200, "activity_type": "running"}],
      "music": [{"time": "2024-01-01 07:00:00", "track_name": "Energy Boost", "artist": "The Beats", "genre": "electronic", "mood": "upbeat"}]
    },
    "use_vector_db": true
  }'
```

### Get metrics:
```bash
curl http://localhost:8000/metrics
```

## Project Structure

- `api_server.py` - FastAPI server
- `streamlit_app.py` - Interactive UI
- `main.py` - Benchmark script
- `data_generators.py` - Fake data generation
- `llm_orchestrator.py` - LangGraph orchestration
- `context_manager.py` - Vector DB & KV Cache
- `metrics_tracker.py` - Performance tracking
- `evaluator.py` - Evaluation pipeline
- `on_device_inference.py` - Edge inference

## Troubleshooting

### "API server not running"
- Make sure `python api_server.py` is running in a separate terminal
- Check that port 8000 is not in use

### "GROQ_API_KEY not found"
- Verify your `.env` file exists and contains `GROQ_API_KEY=your_key_here`
- Make sure you're in the project root directory

### Import errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Try upgrading packages: `pip install --upgrade -r requirements.txt`

### LangGraph import issues
- LangGraph is actively developed, versions may vary
- The code includes fallback imports for compatibility

## Next Steps

1. **Customize data**: Edit `data_generators.py` to create your own data patterns
2. **Adjust targets**: Modify `config.py` to change latency/cost targets
3. **Add sources**: Extend data ingestion to include more data types
4. **Deploy**: Use the FastAPI server for production deployment

## Support

Check the main [README.md](README.md) for detailed documentation.

