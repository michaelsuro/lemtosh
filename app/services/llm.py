import os
from typing import Optional
from ctransformers import AutoModelForCausalLM

class LLMService:
    def __init__(self):
        self.model = None
        self.current_model_name = None

    async def load_model(self, model_name: str):
        if self.current_model_name == model_name:
            return
        
        # Model paths - in production these would come from config
        model_paths = {
            "mistral-7b": "mistral-7b-instruct-v0.1.Q4_K_M.gguf",  # You'll need to download this
        }

        if model_name not in model_paths:
            raise ValueError(f"Unknown model: {model_name}")

        model_path = model_paths[model_name]
        
        # Load the model
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            model_type="mistral",
            gpu_layers=0  # Set this higher if using GPU
        )
        self.current_model_name = model_name

    async def get_response(self, prompt: str) -> str:
        if not self.model:
            raise RuntimeError("Model not loaded")

        # Format prompt for Mistral
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