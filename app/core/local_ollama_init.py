import os
import sys
import torch
import psutil # For checking system RAM
from pynvml import * # For checking NVIDIA VRAM
import subprocess
import logging
logger = logging.getLogger(__name__)

def _detect_amd_gpu():
    """
    Detect if AMD GPU with ROCm support is available.
    """
    try:
        # Check if PyTorch was built with ROCm support
        if hasattr(torch.version, 'hip') and torch.version.hip is not None:
            return True
        
        # Alternative: Check if rocm-smi command is available
        try:
            result = subprocess.run(['rocm-smi', '--showproductname'], 
                                 capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Another alternative: Check for AMD GPU in lspci (Linux only)
        if sys.platform == "linux":
            try:
                result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    output = result.stdout.lower()
                    return 'amd' in output and ('radeon' in output or 'navi' in output or 'vega' in output)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
                
        return False
    except Exception:
        return False

def _get_amd_memory():
    """
    Get AMD GPU memory information in MB.
    """
    try:
        # Method 1: Try using rocm-smi
        try:
            result = subprocess.run(['rocm-smi', '--showmeminfo', 'vram'], 
                                 capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'Total Memory' in line or 'VRAM Total' in line:
                        # Extract memory value (typically in MB or GB)
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part.replace('.', '').replace(',', '').isdigit():
                                memory_val = float(part.replace(',', ''))
                                # Check if next part indicates unit
                                if i + 1 < len(parts):
                                    unit = parts[i + 1].upper()
                                    if 'GB' in unit:
                                        return int(memory_val * 1024)
                                    elif 'MB' in unit:
                                        return int(memory_val)
                                # Default assumption: MB
                                return int(memory_val)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Method 2: Try ROCm torch functions (if available)
        if hasattr(torch, 'cuda') and torch.cuda.is_available():
            # Sometimes CUDA functions work with ROCm
            try:
                memory_bytes = torch.cuda.get_device_properties(0).total_memory
                return int(memory_bytes / (1024**2))
            except Exception:
                pass
        
        # Method 3: Parse /sys/class/drm files (Linux only)
        if sys.platform == "linux":
            try:
                import glob
                for card_path in glob.glob('/sys/class/drm/card*/device/mem_info_vram_total'):
                    with open(card_path, 'r') as f:
                        vram_bytes = int(f.read().strip())
                        return int(vram_bytes / (1024**2))
            except Exception:
                pass
        
        return 0
    except Exception:
        return 0
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

        # Check for AMD GPUs (Windows/Linux with ROCm)
        elif sys.platform in ["win32", "linux"] and _detect_amd_gpu():
            try:
                # Try to get AMD GPU memory info
                amd_vram_mb = _get_amd_memory()
                if amd_vram_mb > 0:
                    # Calculate the memory budget based on VRAM
                    memory_budget_mb = amd_vram_mb * USAGE_LIMIT_FRACTION
                    detected_hardware = f"AMD GPU with {amd_vram_mb:.0f} MB VRAM"
                    logger.info(f"🔴 Detected {detected_hardware}.")
                else:
                    raise ValueError("Could not determine AMD GPU memory")
            except Exception as amd_error:
                logger.warning(f"AMD GPU detected but could not get memory info: {amd_error}")
                # Fall back to system RAM for AMD systems
                total_ram_mb = psutil.virtual_memory().total / (1024**2)
                memory_budget_mb = total_ram_mb * USAGE_LIMIT_FRACTION
                detected_hardware = f"AMD GPU (using system RAM fallback: {total_ram_mb:.0f} MB)"
                logger.info(f"🔴 {detected_hardware}.")

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