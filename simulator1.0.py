import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
from io import BytesIO

def export_to_excel(results):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    df = pd.DataFrame({
        'Fecha': results['dates'],
        'Depósitos Acumulados': results['savings'],
        'Escenario Pesimista': results['pessimistic'],
        'Escenario Moderado': results['moderate'],
        'Escenario Optimista': results['optimistic'],
        'Drawdown Pesimista (%)': results['drawdown_pess'],
        'Drawdown Moderado (%)': results['drawdown_mod'],
        'Drawdown Optimista (%)': results['drawdown_opt']
    })
    
    df.to_excel(writer, sheet_name='Simulación', index=False)
    writer.close()
    
    return output.getvalue()

def calculate_performance_fee(return_pct, lock_period):
    """Calculate performance fee based on return range and lock period"""
    if lock_period == 6:
        if return_pct <= 15:
            return 0.18  # 18%
        elif return_pct <= 35:
            return 0.24  # 24%
        elif return_pct <= 60:
            return 0.33  # 33%
        else:
            return 0.39  # 39%
    else:  # 12 month lock period
        if return_pct <= 15:
            return 0.15  # 15%
        elif return_pct <= 35:
            return 0.19  # 19%
        elif return_pct <= 60:
            return 0.27  # 27%
        else:
            return 0.33  # 33%

def calculate_drawdown(values):
    """Calculate the maximum drawdown for a series of values"""
    peak = values[0]
    drawdowns = []
    for value in values:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak * 100
        drawdowns.append(drawdown)
    return drawdowns

def calculate_investment_scenarios(initial_capital, periodic_savings, periods, lock_period, savings_frequency, include_savings):
    # Convert periods to weeks for internal calculations
    if savings_frequency == 'Mensual':
        weeks = periods * 4
        savings_weekly = periodic_savings / 4 if include_savings else 0
    elif savings_frequency == 'Trimestral':
        weeks = periods * 12
        savings_weekly = periodic_savings / 12 if include_savings else 0
    else:  # Weekly
        weeks = periods
        savings_weekly = periodic_savings if include_savings else 0
    
    dates = [datetime.now() + timedelta(weeks=x) for x in range(weeks)]
    cumulative_savings = [initial_capital + (savings_weekly * i) for i in range(weeks)]
    
    # Initialize scenario arrays
    pessimistic = [initial_capital]
    moderate = [initial_capital]
    optimistic = [initial_capital]
    
    # Weekly rates (based on historical performance)
    pessimistic_weekly = (1 + 0.1857) ** (1/52) - 1  # QQQ baseline
    moderate_weekly = (1 + 0.2950) ** (1/52) - 1     # StreakBull baseline
    optimistic_weekly = (1 + 0.6500) ** (1/52) - 1   # Enhanced StreakBull (updated to 65%)
    
    # Calculate returns
    for week in range(1, weeks):
        pess_return = pessimistic[-1] * (1 + pessimistic_weekly)
        mod_return = moderate[-1] * (1 + moderate_weekly)
        opt_return = optimistic[-1] * (1 + optimistic_weekly)
        
        pessimistic.append(pess_return + savings_weekly)
        moderate.append(mod_return + savings_weekly)
        optimistic.append(opt_return + savings_weekly)
    
    # Calculate drawdowns
    drawdown_pess = calculate_drawdown(pessimistic)
    drawdown_mod = calculate_drawdown(moderate)
    drawdown_opt = calculate_drawdown(optimistic)
    
    # Calculate final returns
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
        'drawdown_pess': drawdown_pess,
        'drawdown_mod': drawdown_mod,
        'drawdown_opt': drawdown_opt,
        'fees': fees,
        'returns': final_returns
    }

