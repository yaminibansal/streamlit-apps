import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import copy
import urllib

@st.cache
def cf_data():
    gen_gap_url = 'https://raw.githubusercontent.com/yaminibansal/tmp/main/cf10_repo.csv'
    df = pd.read_csv(gen_gap_url)
    
    return df


try:
    df = cf_data()
    
except urllib.error.URLError as e:
    st.error(
        """
        **This demo requires internet access.**

        Connection error: %s
    """
        % e.reason
    )

def hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = hex_color * 2
    return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

############# Colors ###############
############# Colors ###############
cpurple_shade = '#FCFDBD'
cred_shade = '#F3D19D'
cgreen_shade = '#C9E6A6'
cgrey = '#666666' #[0.4, 0.4, 0.4]

cpurple = '#F9E378' #'#F9E3AB' #F9E378
cred = '#F36D44'
cgreen=  '#49AD67'
cyellow  = '#5EA8B1'
crrm = '#4B7F69' #

fill_transparency = 0.5

memorization = df["Memorization"]
gen_gap = df["Generalization Gap"]
robustness = df["Robustness"]
rationality = df["Rationality"]
bound = np.minimum(robustness+rationality + df["Theorem II bound"], 100)


var_list = [(df["Memorization"], 'Memorization Gap', cred, cred_shade), 
            (df["Rationality"], 'Rationality Gap', cpurple, cpurple_shade), 
            (df["Robustness"], 'Robustness Gap', cgreen, cgreen_shade)
]

fig = go.Figure()

var = np.zeros(len(memorization))
for (current_var, name, clr, clr_shade) in var_list:
    old_var = copy.copy(var)
    var += current_var
    fig.add_trace(go.Scatter(x=gen_gap.values, y=var.values, fill='tonexty', mode='lines', fillcolor=clr_shade, line=dict(width=0., color=clr_shade), showlegend=False,))

fig.add_trace(go.Scatter(x=gen_gap.values, y=bound.values, fill='tonexty', mode='lines+markers', 
                         fillcolor=f"rgba{(*hex_to_rgb(cyellow), 0.1)}", marker=dict(size=5, color=cyellow), line=dict(width=0., color=clr_shade), name="Theorem II Bound"))

var = np.zeros(len(memorization))
for (current_var, name, clr, clr_shade) in var_list:
    old_var = copy.copy(var)
    var += current_var
    for i, (gen_gap_val, old_var_val, var_val) in enumerate(zip(gen_gap, old_var, var)):
        if i!=0:
            fig.add_trace(go.Scatter(x=[gen_gap_val]*2, y=[old_var_val, var_val], mode='lines', line=dict(width=3., color=clr), showlegend=False))
        else:
            fig.add_trace(go.Scatter(x=[gen_gap_val]*2, y=[old_var_val, var_val], mode='lines', line=dict(width=3., color=clr), name=name))


fig.add_trace(go.Scatter(x=gen_gap.values, y=var, mode='lines', line=dict(width=1.8, color=crrm, dash="solid"), name="Empirical RRM Bound"))
fig.add_trace(go.Scatter(x=gen_gap.values, y=gen_gap.values, mode='lines', line=dict(width=1.8, color=cgrey, dash="dash"), name="Generalization Gap"))

fig.update_layout(template='ggplot2', yaxis=dict(range=[-0.01,60], title="value"), xaxis=dict(title="Generalization Gap"),
                  font=dict(size=18))

fig.show()

st.plotly_chart(fig)
