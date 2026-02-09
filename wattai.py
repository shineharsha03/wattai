"""
WattAI Core Engine
This file contains pure calculation logic.
No UI code. No Streamlit code.
"""

# GPU Database
GPU_DATABASE = {
    "RTX 3090": {"watts": 350, "hourly_cost_usd": 1.80},
    "A100": {"watts": 400, "hourly_cost_usd": 3.50},
    "RTX 4090": {"watts": 450, "hourly_cost_usd": 2.20},
}


def calculate_cloud_cost(electricity_cost_usd, gpu_name, hours):
    gpu = GPU_DATABASE[gpu_name]

    gpu_watts = gpu["watts"]
    gpu_hourly_cost = gpu["hourly_cost_usd"]

    energy_kwh = (gpu_watts * hours) / 1000
    energy_cost = energy_kwh * electricity_cost_usd
    compute_cost = gpu_hourly_cost * hours

    total_cost = energy_cost + compute_cost

    return {
        "energy_kwh": energy_kwh,
        "energy_cost_usd": energy_cost,
        "compute_cost_usd": compute_cost,
        "total_cost_usd": total_cost,
    }


def calculate_local_cost(electricity_cost_usd, gpu_name, hours):
    gpu = GPU_DATABASE[gpu_name]

    gpu_watts = gpu["watts"]

    energy_kwh = (gpu_watts * hours) / 1000
    energy_cost = energy_kwh * electricity_cost_usd

    return {
        "energy_kwh": energy_kwh,
        "energy_cost_usd": energy_cost,
        "total_cost_usd": energy_cost,
    }


# Optional: simple test mode
if __name__ == "__main__":
    print("Testing WattAI Core Engine...\n")

    result_cloud = calculate_cloud_cost(0.10, "RTX 3090", 10)
    result_local = calculate_local_cost(0.10, "RTX 3090", 10)

    print("Cloud Total Cost:", round(result_cloud["total_cost_usd"], 2))
    print("Local Total Cost:", round(result_local["total_cost_usd"], 2))
