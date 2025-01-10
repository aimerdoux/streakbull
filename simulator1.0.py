# Previous imports remain the same
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
from io import BytesIO

# [Previous functions remain unchanged]

def main():
    st.set_page_config(page_title="StreakBull Investment Simulator", layout="wide")
    
    # Remove the problematic logo line and replace with markdown centered image
    st.markdown(
        """
        <div style="text-align: center;">
            <img src="https://raw.githubusercontent.com/aimerdoux/streakbull/main/Logo%20(1).png" width="200"/>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Rest of your main() function remains the same
    st.title("Simulador de Inversión StreakBull")
    # [Rest of the code remains unchanged]

if __name__ == "__main__":
    main()
