import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import StringIO

# Key parameters
investmentRange = {
    "min": 10000,
    "max": 100000
}
lockPeriods = [180, 365]  # 6 months and 12 months
earlyWithdrawalPenalty = 0.1  # 10% of initial capital
managementFee = 0.03  # 3%
performanceFeeConfig = {  # Commission cascade scheme
    "0-15%": [18, 3.0, 0.0, 0.0],
    "15-35%": [24, 5.7, 9.3, 0.0],
    "35-60%": [33, 11.4, 23.6, 0.0],
    "60%+": [39, 22.8, 37.2, 0.0]
}

def simulate_investment_data():
    # Simulation logic similar to the previous code
    # ...
    return simulated_data

def plot_investment_charts(data):
    # Total Investment Over Time
    total_investment_fig = go.Figure()
    total_investment_fig.add_trace(go.Scatter(x=data["day"], y=data["totalInvestment"], mode="lines", name="Total Investment"))
    total_investment_fig.update_layout(title="Total Investment Over Time", xaxis_title="Day", yaxis_title="Investment")

    # Active Investors Over Time
    active_investors_fig = go.Figure()
    active_investors_fig.add_trace(go.Scatter(x=data["day"], y=data["numInvestors"], mode="lines", name="Active Investors"))
    active_investors_fig.update_layout(title="Active Investors Over Time", xaxis_title="Day", yaxis_title="Investors")

    # Investor Ownership Percentages
    investor_ownership_fig = go.Figure()
    for col in data.columns:
        if col.endswith("_pct"):
            investor_ownership_fig.add_trace(go.Scatter(x=data["day"], y=data[col], mode="lines", name=col.replace("_pct", "")))
    investor_ownership_fig.update_layout(title="Investor Ownership Percentages", xaxis_title="Day", yaxis_title="Percentage")

    st.plotly_chart(total_investment_fig, use_container_width=True)
    st.plotly_chart(active_investors_fig, use_container_width=True)
    st.plotly_chart(investor_ownership_fig, use_container_width=True)

def main():
    st.title("Investment Visualization")

    # Allow the user to adjust the key parameters
    st.sidebar.header("Simulation Parameters")
    investmentRange["min"] = st.sidebar.number_input("Minimum Investment", min_value=1000, max_value=500000, value=10000, step=1000)
    investmentRange["max"] = st.sidebar.number_input("Maximum Investment", min_value=1000, max_value=500000, value=100000, step=1000)
    lock_period_idx = st.sidebar.selectbox("Lock Period", [0, 1], format_func=lambda x: f"{lockPeriods[x]} days")
    earlyWithdrawalPenalty = st.sidebar.number_input("Early Withdrawal Penalty (%)", min_value=0.0, max_value=1.0, value=0.1, step=0.01)
    managementFee = st.sidebar.number_input("Management Fee (%)", min_value=0.0, max_value=1.0, value=0.03, step=0.01)

    # Simulate the investment data
    data = simulate_investment_data()

    # Plot the investment charts
    plot_investment_charts(data)

if __name__ == "__main__":
    main()
