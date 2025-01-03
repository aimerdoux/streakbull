import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
from io import BytesIO

def calculate_performance_fee(return_pct, lock_period):
    """Calculate performance fee based on return range and lock period"""
    if return_pct <= 12:
        return 0.10  # 10%
    elif return_pct <= 25:
        return 0.18  # 18%
    elif return_pct <= 40:
        return 0.25  # 25%
    else:
        return 0.32  # 32%

def calculate_investment_scenarios(initial_capital, periodic_savings, periods, lock_period, savings_frequency):
    # Convert periods to weeks for internal calculations
    if savings_frequency == 'Mensual':
        weeks = periods * 4
        savings_weekly = periodic_savings / 4
    elif savings_frequency == 'Trimestral':
        weeks = periods * 12
        savings_weekly = periodic_savings / 12
    else:  # Weekly
        weeks = periods
        savings_weekly = periodic_savings
    
    # Generate timestamps
    dates = [datetime.now() + timedelta(weeks=x) for x in range(weeks)]
    
    # Calculate cumulative savings
    cumulative_savings = [initial_capital + (savings_weekly * i) for i in range(weeks)]
    
    # Initialize scenario arrays
    pessimistic = [initial_capital]
    moderate = [initial_capital]
    optimistic = [initial_capital]
    
    # Weekly rates
    pessimistic_weekly = (1 + 0.1857) ** (1/52) - 1
    moderate_weekly = (1 + 0.2950) ** (1/52) - 1
    optimistic_weekly = (1 + 0.5900) ** (1/52) - 1
    
    # Convert lock period to weeks
    lock_weeks = lock_period * 4
    
    for week in range(1, weeks):
        if week < lock_weeks:
            # During lock period, only accumulate savings
            pessimistic.append(pessimistic[-1] + savings_weekly)
            moderate.append(moderate[-1] + savings_weekly)
            optimistic.append(optimistic[-1] + savings_weekly)
        else:
            # After lock period, apply returns and fees
            pess_return = pessimistic[-1] * (1 + pessimistic_weekly)
            mod_return = moderate[-1] * (1 + moderate_weekly)
            opt_return = optimistic[-1] * (1 + optimistic_weekly)
            
            pessimistic.append(pess_return + savings_weekly)
            moderate.append(mod_return + savings_weekly)
            optimistic.append(opt_return + savings_weekly)
    
    # Calculate final returns for fee calculation
    final_returns = {
        'pessimistic': (pessimistic[-1] - cumulative_savings[-1]) / cumulative_savings[-1] * 100,
        'moderate': (moderate[-1] - cumulative_savings[-1]) / cumulative_savings[-1] * 100,
        'optimistic': (optimistic[-1] - cumulative_savings[-1]) / cumulative_savings[-1] * 100
    }
    
    # Calculate fees
    fees = {
        'pessimistic': calculate_performance_fee(final_returns['pessimistic'], lock_period),
        'moderate': calculate_performance_fee(final_returns['moderate'], lock_period),
        'optimistic': calculate_performance_fee(final_returns['optimistic'], lock_period)
    }
    
    return {
        'dates': dates,
        'savings': cumulative_savings,
        'pessimistic': pessimistic,
        'moderate': moderate,
        'optimistic': optimistic,
        'fees': fees,
        'returns': final_returns
    }

def export_to_excel(results):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    # Create DataFrame with results
    df = pd.DataFrame({
        'Fecha': results['dates'],
        'Depósitos Acumulados': results['savings'],
        'Escenario Pesimista': results['pessimistic'],
        'Escenario Moderado': results['moderate'],
        'Escenario Optimista': results['optimistic']
    })
    
    df.to_excel(writer, sheet_name='Simulación', index=False)
    writer.close()
    
    return output.getvalue()

def main():
    st.set_page_config(page_title="StreakBull Investment Simulator", layout="wide")
    
    # Display StreakBull logo
    st.image("path_to_bull_logo.png", width=200)  # Update with actual logo path
    
    st.title("Simulador de Inversión StreakBull")
    st.markdown("""
    Este simulador te permite visualizar diferentes escenarios de inversión basados en:
    - Escenario Pesimista (1X QQQ 2024: 18.57% Anual)
    - Escenario Moderado (1X StreakBull 2024: 29.50% Anual)
    - Escenario Optimista (2X StreakBull 2024: 59.00% Anual)
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        initial_capital = st.number_input(
            "Capital Inicial (USD)", 
            min_value=1000,
            value=5000,
            step=1000
        )
        
        savings_frequency = st.selectbox(
            "Frecuencia de Ahorro",
            options=['Semanal', 'Mensual', 'Trimestral']
        )
        
        periodic_savings = st.number_input(
            f"Ahorro {savings_frequency} (USD)",
            min_value=0,
            value=100,
            step=50
        )
    
    with col2:
        if savings_frequency == 'Semanal':
            periods = st.slider("Semanas de Simulación", 10, 260, 52)
        elif savings_frequency == 'Mensual':
            periods = st.slider("Meses de Simulación", 3, 60, 12)
        else:
            periods = st.slider("Trimestres de Simulación", 1, 20, 4)
        
        lock_period = st.radio(
            "Período de Bloqueo",
            options=[6, 12],
            format_func=lambda x: f"{x} meses"
        )
    
    # Calculate scenarios
    results = calculate_investment_scenarios(
        initial_capital,
        periodic_savings,
        periods,
        lock_period,
        savings_frequency
    )
    
    # Create plot
    fig = go.Figure()
    
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
    
    fig.update_layout(
        title="Simulación de Flujos: Depósitos vs. Inversión",
        xaxis_title="Fecha",
        yaxis_title="Valor Acumulado (USD)",
        hovermode='x unified',
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display summary statistics and fees
    st.subheader("Resumen de Inversión")
    
    final_values = pd.DataFrame({
        'Escenario': ['Depósitos', 'Pesimista', 'Moderado', 'Optimista'],
        'Valor Final': [
            results['savings'][-1],
            results['pessimistic'][-1],
            results['moderate'][-1],
            results['optimistic'][-1]
        ],
        'Retorno (%)': [
            0,
            results['returns']['pessimistic'],
            results['returns']['moderate'],
            results['returns']['optimistic']
        ],
        'Comisión de Performance': [
            '0%',
            f"{results['fees']['pessimistic']*100}%",
            f"{results['fees']['moderate']*100}%",
            f"{results['fees']['optimistic']*100}%"
        ]
    })
    
    final_values['Valor Final'] = final_values['Valor Final'].map('${:,.2f}'.format)
    final_values['Retorno (%)'] = final_values['Retorno (%)'].map('{:.2f}%'.format)
    
    st.table(final_values)
    
    # Export results button
    if st.button('Exportar Resultados'):
        excel_data = export_to_excel(results)
        b64 = base64.b64encode(excel_data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="simulacion_streakbull.xlsx">Descargar Excel</a>'
        st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
