import streamlit as st
from typing import Dict, Optional, Tuple
from wattai import (
    calculate_cloud_cost, 
    calculate_local_cost, 
    GPU_DATABASE,
    DEFAULT_ELECTRICITY_COST_USD,
    GPUNotFoundError,
    InvalidInputError
)

# Constants
BENCHMARK_ELECTRICITY_COST = DEFAULT_ELECTRICITY_COST_USD
BENCHMARK_HOURS = 1.0
DEFAULT_HOURS = 10.0
COST_DECIMAL_PLACES = 2
PREVIEW_COST_DECIMAL_PLACES = 4

st.set_page_config(page_title="WattAI", layout="centered")

st.title("⚡ WattAI")
st.subheader("AI Cost Intelligence Calculator")


def format_currency(amount: float, decimal_places: int = COST_DECIMAL_PLACES) -> str:
    """
    Format a currency amount with specified decimal places.
    
    Args:
        amount: The amount to format
        decimal_places: Number of decimal places
        
    Returns:
        Formatted currency string
    """
    return f"${round(amount, decimal_places):.{decimal_places}f}"


@st.cache_data
def find_cheapest_option(
    electricity_cost: float, 
    hours: float
) -> Optional[Tuple[str, float]]:
    """
    Find the cheapest GPU option (cloud or local) for given parameters.
    
    Args:
        electricity_cost: Cost of electricity per kWh
        hours: Number of hours of usage
        
    Returns:
        Tuple of (label, price) or None if database is empty
    """
    if not GPU_DATABASE:
        return None
    
    cheapest_price: Optional[float] = None
    cheapest_label: str = ""
    
    for gpu_name in GPU_DATABASE:
        try:
            cloud = calculate_cloud_cost(electricity_cost, gpu_name, hours)
            local = calculate_local_cost(electricity_cost, gpu_name, hours)
            
            # Compare cloud option
            cloud_price = cloud["total_cost_usd"]
            if cheapest_price is None or cloud_price < cheapest_price:
                cheapest_price = cloud_price
                cheapest_label = f"☁️ Cloud - {gpu_name}"
            
            # Compare local option
            local_price = local["total_cost_usd"]
            if local_price < cheapest_price:
                cheapest_price = local_price
                cheapest_label = f"🖥 Local - {gpu_name}"
                
        except (GPUNotFoundError, InvalidInputError) as e:
            st.error(f"Error calculating costs for {gpu_name}: {str(e)}")
            continue
    
    if cheapest_price is None:
        return None
    
    return (cheapest_label, cheapest_price)


# ---------------------------------
# 🔥 Cheapest Option Preview
# ---------------------------------

st.markdown("## 🔥 Lowest AI Cost Right Now (1 Hour Benchmark)")

cheapest_result = find_cheapest_option(BENCHMARK_ELECTRICITY_COST, BENCHMARK_HOURS)

if cheapest_result:
    cheapest_label, cheapest_price = cheapest_result
    st.success(f"🏆 Cheapest Option: {cheapest_label}")
    st.write(f"Cost per hour: {format_currency(cheapest_price, PREVIEW_COST_DECIMAL_PLACES)}")
else:
    st.warning("⚠️ No GPUs available in database. Please add GPUs to calculate costs.")

st.divider()

# ---------------------------------
# User Inputs
# ---------------------------------

electricity_cost = st.number_input(
    "Electricity Cost (USD per kWh)",
    min_value=0.0,
    value=DEFAULT_ELECTRICITY_COST_USD,
    step=0.01,
    help="Enter your local electricity cost per kilowatt-hour"
)

if not GPU_DATABASE:
    st.error("⚠️ No GPUs available in database. Cannot proceed with calculations.")
    st.stop()

gpu_name = st.selectbox(
    "Select GPU",
    options=list(GPU_DATABASE.keys()),
    help="Choose the GPU you want to compare costs for"
)

hours = st.number_input(
    "Hours of Usage",
    min_value=0.0,
    value=DEFAULT_HOURS,
    step=0.5,
    help="Enter the number of hours you plan to use the GPU"
)

# ---------------------------------
# Calculation Section
# ---------------------------------

if st.button("Calculate", type="primary"):
    try:
        # Validate inputs
        if electricity_cost < 0:
            st.error("❌ Electricity cost cannot be negative.")
            st.stop()
        
        if hours < 0:
            st.error("❌ Hours cannot be negative.")
            st.stop()
        
        if hours == 0:
            st.warning("⚠️ Hours is 0. No costs will be incurred.")
            st.stop()
        
        # Calculate costs
        cloud = calculate_cloud_cost(electricity_cost, gpu_name, hours)
        local = calculate_local_cost(electricity_cost, gpu_name, hours)

        st.markdown("## 📊 Comparison Results")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### ☁️ Cloud")
            st.write(f"Energy Cost: {format_currency(cloud['energy_cost_usd'])}")
            st.write(f"Compute Cost: {format_currency(cloud['compute_cost_usd'])}")
            st.write(f"**Total: {format_currency(cloud['total_cost_usd'])}**")
            
            # Additional info
            with st.expander("📈 Details"):
                st.write(f"Energy Consumption: {cloud['energy_kwh']:.4f} kWh")

        with col2:
            st.markdown("### 🖥 Local")
            st.write(f"Energy Cost: {format_currency(local['energy_cost_usd'])}")
            st.write(f"**Total: {format_currency(local['total_cost_usd'])}**")
            
            # Additional info
            with st.expander("📈 Details"):
                st.write(f"Energy Consumption: {local['energy_kwh']:.4f} kWh")

        # Comparison result
        cloud_total = cloud["total_cost_usd"]
        local_total = local["total_cost_usd"]
        
        if cloud_total < local_total:
            savings = local_total - cloud_total
            st.success(f"☁️ **Cloud is cheaper** for this workload. Save {format_currency(savings)} by using cloud.")
        elif local_total < cloud_total:
            savings = cloud_total - local_total
            st.success(f"🖥 **Local is cheaper** for this workload. Save {format_currency(savings)} by using local.")
        else:
            st.info("💰 Both options cost the same for this workload.")
            
    except GPUNotFoundError as e:
        st.error(f"❌ {str(e)}")
    except InvalidInputError as e:
        st.error(f"❌ Invalid input: {str(e)}")
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {str(e)}")
        st.exception(e)
