import os
import sys
import torch
import psutil # For checking system RAM
from pynvml import * # For checking NVIDIA VRAM
import subprocess
import logging
logger = logging.getLogger(__name__)

def _detect_nvidia_gpu_smi():
    """
    Detect NVIDIA GPU using nvidia-smi command and get memory info.
    Returns (detected: bool, memory_mb: int, gpu_name: str)
    """
    try:
        result = subprocess.run([
            'nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    parts = line.split(', ')
                    if len(parts) >= 2:
                        gpu_name = parts[0].strip()
                        memory_mb = float(parts[1].strip())
                        return True, int(memory_mb), gpu_name
        return False, 0, ""
    except Exception as e:
        logger.debug(f"nvidia-smi detection failed: {e}")
        return False, 0, ""

def _detect_amd_gpu():
    """
    Detect AMD GPU using multiple methods for Windows.
    Returns (detected: bool, memory_mb: int, gpu_name: str)
    """
    try:
        # Method 1: Try rocm-smi (if ROCm is installed)
        try:
            result = subprocess.run(['rocm-smi', '--showproductname'], 
                                 capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Get memory info
                mem_result = subprocess.run(['rocm-smi', '--showmeminfo', 'vram'], 
                                         capture_output=True, text=True, timeout=5)
                if mem_result.returncode == 0:
                    lines = mem_result.stdout.strip().split('\n')
                    for line in lines:
                        if 'Total Memory' in line or 'VRAM Total' in line:
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if part.replace('.', '').replace(',', '').isdigit():
                                    memory_val = float(part.replace(',', ''))
                                    if i + 1 < len(parts) and 'GB' in parts[i + 1].upper():
                                        return True, int(memory_val * 1024), "AMD GPU (ROCm)"
                                    elif i + 1 < len(parts) and 'MB' in parts[i + 1].upper():
                                        return True, int(memory_val), "AMD GPU (ROCm)"
                return True, 0, "AMD GPU (ROCm - no memory info)"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Method 2: Check WMI for AMD GPUs and try to get memory
        if sys.platform == "win32":
            try:
                result = subprocess.run([
                    'wmic', 'path', 'win32_VideoController', 
                    'get', 'name,adapterram', '/format:csv'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines[1:]:  # Skip header
                        if line.strip():
                            parts = [p.strip() for p in line.split(',')]
                            if len(parts) >= 3 and parts[2]:  # Check if name exists
                                gpu_name = parts[2].lower()
                                if 'amd' in gpu_name or 'radeon' in gpu_name or 'rx ' in gpu_name:
                                    memory_bytes = parts[1] if parts[1] else "0"
                                    try:
                                        memory_mb = int(memory_bytes) // (1024 * 1024)
                                        return True, memory_mb, parts[2]
                                    except:
                                        return True, 0, parts[2]
            except Exception as e:
                logger.debug(f"WMI AMD detection failed: {e}")
        
        return False, 0, ""
    except Exception as e:
        logger.debug(f"AMD detection failed: {e}")
        return False, 0, ""
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
        # Method 1: Check for NVIDIA GPUs using nvidia-smi (more reliable for Windows)
        nvidia_detected, nvidia_memory_mb, nvidia_name = _detect_nvidia_gpu_smi()
        if nvidia_detected and nvidia_memory_mb > 0:
            # Calculate the memory budget based on VRAM
            memory_budget_mb = nvidia_memory_mb * USAGE_LIMIT_FRACTION
            detected_hardware = f"NVIDIA GPU ({nvidia_name}) with {nvidia_memory_mb:.0f} MB VRAM"
            logger.info(f"🚀 Detected {detected_hardware} via nvidia-smi.")

        # Method 2: Fallback to PyTorch + NVML for NVIDIA (original method)
        elif sys.platform in ["win32", "linux"] and torch.cuda.is_available():
            try:
                nvmlInit()
                handle = nvmlDeviceGetHandleByIndex(0) # Assuming usage of the first GPU
                mem_info = nvmlDeviceGetMemoryInfo(handle)
                total_vram_mb = mem_info.total / (1024**2)
                nvmlShutdown()
                
                # Calculate the memory budget based on VRAM
                memory_budget_mb = total_vram_mb * USAGE_LIMIT_FRACTION
                detected_hardware = f"NVIDIA GPU with {total_vram_mb:.0f} MB VRAM"
                logger.info(f"✅ Detected {detected_hardware} via PyTorch/NVML.")
            except Exception as nvml_error:
                logger.warning(f"NVML detection failed: {nvml_error}")
                # Will fall through to other detection methods

        # Method 3: Check for macOS (Apple Silicon with unified memory)
        elif sys.platform == "darwin" and torch.backends.mps.is_available():
            total_ram_mb = psutil.virtual_memory().total / (1024**2)
            
            # Calculate the memory budget based on system RAM
            memory_budget_mb = total_ram_mb * USAGE_LIMIT_FRACTION
            detected_hardware = f"Apple Silicon (MPS) with {total_ram_mb:.0f} MB Unified RAM"

            logger.info(f"🍎 Detected {detected_hardware}.")

        # Method 4: Check for AMD GPUs (Windows/Linux)
        elif sys.platform in ["win32", "linux"]:
            amd_detected, amd_memory_mb, amd_name = _detect_amd_gpu()
            if amd_detected:
                if amd_memory_mb > 0:
                    # Calculate the memory budget based on VRAM
                    memory_budget_mb = amd_memory_mb * USAGE_LIMIT_FRACTION
                    detected_hardware = f"AMD GPU ({amd_name}) with {amd_memory_mb:.0f} MB VRAM"
                    logger.info(f"🔴 Detected {detected_hardware}.")
                else:
                    # Fall back to system RAM for AMD systems when memory can't be determined
                    total_ram_mb = psutil.virtual_memory().total / (1024**2)
                    memory_budget_mb = total_ram_mb * USAGE_LIMIT_FRACTION
                    detected_hardware = f"AMD GPU ({amd_name}) - using system RAM fallback: {total_ram_mb:.0f} MB"
                    logger.info(f"🔴 Detected {detected_hardware}.")

        # Fallback for CPU-only systems
        if 'memory_budget_mb' not in locals():
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
            os.environ['OLLAMA_NUM_GPU'] = ollama_gpu_layers
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