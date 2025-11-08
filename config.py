"""Configuration settings for the Proactive Daily Assistant."""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Model Configuration
GROQ_MODEL = "llama-3.1-70b-versatile"  # Fast model for low latency
ON_DEVICE_MODEL = "microsoft/Phi-3-mini-4k-instruct"  # Small model for on-device

# Performance Targets
TARGET_LATENCY_MS = 500
CONTEXT_RETRIEVAL_TARGET_MS = 200

# Evaluation
GOLDEN_DATASET_SIZE = 50
BENCHMARK_SAMPLES = 200

# Cost Estimation (approximate Groq pricing)
COST_PER_INPUT_TOKEN = 0.0000001  # $0.0001 per 1K tokens
COST_PER_OUTPUT_TOKEN = 0.0000001

# Data Paths
DATA_DIR = "data"
OUTPUT_DIR = "outputs"
MODELS_DIR = "models"

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

