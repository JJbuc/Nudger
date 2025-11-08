@echo off
REM Quick start script for Windows

echo 🚀 Starting Proactive Daily Assistant Demo
echo ==========================================

REM Check if .env exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from template...
    copy .env.example .env
    echo Please edit .env and add your GROQ_API_KEY
    exit /b 1
)

echo.
echo 1. Generating sample data...
python -c "from data_generators import DataGenerator; DataGenerator().save_day_data()"

echo.
echo 2. Starting API server...
start "API Server" python api_server.py
timeout /t 3 /nobreak >nul

echo.
echo 3. Starting Streamlit UI...
echo    Open http://localhost:8501 in your browser
streamlit run streamlit_app.py

echo.
echo ✅ Demo complete!
echo    Press any key to exit...
pause >nul

