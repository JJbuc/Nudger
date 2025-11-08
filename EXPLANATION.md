# Proactive Daily Assistant - Simple Explanation

## 🎯 What I Built

A **smart AI assistant** that watches your day (calendar, emails, fitness, music) and **proactively suggests helpful actions** before you even ask. Think of it like having a thoughtful friend who notices you're stressed and suggests "Hey, you just worked out and have a deadline email - take 5 minutes to breathe first."

---

## 🏗️ How It Works (Simple Version)

```
┌─────────────┐
│  Your Data  │  ← Calendar, Emails, Fitness, Music
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Find Context   │  ← "What's relevant right now?"
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Analyze Mood   │  ← "Are they stressed? Happy? Tired?"
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Generate Nudge │  ← "Here's a helpful suggestion"
└─────────────────┘
```

**Example Flow**:
1. **Input**: "Email: 'Urgent deadline!' | Fitness: Just ran 5 miles | Music: Upbeat tracks"
2. **Context**: Finds related stress indicators and activity patterns
3. **Analysis**: "User is stressed about deadline, just exercised, needs recovery"
4. **Nudge**: "You've been working hard! After your run, consider hydrating and taking 5 minutes to breathe before tackling that deadline - your body needs recovery time."

---

## 🚀 How to Run It (Step-by-Step)

### Step 1: Get Groq API Key ⚠️ REQUIRED

**Why**: The system uses Groq's super-fast AI to generate suggestions in under 500ms.

1. Go to: **https://console.groq.com/**
2. Sign up (free account works!)
3. Click "API Keys" in the menu
4. Click "Create API Key"
5. Copy the key (starts with `gsk_...`)

**Cost**: Free tier is generous enough for this project!

### Step 2: Install Everything

```bash
# Make sure Python 3.8+ is installed
python --version

# Install all the code libraries
pip install -r requirements.txt
```

**This takes 2-5 minutes** - it's downloading AI models, web frameworks, etc.

### Step 3: Set Up Your API Key

```bash
# Copy the example file
cp .env.example .env

# Edit it (Windows: notepad .env | Mac: nano .env)
# Add this line:
GROQ_API_KEY=gsk_your_actual_key_here
```

**Important**: Replace `gsk_your_actual_key_here` with your actual key from Step 1!

### Step 4: Download Language Data

```bash
python -c "import nltk; nltk.download('punkt')"
```

This downloads text processing data (one-time setup).

### Step 5: Run It!

**Option A - Easy Way (Windows)**:
```bash
run_demo.bat
```

**Option A - Easy Way (Mac/Linux)**:
```bash
chmod +x run_demo.sh
./run_demo.sh
```

**Option B - Manual Way**:

Terminal 1:
```bash
python api_server.py
```
Wait for: `Uvicorn running on http://0.0.0.0:8000`

Terminal 2:
```bash
streamlit run streamlit_app.py
```
Wait for: `Local URL: http://localhost:8501`

Then open your browser to: **http://localhost:8501**

---

## 📊 What You'll See

### In the Browser (Streamlit UI)

1. **"Generate Nudges" Tab**:
   - Click "Generate New Day Data" → Creates fake calendar/emails/fitness data
   - Click "Generate Nudge" → See a personalized suggestion appear!
   - See breakdown: "Ingestion: 50ms, Retrieval: 120ms, LLM: 280ms, Total: 450ms"
   - See cost: "$0.000123 per query"

2. **"Metrics & Performance" Tab**:
   - Beautiful graphs showing how fast the system is
   - Histogram of response times
   - Cost analysis

3. **"Evaluation" Tab**:
   - How accurate the suggestions are
   - Comparison of different approaches

### In the Terminal

When you run `python main.py`, you'll see:
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
   Progress: 5/10
   Progress: 10/10
   ✓ Benchmark complete

4. Generating metrics report...
   Mean Latency: 387.45ms
   P95 Latency: 456.23ms
   Target Met (<500ms): True
   Total Cost: $0.001234
