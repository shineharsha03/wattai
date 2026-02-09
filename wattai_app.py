import streamlit as st
from wattai import calculate_cloud_cost, calculate_local_cost, GPU_DATABASE

st.set_page_config(page_title="WattAI", layout="centered")

st.title("⚡ WattAI")
st.subheader("AI Cost Intelligence Calculator")

# ---------------------------------
# 🔥 Cheapest Option Preview
# ---------------------------------

st.markdown("## 🔥 Lowest AI Cost Right Now (1 Hour Benchmark)")

benchmark_electricity = 0.10
benchmark_hours = 1

cheapest_price = None
cheapest_label = ""

for gpu in GPU_DATABASE:

    cloud = calculate_cloud_cost(benchmark_electricity, gpu, benchmark_hours)
    local = calculate_local_cost(benchmark_electricity, gpu, benchmark_hours)

    # Cloud comparison
    if cheapest_price is None or cloud["total_cost_usd"] < cheapest_price:
        cheapest_price = cloud["total_cost_usd"]
        cheapest_label = f"☁️ Cloud - {gpu}"

    # Local comparison
    if local["total_cost_usd"] < cheapest_price:
        cheapest_price = local["total_cost_usd"]
        cheapest_label = f"🖥 Local - {gpu}"

st.success(f"🏆 Cheapest Option: {cheapest_label}")
st.write("Cost per hour: $", round(cheapest_price, 4))

st.divider()

# ---------------------------------
# User Inputs
# ---------------------------------

electricity_cost = st.number_input(
    "Electricity Cost (USD per kWh)",
    min_value=0.0,
    value=0.10
)

gpu_name = st.selectbox(
    "Select GPU",
    list(GPU_DATABASE.keys())
)

hours = st.number_input(
    "Hours of Usage",
    min_value=0.0,
    value=10.0
)

# ---------------------------------
# Calculation Section
# ---------------------------------

if st.button("Calculate"):

    cloud = calculate_cloud_cost(electricity_cost, gpu_name, hours)
    local = calculate_local_cost(electricity_cost, gpu_name, hours)

    st.markdown("## 📊 Comparison Results")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ☁️ Cloud")
        st.write("Energy Cost: $", round(cloud["energy_cost_usd"], 2))
        st.write("Compute Cost: $", round(cloud["compute_cost_usd"], 2))
        st.write("**Total: $", round(cloud["total_cost_usd"], 2), "**")

    with col2:
        st.markdown("### 🖥 Local")
        st.write("Energy Cost: $", round(local["energy_cost_usd"], 2))
        st.write("**Total: $", round(local["total_cost_usd"], 2), "**")

    if cloud["total_cost_usd"] < local["total_cost_usd"]:
        st.success("☁️ Cloud is cheaper for this workload.")
    else:
        st.success("🖥 Local is cheaper for this workload.")
