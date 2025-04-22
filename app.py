import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# ===== SESSION STATE ===== #
# Initialize with mandatory keys
if 'pink_zones' not in st.session_state:
    st.session_state.pink_zones = {'multipliers': [], 'indices': []}
else:  # Repair legacy states
    st.session_state.pink_zones.setdefault('multipliers', [])
    st.session_state.pink_zones.setdefault('indices', [])

if 'momentum_line' not in st.session_state:
    st.session_state.momentum_line = [0]
if 'rounds' not in st.session_state:
    st.session_state.rounds = []
if 'danger_zones' not in st.session_state:
    st.session_state.danger_zones = []

# ===== CORE ENGINE ===== #
def score_round(multiplier):
    """Raw precision scoring without rounding"""
    if multiplier < 1.5: return -1.5
    return np.interp(multiplier,
                   [1.5, 2.0, 5.0, 10.0, 20.0],
                   [-1.0, 1.0, 1.5, 2.0, 3.0])

def detect_dangers():
    """Fibonacci sequence danger detection"""
    st.session_state.danger_zones = [
        i for i in range(4, len(st.session_state.rounds))
        if sum(m < 2.0 for m in st.session_state.rounds[i-4:i+1]) >= 4
    ]

# ===== TACTICAL VISUALS ===== #
def create_battle_chart():
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12,6))
    
    # Momentum line with white dots
    momentum = pd.Series(st.session_state.momentum_line)
    ax.plot(momentum.ewm(alpha=0.75).mean(),
            color='#00fffa',
            lw=2,
            marker='o',
            markersize=8,
            markerfacecolor='white',
            markeredgecolor='white',
            zorder=4)

    # Pink reaction zones
    for mult, idx in zip(st.session_state.pink_zones['multipliers'],
                        st.session_state.pink_zones['indices']):
        ax.fill_betweenx(y=[mult*0.95, mult*1.05],
                        x1=0,
                        x2=len(momentum)-1,
                        color='#4a148c',
                        alpha=0.08)
        ax.axvline(idx,
                  color='#ff00ff',
                  linestyle=':',
                  alpha=0.4,
                  zorder=2)

    # Danger zones
    for zone in st.session_state.danger_zones:
        ax.axvspan(zone-0.5, zone+0.5, color='#d50000', alpha=0.15)

    ax.set_title("CYA TACTICAL OVERLAY v5.1", color='#00fffa', fontsize=18, weight='bold')
    ax.set_facecolor('#000000')
    return fig

# ===== INTERFACE ===== #
st.set_page_config(page_title="CYA Tactical", layout="wide")
st.title("🔥 CYA BATTLE MATRIX")

# Input panel
with st.container():
    col1, col2 = st.columns([3,1])
    with col1:
        mult = st.number_input("ENTER MULTIPLIER", 
                             1.0, 1000.0, 1.0, 0.1,
                             key='mult_input')
    with col2:
        if st.button("🚀 ANALYZE", type="primary"):
            st.session_state.rounds.append(mult)
            st.session_state.momentum_line.append(
                st.session_state.momentum_line[-1] + score_round(mult))
            
            if mult >= 10.0:
                st.session_state.pink_zones['multipliers'].append(mult)
                st.session_state.pink_zones['indices'].append(len(st.session_state.rounds)-1)
            
            detect_dangers()
            
        if st.button("🔄 FULL RESET", type="secondary"):
            st.session_state.clear()
            st.rerun()

# Main display
st.pyplot(create_battle_chart())

# Status HUD
with st.container():
    cols = st.columns(3)
    cols[0].metric("TOTAL ROUNDS", len(st.session_state.rounds))
    cols[1].metric("PINK SIGNALS", len(st.session_state.pink_zones['multipliers']))
    cols[2].progress(
        min(100, len(st.session_state.danger_zones)*20),
        text=f"ALGORITHMIC DANGER: {len(st.session_state.danger_zones)*20}%"
    )

# Alert system
if st.session_state.danger_zones:
    st.error(f"⚡ FIBONACCI TRAP PATTERNS DETECTED ({len(st.session_state.danger_zones)})")
