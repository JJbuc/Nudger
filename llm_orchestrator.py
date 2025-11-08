"""LLM orchestration using LangGraph for multi-step workflows."""
import time
import os
from typing import Dict, Any, List, Optional
try:
    from langchain_groq import ChatGroq
except ImportError:
    try:
        # Try alternative import
        from langchain_community.chat_models import ChatGroq
    except ImportError:
        # Use groq directly and wrap it
        from groq import Groq
        from langchain_core.language_models.chat_models import BaseChatModel
        from langchain_core.messages import AIMessage
        
        class ChatGroqWrapper:
            """Simple wrapper for Groq API compatible with LangChain."""
            def __init__(self, groq_api_key, model_name, temperature=0.7):
                self.client = Groq(api_key=groq_api_key)
                self.model_name = model_name
                self.temperature = temperature
            
            def invoke(self, messages, **kwargs):
                # Convert langchain messages to groq format
                groq_messages = []
                for msg in messages:
                    if hasattr(msg, 'content'):
                        groq_messages.append({"role": "user", "content": msg.content})
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=groq_messages,
                    temperature=self.temperature
                )
                
                # Create a response object with content and metadata
                class Response:
                    def __init__(self, content, usage):
                        self.content = content
                        self.response_metadata = {"usage": usage}
                
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else 0,
                    "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else 0,
                    "total_tokens": response.usage.total_tokens if hasattr(response, 'usage') else 0
                }
                
                return Response(
                    content=response.choices[0].message.content,
                    usage=usage
                )
        
        ChatGroq = ChatGroqWrapper
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
try:
    from langgraph.graph import StateGraph, END
except ImportError:
    # Fallback for older versions
    from langgraph.graph.state import StateGraph
    from langgraph.graph import END
import config
from context_manager import VectorDBContextManager, KVCacheContextManager, ContextResult

class OrchestratorState:
    """State for the orchestration graph."""
    def __init__(self):
        self.messages: List[BaseMessage] = []
        self.context: str = ""
        self.user_data: Dict[str, Any] = {}
        self.nudge: Optional[str] = None
        self.latency_breakdown: Dict[str, float] = {}
        self.cost_tokens: Dict[str, int] = {"input": 0, "output": 0}
        self.error: Optional[str] = None

