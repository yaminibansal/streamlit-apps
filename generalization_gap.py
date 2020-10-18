import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import copy
import urllib

@st.cache
def get_gen_data():
    gen_gap_url = 'https://raw.githubusercontent.com/yaminibansal/streamlit-apps/main/gen_gap.csv'
    df = pd.read_csv(gen_gap_url)
    
    return df


try:
    vary_noise_df = get_gen_data()
    
except urllib.error.URLError as e:
    st.error(
        """
        **This demo requires internet access.**

        Connection error: %s
    """
        % e.reason
    )

newnames = ['ResNet 18',
           'Wide ResNet',
           'ConvNet',
           'AMDIM',
           'MoCoV2',
           'SimCLR']
names =sorted(vary_noise_df.model_name.unique())
vary_noise_df.sort_values(['train_noise_prob','model_name'],inplace=True)
# Create figure
fig = go.Figure()
noise_levels = sorted(vary_noise_df.train_noise_prob.unique())
print(noise_levels)
# Add traces, one for each slider step
for noise in noise_levels:
    fig.add_trace(
        go.Scatter(
            visible=False,
            marker=dict(color="#00CED1", size=15),
            name="Train",
            x= newnames,
            y= vary_noise_df[vary_noise_df.train_noise_prob==noise]['Train Acc'],
            mode='markers'))
    fig.add_trace(
        go.Scatter(
            visible=False,
            marker=dict(color="#a83277", size=15),
            name="Test",
            x= newnames,
            y= vary_noise_df[vary_noise_df.train_noise_prob==noise]['Dirty Test'],
            mode='markers' ))
    
    cnt = 0
    for (name, newname) in zip(names, newnames):
        tmp_df = vary_noise_df[vary_noise_df["model_name"]==name]
        tmp_df = tmp_df[tmp_df["train_noise_prob"]==noise]
        test_acc = tmp_df["Dirty Test"].values
        train_acc = tmp_df["Train Acc"].values

        if len(test_acc)!=0: 

            fig.add_trace(
                go.Scatter(
            visible=False,
            line=dict(
                color="Black",
                width=3
            ),
            x= [newname]*100,
            y= np.linspace(test_acc[0], train_acc[0], 100),
            ))

        cnt += 1

fig.add_shape(
        # Line Vertical
        dict(
            type="line",
            x0=2.5,
            y0=0,
            x1=2.5,
            y1=110,
            line=dict(
                color="Grey",
                width=3,
                dash="dot"
            )
))

# Make 10th trace visible
fig.data[0].visible = True
fig.data[1].visible = True
for i in range(6):
    fig.data[i+2].visible = True

# Create and add slider
steps = []
for i in range(len(noise_levels)):
    step = dict(
        method="update",
        label = str(noise_levels[i]),
        args=[{"visible": [False] * 8*len(fig.data)} 
              , {"title": f"Generalization gap (noise = {noise_levels[i]:.2f})" }],  # layout attribute
    )
    step["args"][0]["visible"][8*i] = True  # Toggle i'th trace to "visible"
    step["args"][0]["visible"][8*i+1] = True  # Toggle i'th trace to "visible"
    for j in range(6):
        step["args"][0]["visible"][8*i+j+2] = True
        if (8*i+j+2) < len(fig.data):
            fig.data[8*i+j+2]["showlegend"] = False

    steps.append(step)

sliders = [dict(
    active=0.0,
    currentvalue={"visible": False},
    pad={"t": 70},
    steps=steps
)]

fig.update_layout(
    sliders=sliders,
    title = dict(text = f"Generalization gap (noise = {0:.2f})",
                 y = .91,
                 x = 0.5,    
             xanchor= 'center',
             yanchor= 'top'),
#                 size = 16),
    annotations = [dict(xref='paper',
                        yref='paper',
                        x=0.1, y=1.1,
                        showarrow=False,
                        text ='End-to-end Supervision',
                        font = dict(size = 16)),
                    dict(xref='paper',
                        yref='paper',
                        x=0.9, y=1.1,
                        showarrow=False,
                        text ='SSS algorithms',
                        font = dict(size = 16))
                        ],
    font = dict(size = 16)
)

fig['layout']['sliders'][0]['pad']=dict(r= 10, t= 80,)

st.plotly_chart(fig)
