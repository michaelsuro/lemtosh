import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    IS_DEVELOPMENT: bool = ENVIRONMENT == "development"
    IS_PRODUCTION: bool = ENVIRONMENT == "production"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    if not SECRET_KEY and IS_PRODUCTION:
        raise ValueError("SECRET_KEY environment variable is required in production")
    elif not SECRET_KEY:
        SECRET_KEY = "default-development-secret-key-not-for-production"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./lemtosh.db")
    
    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))

    # LLM Models Configuration
    MODELS_CONFIG: Dict[str, Dict[str, Any]] = {
        "mistral-7b": {
            "name": "Mistral 7B",
            "path": "models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
            "type": "mistral",
            "context_length": 8192,
            "gpu_layers": 0,  # 0 for local CPU testing
            "environment": ["development", "production"],
            "file_name": "mistral-7b-instruct-v0.1.Q4_K_M.gguf",
            "download_url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/blob/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
        },
        "llama-2-13b": {
            "name": "LLaMA-2 13B",
            "path": "models/llama-2-13b-chat.Q4_K_M.gguf",
            "type": "llama",
            "context_length": 4096,
            "gpu_layers": 50,  # Using GPU in production
            "environment": ["production"],
            "file_name": "llama-2-13b-chat.Q4_K_M.gguf",
            "download_url": "https://huggingface.co/TheBloke/Llama-2-13B-chat-GGUF/resolve/main/llama-2-13b-chat.Q4_K_M.gguf"
        },
        "hermes-13b": {
            "name": "Hermes-3 13B",
            "path": "models/hermes-13b.Q4_K_M.gguf",
            "type": "llama2",
            "context_length": 4096,
            "gpu_layers": 50,  # Using GPU in production
            "environment": ["production"],
            "file_name": "hermes-13b.Q4_K_M.gguf",
            "download_url": "https://huggingface.co/TheBloke/Hermes-13B-GGUF/resolve/main/hermes-13b.Q4_K_M.gguf"
        },
        "falcon-40b": {
            "name": "Falcon 40B",
            "path": "models/falcon-40b-instruct.Q4_K_M.gguf",
            "type": "falcon",
            "context_length": 4096,
            "gpu_layers": 90,  # More GPU layers for larger model
            "environment": ["production"],
            "file_name": "falcon-40b-instruct.Q4_K_M.gguf",
            "download_url": "https://huggingface.co/TheBloke/falcon-40b-instruct-GGUF/resolve/main/falcon-40b-instruct.Q4_K_M.gguf"
        }
    }

    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Return only the models available for the current environment."""
        return {
            model_id: config 
            for model_id, config in self.MODELS_CONFIG.items() 
            if self.ENVIRONMENT in config["environment"]
        }

# Create settings instance
settings = Settings()