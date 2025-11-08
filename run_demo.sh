#!/bin/bash
# Quick start script for the Proactive Daily Assistant

echo "🚀 Starting Proactive Daily Assistant Demo"
echo "=========================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "Please edit .env and add your GROQ_API_KEY"
    exit 1
fi

# Check if API key is set
if ! grep -q "GROQ_API_KEY=.*[^your_groq_api_key_here]" .env; then
    echo "⚠️  Please set your GROQ_API_KEY in .env file"
    exit 1
fi

echo ""
echo "1. Generating sample data..."
python -c "from data_generators import DataGenerator; DataGenerator().save_day_data()"

echo ""
echo "2. Starting API server in background..."
python api_server.py &
API_PID=$!
sleep 3

echo ""
echo "3. Starting Streamlit UI..."
echo "   Open http://localhost:8501 in your browser"
streamlit run streamlit_app.py

# Cleanup
echo ""
echo "Stopping API server..."
kill $API_PID 2>/dev/null

echo "✅ Demo complete!"

