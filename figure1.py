import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import copy
import urllib

@st.cache
def cf_data(dataname):
    if dataname=='CIFAR10':
        gen_gap_url = 'https://raw.githubusercontent.com/yaminibansal/streamlit-apps/main/cf10_repo.csv'
    elif dataname=='ImageNet':
        gen_gap_url = 'https://raw.githubusercontent.com/yaminibansal/streamlit-apps/main/in_repo.csv'
    df = pd.read_csv(gen_gap_url)
    
    return df

st.markdown("## [For self-supervised learning, Rationality implies Generalization, provably](https://arxiv.org/abs/2010.08508)")
st.markdown("### [Yamini Bansal*](https://yaminibansal.com/about/), [Gal Kaplun*](https://www.galkaplun.com/), [Boaz Barak](https://www.boazbarak.org/)")
st.markdown("We show that the generalization gap of classifiers obtained by first using self-supervision to learn a representation of the training data, and then fitting a simple (e.g., linear) classifier to the labels is small, and we can provide non-vacuous bounds for it")

dataname = st.selectbox("Dataset", ["CIFAR10", "ImageNet"], 0)


try:
    df = cf_data(dataname)
    
except urllib.error.URLError as e:
    st.error(
        """
        **This demo requires internet access.**

        Connection error: %s
    """
        % e.reason
    )

### Select aug ####
#augmentation = st.radio("Augmentation", df["Augmentation"])
method_name = st.sidebar.multiselect("Self-Supervised Method", list(df.Method.unique()), default=list(df.Method.unique()))#, default=df.Method.values)
backbone = st.sidebar.multiselect("Backbone Architecture", list(df.Backbone.unique()),
                          default=list(df.Backbone.unique()))#, default=df.Backbone.values)
aug = st.sidebar.multiselect("Augmentation", options=list(df["Data Augmentation"].unique()),
                     default=list(df["Data Augmentation"].unique()))

df = df[df["Method"].isin(method_name)]
df = df[df["Backbone"].isin(backbone)]
df = df[df["Data Augmentation"].isin(aug)]

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
method = df["Method"].values
aug = df["Data Augmentation"].values
backbone = df["Backbone"].values
test = df["Test Performance"].values



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
                         text=[f'<br>Method={meth}<br>Backbone={bb}<br>Augmentation={a}<br>Test Acc={t:.2f}' for meth, bb, a, t in zip(method, backbone, aug, test)],                         
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
fig.add_trace(go.Scatter(x=gen_gap.values, y=gen_gap.values, mode='lines', line=dict(width=1.8, color=cgrey, dash="dash"),
                         text=[f'<br>Method={meth}<br>Backbone={bb}<br>Augmentation={a}<br>Test Acc={t:.2f}' for meth, bb, a, t in zip(method, backbone, aug, test)],                         
                         name="Generalization Gap"))

fig.update_layout(template='ggplot2', yaxis=dict(range=[-0.01,60], title="value"), xaxis=dict(title="Generalization Gap"),
                  font=dict(size=14),
                  legend=dict(
                      x=0.02,
                      y=0.99,))

#fig.show()



#st.markdown("### RRM Bound for Generalization Gap of Self-Supervised + Simple Algorithms")
st.plotly_chart(fig)

st.markdown("#### Raw Data (click on column header to sort)")
df = df.drop(["Unnamed: 0"], axis=1)
st.dataframe(df)
