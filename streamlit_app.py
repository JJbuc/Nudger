"""Streamlit UI for interactive demo."""
import streamlit as st
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import time
from data_generators import DataGenerator
from metrics_tracker import MetricsTracker
from evaluator import Evaluator
from on_device_inference import OnDeviceInference
import config

# Page config
st.set_page_config(
    page_title="Proactive Daily Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize
if "data_generator" not in st.session_state:
    st.session_state.data_generator = DataGenerator()
if "metrics_tracker" not in st.session_state:
    st.session_state.metrics_tracker = MetricsTracker()
if "evaluator" not in st.session_state:
    st.session_state.evaluator = Evaluator()
if "on_device" not in st.session_state:
    st.session_state.on_device = None  # Lazy load

API_URL = "http://localhost:8000"

st.title("🤖 Proactive Daily Assistant Prototype")
st.markdown("An LLM-orchestrated system for context-aware nudges and suggestions")

# Sidebar
st.sidebar.header("Configuration")
use_vector_db = st.sidebar.radio(
    "Context Manager",
    ["Vector DB (FAISS)", "KV Cache"],
    index=0
)
use_vector_db_bool = use_vector_db == "Vector DB (FAISS)"

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Generate Nudges",
    "📈 Metrics & Performance",
    "🔬 Evaluation",
    "📱 On-Device Inference",
    "📚 About"
])

