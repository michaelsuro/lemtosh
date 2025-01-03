import os
from typing import Optional
from ctransformers import AutoModelForCausalLM
from app.config import settings

class LLMService:
    def __init__(self):
        self.models = {}  # Store loaded models
        
    def initialize(self):
        """Initialize the default model on startup"""
        print("Initializing LLM service...")
        try:
            # Load Mistral model for development environment
            if settings.IS_DEVELOPMENT:
                print("Loading Mistral model...")
                model_config = settings.MODELS_CONFIG["mistral-7b"]
                self.models["mistral-7b"] = AutoModelForCausalLM.from_pretrained(
                    model_config["path"],
                    model_type=model_config["type"],
                    context_length=model_config["context_length"],
                    gpu_layers=model_config["gpu_layers"]
                )
                print("Mistral model loaded successfully")
        except Exception as e:
            print(f"Error initializing LLM service: {str(e)}")
            raise

    async def get_response(self, message: str, model_name: str) -> str:
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not loaded")

        try:
            print(f"Generating response using {model_name}")
            formatted_prompt = f"<s>[INST] {message} [/INST]"
            
            response = self.models[model_name](
                formatted_prompt,
                max_new_tokens=512,
                temperature=0.7,
                stop=["</s>"]
            )
            return response.strip()
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            raise

# Global instance
llm_service = LLMService()

async def get_llm_response(message: str, model_name: str) -> str:
    return await llm_service.get_response(message, model_name)