```

### Generated Files

After running benchmarks, check the `outputs/` folder:
- `latency_distribution.png` - Graph of how fast responses are
- `metrics_report.json` - All the numbers
- `configuration_comparison.json` - Which approach is better

---

## 💡 Why This Matters

### The Problem

Most AI assistants are **reactive** - you ask, they answer. This is **proactive** - it notices patterns and suggests actions.

### Real-World Impact

1. **Health & Wellness**: "You've been sitting 4 hours, time for a walk"
2. **Productivity**: "You have a meeting in 30 min, here's a quick prep checklist"
3. **Mental Health**: "You seem stressed, here's a 2-minute breathing exercise"
4. **Work-Life Balance**: "You worked late 3 days this week, consider blocking time for rest"

### Technical Innovation

This isn't just "an AI that talks" - it demonstrates:

1. **Production-Grade Engineering**:
   - Multi-step workflows (not just one AI call)
   - Error handling (what if API fails?)
   - Performance monitoring (tracking every millisecond)
   - Cost tracking (knowing exactly how much each query costs)

2. **Data-Driven Decisions**:
   - Tests multiple approaches (Vector DB vs KV Cache)
   - Measures which is better (speed vs accuracy)
   - Makes informed choices based on data

3. **Real Performance Targets**:
   - Sub-500ms latency (faster than human reaction time)
   - Cost optimization (tracks every penny)
   - Accuracy measurement (ensures suggestions are actually helpful)

### Who Would Use This?

- **Product Teams**: Building AI features that need to be fast and reliable
- **ML Engineers**: Learning how to orchestrate complex AI workflows
- **Researchers**: Studying how to balance speed, accuracy, and cost
- **Startups**: Prototyping AI products with production-ready code

---

## 🔧 What Else You Need to Know

### File Structure

```
Nudger/
├── api_server.py          ← The web server (FastAPI)
├── streamlit_app.py       ← The user interface
├── main.py                ← Run benchmarks here
├── data_generators.py     ← Creates fake data
├── llm_orchestrator.py    ← The "brain" - coordinates everything
├── context_manager.py     ← Finds relevant information
├── metrics_tracker.py     ← Measures performance
├── evaluator.py           ← Checks if suggestions are good
├── on_device_inference.py ← Runs AI on your computer (no internet)
├── config.py              ← Settings (change models, targets here)
└── .env                   ← YOUR API KEY GOES HERE
```

### Key Files to Understand

**Start here**:
1. `main.py` - Shows the full flow
2. `llm_orchestrator.py` - The orchestration logic
3. `streamlit_app.py` - The UI code

**Then explore**:
- `context_manager.py` - How it finds relevant info
- `data_generators.py` - How fake data is created
- `config.py` - All the settings

### Common Issues & Fixes

**"Module not found"**:
```bash
pip install --upgrade -r requirements.txt
```

**"API key invalid"**:
- Check `.env` file exists
- Make sure key starts with `gsk_`
- No extra spaces in the file

**"Port already in use"**:
- Close other programs using port 8000
- Or change port in `api_server.py`

**"Slow performance"**:
- Check internet (needs connection for Groq API)
- Try smaller model in `config.py`

### Customization

**Change the AI model**:
Edit `config.py`, line with `GROQ_MODEL = "llama-3.1-70b-versatile"`

**Change latency target**:
Edit `config.py`, line with `TARGET_LATENCY_MS = 500`

**Add real data**:
Modify `data_generators.py` to connect to real APIs (Google Calendar, Gmail, etc.)

---

## 🎤 How to Explain This to Others

### 30-Second Pitch

"It's an AI assistant that watches your day and proactively suggests helpful actions. Instead of asking 'What should I do?', it notices patterns and says 'Hey, you seem stressed - here's a quick way to reset.' It's built with production-grade engineering, hitting sub-500ms response times with full cost tracking."

### 2-Minute Explanation

"Most AI assistants are reactive - you ask, they answer. This is proactive - it analyzes your calendar, emails, fitness data, and music preferences to understand your context, then generates personalized suggestions.

The technical innovation is in the orchestration - it's not just one AI call, but a coordinated workflow: ingest data, find relevant context, analyze mood, generate suggestion. Every step is measured for latency and cost.

We benchmark multiple approaches (semantic search vs keyword matching) and make data-driven decisions. The system hits sub-500ms latency targets while tracking costs and measuring accuracy. It's production-ready code that demonstrates real-world AI system design."

### For Technical Audience

Focus on:
- LangGraph orchestration patterns
- Vector DB vs KV Cache trade-offs
- Performance optimization techniques
- Production patterns (error handling, observability)

### For Business Audience

Focus on:
- Real-world applications (proactive assistance)
- User experience benefits
- Cost efficiency at scale
- Market opportunity

---

## 📈 Next Steps

### Immediate
1. ✅ Get Groq API key
2. ✅ Install dependencies
3. ✅ Set up `.env` file
4. ✅ Run the demo
5. ✅ Explore the code

### Short-term
- Modify prompts to change nudge style
- Add more data sources
- Customize the UI
- Deploy to cloud (Render, Railway, etc.)

### Long-term
- Integrate real APIs (Google Calendar, Gmail)
- Fine-tune models on your data
- Add user feedback loop
- Build mobile app

---

## 🎓 Learning Resources

- **LangGraph**: https://langchain-ai.github.io/langgraph/ (orchestration)
- **Groq**: https://console.groq.com/docs (fast AI API)
- **FastAPI**: https://fastapi.tiangolo.com/ (web framework)
- **Streamlit**: https://docs.streamlit.io/ (UI framework)

---

## ✅ Checklist

Before presenting or demoing:

- [ ] Groq API key obtained and added to `.env`
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] NLTK data downloaded
- [ ] API server runs successfully (`python api_server.py`)
- [ ] Streamlit UI opens (`streamlit run streamlit_app.py`)
- [ ] Can generate at least one nudge successfully
- [ ] Benchmarks run (`python main.py`)
- [ ] Understand what each file does
- [ ] Can explain the architecture
- [ ] Know how to troubleshoot common issues

---

**You're ready to go! 🚀**

This is a complete, production-grade system that demonstrates real-world LLM orchestration. Use it, learn from it, extend it, or deploy it!

