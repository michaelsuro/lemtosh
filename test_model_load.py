"""
This is a test script to verify model loading outside of the multiprocessing context.
Run this directly to test model loading.
"""
from ctransformers import AutoModelForCausalLM
import os

def test_load():
    model_path = "models/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
    
    print(f"Current working directory: {os.getcwd()}")
    print(f"Testing model load from: {model_path}")
    print(f"File exists: {os.path.exists(model_path)}")
    if os.path.exists(model_path):
        print(f"File size: {os.path.getsize(model_path) / (1024*1024*1024):.2f} GB")
    
    try:
        print("Attempting to load model...")
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            model_type="mistral",
            context_length=2048,
            gpu_layers=0,
            batch_size=1,
            threads=6
        )
        print("Model loaded successfully!")
        
        # Test inference
        print("Testing inference...")
        response = model("Hello, how are you?")
        print(f"Test response: {response}")
        
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_load()