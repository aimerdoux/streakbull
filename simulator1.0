import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
from io import BytesIO

def calculate_performance_fee(return_pct, lock_period):
    """Calculate performance fee based on return range and lock period"""
    if lock_period == 6:
        if return_pct <= 12:
            return 0.12  # 12%
        elif return_pct <= 25:
            return 0.18  # 18%
        elif return_pct <= 40:
            return 0.25  # 25%
        else:
            return 0.32  # 32%
    else:  # 12 month lock period
        if return_pct <= 12:
            return 0.12  # 12%
        elif return_pct <= 25:
            return 0.15  # 15%
        elif return_pct <= 40:
            return 0.20  # 20%
        else:
            return 0.25  # 25%

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
    
    # Weekly rates (applied from the start)
    pessimistic_weekly = (1 + 0.1857) ** (1/52) - 1
    moderate_weekly = (1 + 0.2950) ** (1/52) - 1
    optimistic_weekly = (1 + 0.5900) ** (1/52) - 1
    
    # Calculate returns from the start
    for week in range(1, weeks):
        # Apply returns and add savings
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
    
    # Calculate fees based on lock period
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
