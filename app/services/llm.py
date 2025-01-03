import os
from typing import Optional
from ctransformers import AutoModelForCausalLM
from app.config import settings

class LLMService:
    def __init__(self):
        self.model = None
        self.current_model_name = None

    async def load_model(self, model_name: str):
        if self.current_model_name == model_name:
            return
        
        # Get model config from settings
        model_config = settings.MODELS_CONFIG.get(model_name)
        if not model_config:
            raise ValueError(f"Unknown model: {model_name}")

        if model_name not in settings.get_available_models():
            raise ValueError(f"Model {model_name} is not available in the current environment")
        
        # Load the model
        self.model = AutoModelForCausalLM.from_pretrained(
            model_config["path"],
            model_type=model_config["type"],
            context_length=model_config["context_length"],
            gpu_layers=model_config["gpu_layers"]
        )
        self.current_model_name = model_name

    async def get_response(self, prompt: str) -> str:
        if not self.model:
            raise RuntimeError("Model not loaded")

        # Format prompt for the model
        formatted_prompt = f"<s>[INST] {prompt} [/INST]"
        
        # Generate response
        response = self.model(
            formatted_prompt,
            max_new_tokens=512,
            temperature=0.7,
            stop=["</s>"]
        )

        return response.strip()

# Global instance
llm_service = LLMService()

async def get_llm_response(message: str, model_name: str = "mistral-7b") -> str:
    await llm_service.load_model(model_name)
    return await llm_service.get_response(message)