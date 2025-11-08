"""On-device inference pilot using Hugging Face Transformers."""
import time
from typing import Dict, Any
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import config

class OnDeviceInference:
    """On-device LLM inference for edge deployment simulation."""
    
    def __init__(self):
        self.model_name = config.ON_DEVICE_MODEL
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self._load_model()
    
    def _load_model(self):
        """Load quantized model for faster inference."""
        try:
            print(f"Loading on-device model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                low_cpu_mem_usage=True
            )
            
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=100,
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id
            )
            print("On-device model loaded successfully")
        except Exception as e:
            print(f"Error loading on-device model: {e}")
            self.pipeline = None
    
    def generate_nudge(self, context: str, analysis: str) -> Dict[str, Any]:
        """Generate nudge using on-device model."""
        if not self.pipeline:
            return {
                "nudge": "On-device model not available.",
                "latency_ms": 0,
                "tokens": 0,
                "error": "Model not loaded"
            }
        
        start_time = time.perf_counter()
        
        prompt = f"""Context: {context}
Analysis: {analysis}
Generate a brief, helpful nudge (1-2 sentences):"""
        
        try:
            result = self.pipeline(
                prompt,
                max_length=len(self.tokenizer.encode(prompt)) + 50,
                num_return_sequences=1
            )
            
            generated_text = result[0]["generated_text"]
            nudge = generated_text.replace(prompt, "").strip()
            
            latency_ms = (time.perf_counter() - start_time) * 1000
            tokens = len(self.tokenizer.encode(generated_text))
            
            return {
                "nudge": nudge,
                "latency_ms": latency_ms,
                "tokens": tokens,
                "error": None
            }
        except Exception as e:
            return {
                "nudge": "Error generating nudge on-device.",
                "latency_ms": (time.perf_counter() - start_time) * 1000,
                "tokens": 0,
                "error": str(e)
            }