class LLMOrchestrator:
    """Main orchestrator using LangGraph."""
    
    def __init__(self, use_vector_db: bool = True):
        self.llm = ChatGroq(
            groq_api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL,
            temperature=0.7
        )
        self.context_manager = VectorDBContextManager() if use_vector_db else KVCacheContextManager()
        self.use_vector_db = use_vector_db
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph orchestration graph."""
        workflow = StateGraph(dict)
        
        # Define nodes
        workflow.add_node("ingest_data", self._ingest_data)
        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("analyze_context", self._analyze_context)
        workflow.add_node("generate_nudge", self._generate_nudge)
        
        # Define edges
        workflow.set_entry_point("ingest_data")
        workflow.add_edge("ingest_data", "retrieve_context")
        workflow.add_edge("retrieve_context", "analyze_context")
        workflow.add_edge("analyze_context", "generate_nudge")
        workflow.add_edge("generate_nudge", END)
        
        return workflow.compile()
    
    def _ingest_data(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node: Ingest and prepare user data."""
        start_time = time.perf_counter()
        
        user_data = state.get("user_data", {})
        
        # Prepare contexts for context manager
        contexts = []
        for event in user_data.get("calendar", []):
            contexts.append({**event, "type": "calendar"})
        for email in user_data.get("emails", []):
            contexts.append({**email, "type": "email"})
        for fitness in user_data.get("fitness", []):
            contexts.append({**fitness, "type": "fitness"})
        for music in user_data.get("music", []):
            contexts.append({**music, "type": "music"})
        
        self.context_manager.add_contexts(contexts)
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        state["latency_breakdown"] = state.get("latency_breakdown", {})
        state["latency_breakdown"]["ingestion"] = latency_ms
        
        return state
    
    def _retrieve_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node: Retrieve relevant context."""
        start_time = time.perf_counter()
        
        # Create query from recent data
        user_data = state.get("user_data", {})
        query_parts = []
        
        # Get most recent email
        if user_data.get("emails"):
            latest_email = user_data["emails"][-1]
            query_parts.append(f"Recent email: {latest_email.get('subject', '')}")
        
        # Get current activity
        if user_data.get("fitness"):
            latest_fitness = user_data["fitness"][-1]
            query_parts.append(f"Current activity: {latest_fitness.get('activity_type', '')}")
        
        query = " ".join(query_parts) if query_parts else "user context and mood"
        
        result: ContextResult = self.context_manager.retrieve(query, top_k=3)
        state["context"] = result.context
        state["latency_breakdown"]["retrieval"] = result.latency_ms
        
        return state
    
    def _analyze_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node: Analyze context to infer mood and needs."""
        start_time = time.perf_counter()
        
        context = state.get("context", "")
        user_data = state.get("user_data", {})
        
        analysis_prompt = f"""Analyze the following user context and infer their current mood, stress level, and needs.

Context:
{context}

Provide a brief analysis (2-3 sentences) of:
1. Current emotional state
2. Stress indicators
3. Immediate needs or concerns

Analysis:"""
        
        try:
            messages = [HumanMessage(content=analysis_prompt)]
            response = self.llm.invoke(messages)
            
            analysis = response.content if hasattr(response, 'content') else str(response)
            state["analysis"] = analysis
            
            # Track tokens
            if hasattr(response, 'response_metadata'):
                metadata = response.response_metadata
                state["cost_tokens"] = state.get("cost_tokens", {"input": 0, "output": 0})
                state["cost_tokens"]["input"] += metadata.get("usage", {}).get("prompt_tokens", 0)
                state["cost_tokens"]["output"] += metadata.get("usage", {}).get("completion_tokens", 0)
            
        except Exception as e:
            state["error"] = f"Analysis error: {str(e)}"
            state["analysis"] = "Unable to analyze context."
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        state["latency_breakdown"]["analysis"] = latency_ms
        
        return state
    
    def _generate_nudge(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node: Generate proactive nudge."""
        start_time = time.perf_counter()
        
        context = state.get("context", "")
        analysis = state.get("analysis", "")
        user_data = state.get("user_data", {})
        
        # Get music preferences for personalization
        music_context = ""
        if user_data.get("music"):
            recent_music = user_data["music"][-3:]
            music_context = "\n".join([
                f"- {m.get('track_name', '')} by {m.get('artist', '')} ({m.get('mood', '')})"
                for m in recent_music
            ])
        
        nudge_prompt = f"""Based on the following analysis and context, generate a proactive, helpful nudge or suggestion for the user.

Context:
{context}

Analysis:
{analysis}

Recent Music Preferences:
{music_context if music_context else "None"}

Generate a brief, personalized nudge (1-2 sentences) that:
- Addresses their current state
- Provides actionable advice or suggestion
- Is empathetic and supportive
- Can reference their preferences if relevant

Nudge:"""
        
        try:
            messages = [HumanMessage(content=nudge_prompt)]
            response = self.llm.invoke(messages)
            
            nudge = response.content if hasattr(response, 'content') else str(response)
            state["nudge"] = nudge.strip()
            
            # Track tokens
            if hasattr(response, 'response_metadata'):
                metadata = response.response_metadata
                state["cost_tokens"]["input"] += metadata.get("usage", {}).get("prompt_tokens", 0)
                state["cost_tokens"]["output"] += metadata.get("usage", {}).get("completion_tokens", 0)
            
        except Exception as e:
            state["error"] = f"Nudge generation error: {str(e)}"
            state["nudge"] = "I'm here to help! How can I assist you today?"
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        state["latency_breakdown"]["nudge_generation"] = latency_ms
        
        return state
    
    def generate_nudge(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a nudge from user data."""
        start_time = time.perf_counter()
        
        initial_state = {
            "user_data": user_data,
            "latency_breakdown": {},
            "cost_tokens": {"input": 0, "output": 0}
        }
        
        try:
            final_state = self.graph.invoke(initial_state)
            total_latency_ms = (time.perf_counter() - start_time) * 1000
            final_state["latency_breakdown"]["total"] = total_latency_ms
            
            return final_state
        except Exception as e:
            return {
                "error": str(e),
                "nudge": "Error generating nudge.",
                "latency_breakdown": {"total": (time.perf_counter() - start_time) * 1000}
            }

