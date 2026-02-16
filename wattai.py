"""
WattAI Core Engine
This file contains pure calculation logic.
No UI code. No Streamlit code.
"""
from typing import Dict, Any


# Constants
DEFAULT_ELECTRICITY_COST_USD = 0.10
WATTS_TO_KWH_CONVERSION = 1000.0

# GPU Database
GPU_DATABASE: Dict[str, Dict[str, float]] = {
    "RTX 3090": {"watts": 350, "hourly_cost_usd": 1.80},
    "A100": {"watts": 400, "hourly_cost_usd": 3.50},
    "RTX 4090": {"watts": 450, "hourly_cost_usd": 2.20},
}


class GPUNotFoundError(Exception):
    """Raised when a GPU name is not found in the database."""
    pass


class InvalidInputError(Exception):
    """Raised when input values are invalid."""
    pass


def validate_inputs(electricity_cost_usd: float, hours: float) -> None:
    """
    Validate input parameters for cost calculations.
    
    Args:
        electricity_cost_usd: Cost of electricity per kWh
        hours: Number of hours of usage
        
    Raises:
        InvalidInputError: If inputs are negative or invalid
    """
    if electricity_cost_usd < 0:
        raise InvalidInputError("Electricity cost cannot be negative")
    if hours < 0:
        raise InvalidInputError("Hours cannot be negative")


def calculate_cloud_cost(
    electricity_cost_usd: float, 
    gpu_name: str, 
    hours: float
) -> Dict[str, float]:
    """
    Calculate the total cost of running a GPU in the cloud.
    
    Includes both energy costs (electricity) and compute costs (cloud provider fees).
    
    Args:
        electricity_cost_usd: Cost of electricity per kWh
        gpu_name: Name of the GPU (must exist in GPU_DATABASE)
        hours: Number of hours of usage
        
    Returns:
        Dictionary containing:
            - energy_kwh: Energy consumption in kWh
            - energy_cost_usd: Cost of energy in USD
            - compute_cost_usd: Cost of compute (cloud provider fees) in USD
            - total_cost_usd: Total cost (energy + compute) in USD
            
    Raises:
        GPUNotFoundError: If gpu_name is not in GPU_DATABASE
        InvalidInputError: If input values are invalid
    """
    validate_inputs(electricity_cost_usd, hours)
    
    if gpu_name not in GPU_DATABASE:
        raise GPUNotFoundError(f"GPU '{gpu_name}' not found in database. Available GPUs: {list(GPU_DATABASE.keys())}")
    
    gpu = GPU_DATABASE[gpu_name]
    gpu_watts = gpu["watts"]
    gpu_hourly_cost = gpu["hourly_cost_usd"]

    energy_kwh = (gpu_watts * hours) / WATTS_TO_KWH_CONVERSION
    energy_cost = energy_kwh * electricity_cost_usd
    compute_cost = gpu_hourly_cost * hours

    total_cost = energy_cost + compute_cost

    return {
        "energy_kwh": energy_kwh,
        "energy_cost_usd": energy_cost,
        "compute_cost_usd": compute_cost,
        "total_cost_usd": total_cost,
    }


def calculate_local_cost(
    electricity_cost_usd: float, 
    gpu_name: str, 
    hours: float
) -> Dict[str, float]:
    """
    Calculate the total cost of running a GPU locally.
    
    Only includes energy costs (electricity), as there are no cloud provider fees.
    
    Args:
        electricity_cost_usd: Cost of electricity per kWh
        gpu_name: Name of the GPU (must exist in GPU_DATABASE)
        hours: Number of hours of usage
        
    Returns:
        Dictionary containing:
            - energy_kwh: Energy consumption in kWh
            - energy_cost_usd: Cost of energy in USD
            - total_cost_usd: Total cost (energy only) in USD
            
    Raises:
        GPUNotFoundError: If gpu_name is not in GPU_DATABASE
        InvalidInputError: If input values are invalid
    """
    validate_inputs(electricity_cost_usd, hours)
    
    if gpu_name not in GPU_DATABASE:
        raise GPUNotFoundError(f"GPU '{gpu_name}' not found in database. Available GPUs: {list(GPU_DATABASE.keys())}")
    
    gpu = GPU_DATABASE[gpu_name]
    gpu_watts = gpu["watts"]

    energy_kwh = (gpu_watts * hours) / WATTS_TO_KWH_CONVERSION
    energy_cost = energy_kwh * electricity_cost_usd

    return {
        "energy_kwh": energy_kwh,
        "energy_cost_usd": energy_cost,
        "total_cost_usd": energy_cost,
    }


# Optional: simple test mode
if __name__ == "__main__":
    print("Testing WattAI Core Engine...\n")

    result_cloud = calculate_cloud_cost(DEFAULT_ELECTRICITY_COST_USD, "RTX 3090", 10)
    result_local = calculate_local_cost(DEFAULT_ELECTRICITY_COST_USD, "RTX 3090", 10)

    print("Cloud Total Cost:", round(result_cloud["total_cost_usd"], 2))
    print("Local Total Cost:", round(result_local["total_cost_usd"], 2))