def main():
    st.set_page_config(
        page_title="StreakBull Investment Simulator",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.markdown("""
        <style>
        .stApp {
            background-color: #0E1117;
            color: white;
        }
        .stButton>button {
            background-color: #4B0082;
            color: white;
        }
        div[data-testid="stToolbar"] {
            background-color: #0E1117;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown(
        """
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 2rem;">
            <img src="https://raw.githubusercontent.com/aimerdoux/streakbull/main/Logo%20(1).png" width="200"/>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    st.title("Simulador de Inversión StreakBull")
    
    # Technical Information Expander
    with st.expander("Información Técnica de StreakBull"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ### Métricas de Rendimiento vs S&P 500 (2021-2024)
            - Retorno Total: 96.16% vs 60.78%
            - Máximo Drawdown: -15.1% vs -24.5%
            - Correlación: 0.40
            - Desviación Estándar Diaria: 0.73%
            - Ratio de Sharpe: 1.33
            """)
        with col2:
            st.markdown("""
            ### Composición de Cartera
            - Renta Variable y Bonos: 70%
            - Commodities: 20%
            - Estrategias de Cobertura: 10%
            
            ### Filosofía de Inversión
            - Sistemas impulsados por IA
            - Enfoque multi-temporal
            - Asignación dinámica de efectivo
            """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        initial_capital = st.number_input(
            "Capital Inicial (USD)", 
            min_value=1000,
            value=5000,
            step=1000
        )
        
        include_savings = st.toggle("Incluir Ahorros Periódicos", value=True)
        
        if include_savings:
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
        else:
            savings_frequency = 'Mensual'
            periodic_savings = 0
    
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
    
    show_drawdown = st.checkbox("Mostrar Drawdown", value=False)
    
    results = calculate_investment_scenarios(
        initial_capital,
        periodic_savings,
        periods,
        lock_period,
        savings_frequency,
        include_savings
    )
    
    fig = go.Figure()
    
    if include_savings:
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
    
    # Add historical max drawdown line
    max_value = max(max(results['pessimistic']), max(results['moderate']), max(results['optimistic']))
    drawdown_line = [-15.1] * len(results['dates'])  # Historical max drawdown
    
    fig.add_trace(go.Scatter(
        x=results['dates'],
        y=drawdown_line,
        name="Máximo Drawdown Histórico (-15.1%)",
        line=dict(color='red', dash='dash'),
        visible=show_drawdown
    ))
    
    if show_drawdown:
        fig.add_trace(go.Scatter(
            x=results['dates'],
            y=[-x for x in results['drawdown_pess']],
            name="Drawdown Pesimista",
            line=dict(color='red', dash='dot')
        ))
        
        fig.add_trace(go.Scatter(
            x=results['dates'],
            y=[-x for x in results['drawdown_mod']],
            name="Drawdown Moderado",
            line=dict(color='orange', dash='dot')
        ))
        
        fig.add_trace(go.Scatter(
            x=results['dates'],
            y=[-x for x in results['drawdown_opt']],
            name="Drawdown Optimista",
            line=dict(color='green', dash='dot')
        ))
    
    fig.update_layout(
        title="Simulación de Flujos: Depósitos vs. Inversión",
        xaxis_title="Fecha",
        yaxis_title="Valor Acumulado (USD)",
        hovermode='x unified',
        height=600,
        paper_bgcolor='#0E1117',
        plot_bgcolor='#0E1117',
        font=dict(color='white'),
        xaxis=dict(gridcolor='#333333'),
        yaxis=dict(gridcolor='#333333')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
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
    
    # Add historical crisis performance table
    st.subheader("Rendimiento Histórico en Crisis")
    crisis_data = {
        'Período': ['2008 Q1', '2008 Q3', '2015 Q3', '2018 Q4', '2020 Q1', '2022 Q1-Q3'],
        'Evento': ['Crisis Hipotecaria', 'Crisis de Deuda', 'Crisis Griega', 'Guerra Comercial', 'COVID-19', 'Rusia/Inflación US'],
        'S&P 500': ['-9.45%', '-8.37%', '-6.44%', '-14.31%', '-20.1%', '-23.1%'],
        'StreakBull MS': ['+0.68%', '+0.92%', '-0.2%', '-0.12%', '-1.50%', '-2.8%']
    }
    st.table(pd.DataFrame(crisis_data))
    
    # Export results button
    if st.button('Exportar Resultados'):
        excel_data = export_to_excel(results)
        b64 = base64.b64encode(excel_data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="simulacion_streakbull.xlsx">Descargar Excel</a>'
        st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
