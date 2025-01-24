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
    days = 365
    poisson_rate = 0.15
    total_investment = 0
    portfolio = defaultdict(dict)
    history = []

    # Helper function to create an investor
    def create_investor(day):
        investment = np.random.uniform(investmentRange["min"], investmentRange["max"])
        lock_period = lockPeriods[0] if np.random.random() < 0.5 else lockPeriods[1]  # 6 or 12 months
        return {
            "investment": investment,
            "entryDay": day,
            "lockPeriod": lock_period,
            "isActive": True
        }

    # Initial investors
    for i in range(5):
        investor_id = f"Investor_{i+1}"
        portfolio[investor_id] = create_investor(0)
        total_investment += portfolio[investor_id]["investment"]

    # Simulate days
    for day in range(days):
        # Process exits
        for investor_id, investor in portfolio.items():
            if not investor["isActive"]:
                continue

            # Check for early withdrawal
            if np.random.random() < earlyWithdrawalPenalty / 365:  # Daily probability
                investor["isActive"] = False
                total_investment -= investor["investment"] * (1 - earlyWithdrawalPenalty)

            # Check for lock period expiry
            elif day - investor["entryDay"] >= investor["lockPeriod"]:
                if np.random.random() < 0.3:  # 30% chance to exit after lock period
                    investor["isActive"] = False
                    total_investment -= investor["investment"]

        # Deduct management fee
        total_investment -= total_investment * managementFee / 365

        # New investors (Poisson distribution)
        num_new_investors = 1 if np.random.random() < poisson_rate else 0

        for _ in range(num_new_investors):
            investor_id = f"Investor_{len(portfolio) + 1}"
            new_investor = create_investor(day)
            portfolio[investor_id] = new_investor
            total_investment += new_investor["investment"]

        # Calculate percentages and create daily snapshot
        day_data = {
            "day": day,
            "totalInvestment": total_investment,
            "numInvestors": sum(1 for inv in portfolio.values() if inv["isActive"]),
            "activeInvestors": 0,
            "percentages": {}
        }

        for investor_id, investor in portfolio.items():
            if investor["isActive"]:
                day_data[f"{investor_id}_pct"] = (investor["investment"] / total_investment) * 100
                day_data["activeInvestors"] += 1
            else:
                day_data[f"{investor_id}_pct"] = 0

        history.append(day_data)

    return pd.DataFrame(history)

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
