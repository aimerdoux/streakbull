import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

def calculate_investment_scenarios(initial_capital, weekly_savings, weeks, lock_period):
    # Generate weekly timestamps
    dates = [datetime.now() + timedelta(weeks=x) for x in range(weeks)]
    
    # Calculate cumulative savings
    cumulative_savings = [initial_capital + (weekly_savings * i) for i in range(weeks)]
    
    # Calculate different scenarios
    pessimistic = [initial_capital]
    moderate = [initial_capital]
    optimistic = [initial_capital]
    
    # Weekly rates
    pessimistic_weekly = (1 + 0.1857) ** (1/52) - 1  # 18.57% annual
    moderate_weekly = (1 + 0.2950) ** (1/52) - 1     # 29.50% annual
    optimistic_weekly = (1 + 0.5900) ** (1/52) - 1   # 59.00% annual
    
    for week in range(1, weeks):
        if week < lock_period:
            # During lock period, only accumulate savings
            pessimistic.append(pessimistic[-1] + weekly_savings)
            moderate.append(moderate[-1] + weekly_savings)
            optimistic.append(optimistic[-1] + weekly_savings)
        else:
            # After lock period, apply returns
            pessimistic.append(pessimistic[-1] * (1 + pessimistic_weekly) + weekly_savings)
            moderate.append(moderate[-1] * (1 + moderate_weekly) + weekly_savings)
            optimistic.append(optimistic[-1] * (1 + optimistic_weekly) + weekly_savings)
    
    return {
        'dates': dates,
        'savings': cumulative_savings,
        'pessimistic': pessimistic,
        'moderate': moderate,
        'optimistic': optimistic
    }

def main():
    st.set_page_config(page_title="Acervus Capital Investment Simulator", layout="wide")
    
    st.title("Simulador de Inversión Acervus Capital")
    st.markdown("""
    Este simulador te permite visualizar diferentes escenarios de inversión basados en:
    - Escenario Pesimista (1X QQQ 2024: 18.57% Anual)
    - Escenario Moderado (1X Acervus 2024: 29.50% Anual)
    - Escenario Optimista (2X Acervus 2024: 59.00% Anual)
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        initial_capital = st.number_input(
            "Capital Inicial (USD)", 
            min_value=1000,
            value=5000,
            step=1000
        )
        
        weekly_savings = st.number_input(
            "Ahorro Semanal (USD)",
            min_value=0,
            value=100,
            step=50
        )
    
    with col2:
        weeks = st.slider(
            "Período de Simulación (Semanas)",
            min_value=10,
            max_value=260,
            value=52
        )
        
        lock_period = st.slider(
            "Período de Bloqueo (Semanas)",
            min_value=0,
            max_value=52,
            value=26
        )
    
    # Calculate scenarios
    results = calculate_investment_scenarios(
        initial_capital,
        weekly_savings,
        weeks,
        lock_period
    )
    
    # Create plot
    fig = go.Figure()
    
    # Add traces
    fig.add_trace(go.Scatter(
        x=results['dates'],
        y=results['savings'],
        name="Depósitos acumulados",
        line=dict(dash='dash', color='blue')
    ))
    
    fig.add_trace(go.Scatter(
        x=results['dates'],
        y=results['pessimistic'],
        name="Escenario Pesimista",
        line=dict(color='red')
    ))
    
    fig.add_trace(go.Scatter(
        x=results['dates'],
        y=results['moderate'],
        name="Escenario Moderado",
        line=dict(color='orange')
    ))
    
    fig.add_trace(go.Scatter(
        x=results['dates'],
        y=results['optimistic'],
        name="Escenario Optimista",
        line=dict(color='green')
    ))
    
    # Update layout
    fig.update_layout(
        title="Simulación de Flujos: Depósitos vs. Inversión",
        xaxis_title="Fecha",
        yaxis_title="Valor Acumulado (USD)",
        hovermode='x unified',
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display summary statistics
    st.subheader("Resumen de Inversión")
    final_values = pd.DataFrame({
        'Escenario': ['Depósitos', 'Pesimista', 'Moderado', 'Optimista'],
        'Valor Final': [
            results['savings'][-1],
            results['pessimistic'][-1],
            results['moderate'][-1],
            results['optimistic'][-1]
        ]
    })
    final_values['Valor Final'] = final_values['Valor Final'].map('${:,.2f}'.format)
    st.table(final_values)

if __name__ == "__main__":
    main()
