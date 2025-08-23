import os
import sys
import torch
import psutil # For checking system RAM
from pynvml import * # For checking NVIDIA VRAM
import logging
logger = logging.getLogger(__name__)
def configure_ollama_by_capacity():
    """
    Detects system hardware, calculates a memory budget of ~33% of total
    capacity, and estimates the number of model layers to set for OLLAMA_NUM_GPU.
    """
    
    # --- Constants and Configuration ---
    # Estimated memory per layer for a ~7B model in MB. Adjust if using larger models.
    MEMORY_PER_LAYER_MB = 500
    # The percentage of total capacity to allocate. 0.33 means 33%.
    USAGE_LIMIT_FRACTION = 1/3
    
    ollama_gpu_layers = 0
    detected_hardware = "CPU"

    # --- Step 1: Detect Platform and Measure Capacity ---
    
    try:
        # Check for Windows or Linux (for NVIDIA GPUs)
        if sys.platform in ["win32", "linux"] and torch.cuda.is_available():
            nvmlInit()
            handle = nvmlDeviceGetHandleByIndex(0) # Assuming usage of the first GPU
            mem_info = nvmlDeviceGetMemoryInfo(handle)
            total_vram_mb = mem_info.total / (1024**2)
            nvmlShutdown()
            
            # Calculate the memory budget based on VRAM
            memory_budget_mb = total_vram_mb * USAGE_LIMIT_FRACTION
            detected_hardware = f"NVIDIA GPU with {total_vram_mb:.0f} MB VRAM"

            logger.info(f"✅ Detected {detected_hardware}.")

        # Check for macOS (Apple Silicon with unified memory)
        elif sys.platform == "darwin" and torch.backends.mps.is_available():
            total_ram_mb = psutil.virtual_memory().total / (1024**2)
            
            # Calculate the memory budget based on system RAM
            memory_budget_mb = total_ram_mb * USAGE_LIMIT_FRACTION
            detected_hardware = f"Apple Silicon (MPS) with {total_ram_mb:.0f} MB Unified RAM"

            logger.info(f"🍎 Detected {detected_hardware}.")

        # Fallback for CPU-only systems
        else:
            total_ram_mb = psutil.virtual_memory().total / (1024**2)
            
            # Calculate the memory budget based on system RAM
            memory_budget_mb = total_ram_mb * USAGE_LIMIT_FRACTION
            detected_hardware = f"CPU with {total_ram_mb:.0f} MB RAM"

            logger.info(f"🐌 Detected {detected_hardware}.")

        # --- Step 2: Estimate Layers and Set Configuration ---
        
        # Calculate how many layers can fit into our budget
        if 'memory_budget_mb' in locals():
            ollama_gpu_layers = int(memory_budget_mb / MEMORY_PER_LAYER_MB)
            logger.info(f"📊 Calculated memory budget: {memory_budget_mb:.0f} MB.")
            logger.info(f"🧠 This allows for an estimated {ollama_gpu_layers} model layers to be offloaded.")

        # Ensure at least 1 layer is offloaded if GPU is detected, but don't go crazy
        if ollama_gpu_layers > 0:
            os.environ['OLLAMA_NUM_GPU'] = str(ollama_gpu_layers)
            logger.info(f"🔧 Environment variable 'OLLAMA_NUM_GPU' has been set to '{ollama_gpu_layers}'.")
            logger.info("🚀 Ollama is configured to use approximately 30% of available capacity.")
        else:
            logger.warning("❌ Not enough capacity to offload layers, or no compatible GPU detected. Ollama will use CPU.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.info("Could not configure Ollama automatically. It will use default settings.")

# --- Main Execution ---
if __name__ == "__main__":
    configure_ollama_by_capacity()