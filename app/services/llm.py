import os
import time
import json
import traceback
from typing import Optional, Dict
from multiprocessing import Process
from ctransformers import AutoModelForCausalLM
from app.config import settings

class ModelStatus:
    LOADING = "loading"
    READY = "ready"
    ERROR = "error"

def write_status(model_name: str, status: str, error: str = None):
    """Write model status to a file"""
    status_file = f"models/{model_name}_status.json"
    with open(status_file, 'w') as f:
        json.dump({
            "status": status,
            "error": error,
            "timestamp": time.time()
        }, f)

def read_status(model_name: str) -> Dict:
    """Read model status from file"""
    status_file = f"models/{model_name}_status.json"
    try:
        with open(status_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"status": ModelStatus.LOADING, "error": None}

class LLMService:
    _instance = None  # Singleton instance
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.current_model_name = None
        return cls._instance

    @staticmethod
    def _load_model_process(model_name: str):
        """Separate process for loading the model"""
        try:
            print(f"[LLM] Starting model load process for {model_name}...")
            write_status(model_name, ModelStatus.LOADING)
            
            model_config = settings.MODELS_CONFIG[model_name]
            model_path = model_config["path"]
            
            # Verify model file
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found at {model_path}")
            
            print(f"[LLM] Model file found. Size: {os.path.getsize(model_path) / (1024*1024*1024):.2f} GB")
            
            # Load the model
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                model_type=model_config["type"],
                context_length=2048,
                gpu_layers=0,
                batch_size=1,
                threads=6
            )
            
            # Verify model loaded successfully with a test inference
            test_response = model("Test")
            if not test_response:
                raise RuntimeError("Model loaded but failed to generate test response")
            
            print(f"[LLM] Model {model_name} loaded and verified successfully!")
            write_status(model_name, ModelStatus.READY)
            
        except Exception as e:
            error_msg = str(e)
            print(f"[LLM] Error loading {model_name}: {error_msg}")
            print("[LLM] Full traceback:")
            print(traceback.format_exc())
            write_status(model_name, ModelStatus.ERROR, error_msg)

    def initialize(self):
        """Initialize model loading in background"""
        print("[LLM] Initializing service...")
        if settings.IS_DEVELOPMENT:
            model_name = "mistral-7b"
            print(f"[LLM] Starting background load of {model_name}")
            
            # Ensure models directory exists
            os.makedirs("models", exist_ok=True)
            
            # Start loading process
            process = Process(target=self._load_model_process, args=(model_name,))
            process.daemon = True
            process.start()

    def get_model_status(self, model_name: str) -> Dict[str, str]:
        """Get the current status of a model"""
        status = read_status(model_name)
        print(f"[LLM] Status for {model_name}: {status}")
        return status

    async def get_response(self, message: str, model_name: str) -> str:
        """Generate a response from the model"""
        try:
            print(f"[LLM] Generating response for message: {message[:50]}...")
            
            # Check model status
            status = read_status(model_name)
            if status["status"] != ModelStatus.READY:
                raise ValueError(f"Model {model_name} is not ready. Status: {status['status']}")

            # Load model if not already loaded
            if self.current_model_name != model_name or self.model is None:
                print(f"[LLM] Loading model {model_name} for inference...")
                model_config = settings.MODELS_CONFIG[model_name]
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_config["path"],
                    model_type=model_config["type"],
                    context_length=2048,
                    gpu_layers=0,
                    batch_size=1,
                    threads=6
                )
                self.current_model_name = model_name
                print(f"[LLM] Model {model_name} loaded for inference")

            # Generate response
            formatted_prompt = f"<s>[INST] {message} [/INST]"
            response = self.model(
                formatted_prompt,
                max_new_tokens=512,
                temperature=0.7,
                stop=["</s>"]
            )
            
            print(f"[LLM] Generated response successfully")
            return response.strip()
            
        except Exception as e:
            print(f"[LLM] Error generating response: {str(e)}")
            print("[LLM] Full traceback:")
            print(traceback.format_exc())
            raise ValueError(f"Error generating response: {str(e)}")

# Global instance
llm_service = LLMService()

async def get_llm_response(message: str, model_name: str) -> str:
    """Helper function to get response from LLM service"""
    try:
        return await llm_service.get_response(message, model_name)
    except Exception as e:
        print(f"[LLM] Error in get_llm_response: {str(e)}")
        print("[LLM] Full traceback:")
        print(traceback.format_exc())
        raise