# Tab 1: Generate Nudges
with tab1:
    st.header("Generate Proactive Nudges")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Generate or Load Data")
        if st.button("Generate New Day Data"):
            with st.spinner("Generating fake data..."):
                data = st.session_state.data_generator.generate_day_data()
                st.session_state.current_data = data
                st.success("Data generated!")
        
        if "current_data" in st.session_state:
            st.json(st.session_state.current_data)
    
    with col2:
        st.subheader("2. Generate Nudge")
        if st.button("Generate Nudge", type="primary"):
            if "current_data" not in st.session_state:
                st.warning("Please generate data first!")
            else:
                with st.spinner("Generating nudge..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/generate_nudge",
                            json={
                                "user_data": st.session_state.current_data,
                                "use_vector_db": use_vector_db_bool
                            },
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            st.success("Nudge Generated!")
                            st.info(f"💬 **{result['nudge']}**")
                            
                            # Show details
                            with st.expander("Details"):
                                st.json(result)
                            
                            # Latency breakdown
                            st.subheader("Latency Breakdown")
                            breakdown = result.get("latency_breakdown", {})
                            if breakdown:
                                df = pd.DataFrame([
                                    {"Component": k, "Latency (ms)": v}
                                    for k, v in breakdown.items()
                                    if k != "total"
                                ])
                                st.bar_chart(df.set_index("Component"))
                            
                            # Cost
                            st.metric("Cost", f"${result.get('cost_usd', 0):.6f}")
                            st.metric("Total Latency", f"{result.get('total_latency_ms', 0):.2f}ms")
                            
                        else:
                            st.error(f"Error: {response.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("⚠️ API server not running! Please start it with: `python api_server.py`")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        if st.button("Simulate Full Day"):
            if "current_data" not in st.session_state:
                st.warning("Please generate data first!")
            else:
                with st.spinner("Simulating day..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/simulate_day",
                            json={
                                "user_data": st.session_state.current_data,
                                "use_vector_db": use_vector_db_bool
                            },
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"Generated {result['total_nudges']} nudges!")
                            
                            for i, nudge in enumerate(result["nudges"], 1):
                                st.markdown(f"**Nudge {i}:** {nudge['nudge']}")
                                st.caption(f"Latency: {nudge['latency_ms']:.2f}ms | Cost: ${nudge['cost_usd']:.6f}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Total Cost", f"${result['total_cost_usd']:.6f}")
                            with col2:
                                st.metric("Avg Latency", f"{result['avg_latency_ms']:.2f}ms")
                        else:
                            st.error(f"Error: {response.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("⚠️ API server not running!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# Tab 2: Metrics & Performance
with tab2:
    st.header("Performance Metrics & Visualization")
    
    if st.button("Refresh Metrics"):
        try:
            response = requests.get(f"{API_URL}/metrics")
            if response.status_code == 200:
                metrics = response.json()
                st.session_state.api_metrics = metrics
        
            response = requests.get(f"{API_URL}/metrics/report")
            if response.status_code == 200:
                report = response.json()
                st.session_state.metrics_report = report
        except:
            st.warning("API server not available. Using local metrics.")
    
    if "metrics_report" in st.session_state:
        report = st.session_state.metrics_report
        summary = report.get("summary", {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Queries", summary.get("total_queries", 0))
        with col2:
            latency_stats = summary.get("latency_stats", {})
            st.metric("Mean Latency", f"{latency_stats.get('mean', 0):.2f}ms")
        with col3:
            cost_stats = summary.get("cost_stats", {})
            st.metric("Total Cost", f"${cost_stats.get('total_cost_usd', 0):.6f}")
        
        # Show plots
        plots = report.get("plots", {})
        if plots:
            st.subheader("Visualizations")
            
            col1, col2 = st.columns(2)
            with col1:
                if "latency_distribution" in plots:
                    st.image(plots["latency_distribution"], caption="Latency Distribution")
                if "latency_breakdown" in plots:
                    st.image(plots["latency_breakdown"], caption="Latency Breakdown")
            
            with col2:
                if "latency_over_time" in plots:
                    st.image(plots["latency_over_time"], caption="Latency Over Time")
                if "cost_analysis" in plots:
                    st.image(plots["cost_analysis"], caption="Cost Analysis")
    else:
        st.info("Click 'Refresh Metrics' to load performance data")

# Tab 3: Evaluation
with tab3:
    st.header("Evaluation & Trade-off Analysis")
    
    if st.button("Run Evaluation"):
        with st.spinner("Running evaluation..."):
            try:
                # Get recent predictions from API
                response = requests.get(f"{API_URL}/metrics")
                if response.status_code == 200:
                    # For demo, use golden dataset
                    evaluator = st.session_state.evaluator
                    golden_data = evaluator.golden_dataset[:10]  # Sample
                    
                    # Generate predictions
                    predictions = []
                    for golden in golden_data:
                        # Create user data from context
                        user_data = {
                            "calendar": [],
                            "emails": [{"subject": "Test", "body": golden["context"]}],
                            "fitness": [],
                            "music": []
                        }
                        
                        try:
                            api_response = requests.post(
                                f"{API_URL}/generate_nudge",
                                json={"user_data": user_data, "use_vector_db": use_vector_db_bool},
                                timeout=30
                            )
                            if api_response.status_code == 200:
                                result = api_response.json()
                                predictions.append({
                                    "nudge": result["nudge"],
                                    "total_latency_ms": result["total_latency_ms"],
                                    "cost_usd": result["cost_usd"]
                                })
                        except:
                            pass
                    
                    if predictions:
                        results = evaluator.batch_evaluate(predictions, golden_data[:len(predictions)])
                        
                        st.subheader("Evaluation Results")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Semantic Similarity", f"{results.get('mean_semantic_similarity', 0):.3f}")
                        with col2:
                            st.metric("ROUGE-L", f"{results.get('mean_rougeL', 0):.3f}")
                        with col3:
                            st.metric("Overall Score", f"{results.get('mean_overall_score', 0):.3f}")
                        
                        st.json(results)
            except Exception as e:
                st.error(f"Evaluation error: {str(e)}")

# Tab 4: On-Device Inference
with tab4:
    st.header("On-Device Inference Pilot")
    
    st.info("This simulates edge deployment using a local model (Phi-3-mini)")
    
    if st.button("Load On-Device Model"):
        with st.spinner("Loading model (this may take a minute)..."):
            try:
                if st.session_state.on_device is None:
                    st.session_state.on_device = OnDeviceInference()
                st.success("Model loaded!")
            except Exception as e:
                st.error(f"Error loading model: {str(e)}")
    
    if st.session_state.on_device and st.session_state.on_device.pipeline:
        context = st.text_area("Context", "Email: Feeling stressed about deadline. Fitness: Just finished workout.")
        analysis = st.text_area("Analysis", "User is stressed and just finished a workout.")
        
        if st.button("Generate Nudge (On-Device)"):
            with st.spinner("Generating..."):
                result = st.session_state.on_device.generate_nudge(context, analysis)
                
                st.success("Generated!")
                st.info(f"💬 **{result['nudge']}**")
                st.metric("Latency", f"{result['latency_ms']:.2f}ms")
                st.metric("Tokens", result['tokens'])
    else:
        st.warning("On-device model not loaded. Click 'Load On-Device Model' first.")

# Tab 5: About
with tab5:
    st.header("About")
    st.markdown("""
    ## Proactive Daily Assistant Prototype
    
    This is a production-grade LLM-orchestrated system that generates context-aware nudges
    based on user data from multiple sources (calendar, emails, fitness, music).
    
    ### Key Features:
    - **LLM Orchestration**: LangGraph-based workflow with multi-step reasoning
    - **Context Management**: Vector DB (FAISS) vs KV Cache benchmarking
    - **Performance**: Sub-500ms latency target with detailed tracking
    - **Evaluation**: Automated accuracy, latency, and cost trade-off analysis
    - **On-Device Inference**: Edge deployment simulation
    - **Production API**: FastAPI server with comprehensive endpoints
    
    ### Architecture:
    1. **Data Ingestion**: Simulated user data streams
    2. **Context Retrieval**: Semantic search or keyword matching
    3. **LLM Analysis**: Mood and needs inference
    4. **Nudge Generation**: Personalized, actionable suggestions
    
    ### Performance Targets:
    - End-to-end latency: <500ms
    - Context retrieval: <200ms
    - Cost tracking and optimization
    """)

if __name__ == "__main__":
    st.info("💡 Make sure the API server is running: `python api_server.py`")

