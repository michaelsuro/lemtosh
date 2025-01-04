import os
import time
import json
import traceback
from typing import Optional, Dict
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
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.current_model_name = None
        return cls._instance

    def initialize(self):
        """Initialize the model directly"""
        if self._initialized:
            return

        print("[LLM] Initializing service...")
        if settings.IS_DEVELOPMENT:
            model_name = "mistral-7b"
            try:
                print(f"[LLM] Loading model {model_name}...")
                write_status(model_name, ModelStatus.LOADING)
                
                model_config = settings.MODELS_CONFIG[model_name]
                model_path = model_config["path"]
                
                if not os.path.exists(model_path):
                    raise FileNotFoundError(f"Model file not found at {model_path}")
                
                print(f"[LLM] Model file found. Size: {os.path.getsize(model_path) / (1024*1024*1024):.2f} GB")
                
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    model_type=model_config["type"],
                    context_length=2048,
                    gpu_layers=0,
                    batch_size=1,
                    threads=6
                )
                
                self.current_model_name = model_name
                print(f"[LLM] Model {model_name} loaded successfully!")
                
                # Test inference
                test_response = self.model("Test")
                print(f"[LLM] Test inference successful: {test_response[:50]}...")
                
                write_status(model_name, ModelStatus.READY)
                self._initialized = True
                
            except Exception as e:
                error_msg = str(e)
                print(f"[LLM] Error loading {model_name}: {error_msg}")
                print("[LLM] Full traceback:")
                print(traceback.format_exc())
                write_status(model_name, ModelStatus.ERROR, error_msg)
                raise

    def get_model_status(self, model_name: str) -> Dict[str, str]:
        """Get the current status of a model"""
        if self._initialized and self.model is not None and self.current_model_name == model_name:
            return {"status": ModelStatus.READY, "error": None}
        return read_status(model_name)

    async def get_response(self, message: str, model_name: str, chat_history: list = None) -> str:
        """Generate a response from the model with chat history context"""
        try:
            print(f"[LLM] Generating response for message with {len(chat_history) if chat_history else 0} previous messages")
            
            if not self._initialized or self.model is None:
                raise ValueError("Model not initialized")
            
            if self.current_model_name != model_name:
                raise ValueError(f"Requested model {model_name} is not the currently loaded model")

            # Limit chat history to last 5 messages to prevent context overflow
            if chat_history:
                chat_history = chat_history[-5:]
                
            formatted_prompt = ""
            current_length = 0
            max_history_chars = 4000  # Reduced from previous value
            
            # Add chat history if provided
            if chat_history:
                for msg in chat_history:
                    msg_content = f"[INST] {msg['user_message']} [/INST] {msg['assistant_response']}"
                    msg_length = len(msg_content)
                    
                    if current_length + msg_length > max_history_chars:
                        print(f"[LLM] Reached history limit at {current_length} characters")
                        break
                        
                    formatted_prompt += msg_content
                    current_length += msg_length
                
                print(f"[LLM] Included {current_length} characters of chat history")
            
            # Add current message
            formatted_prompt += f"<s>[INST] {message} [/INST]"
            
            print(f"[LLM] Total prompt length: {len(formatted_prompt)} characters")
            
            # Add timeout protection
            try:
                response = self.model(
                    formatted_prompt,
                    max_new_tokens=512,
                    temperature=0.7,
                    stop=["</s>"]
                )
                print(f"[LLM] Generated response successfully")
                return response.strip()
            except Exception as e:
                print(f"[LLM] Error during model inference: {str(e)}")
                raise ValueError("Model inference failed - please try again")
                
        except Exception as e:
            print(f"[LLM] Error generating response: {str(e)}")
            print("[LLM] Full traceback:")
            print(traceback.format_exc())
            raise ValueError(f"Error generating response: {str(e)}")

# Global instance
llm_service = LLMService()

async def get_llm_response(message: str, model_name: str, chat_history: list = None) -> str:
    """Helper function to get response from LLM service"""
    try:
        return await llm_service.get_response(message, model_name, chat_history)
    except Exception as e:
        print(f"[LLM] Error in get_llm_response: {str(e)}")
        print("[LLM] Full traceback:")
        print(traceback.format_exc())
        raise ValueError(f"Failed to generate response: {str(e)}")