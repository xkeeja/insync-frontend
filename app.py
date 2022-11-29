import streamlit as st
import requests
import math
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time
from htbuilder import div, big, h2, styles
from htbuilder.units import rem
from streamlit_lottie import st_lottie
from streamlit_lottie import st_lottie_spinner
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(layout="wide", page_title="Dance Synchronisation")

#load css
with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

#animations
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

#load animations
lottie_url_dancing = "https://assets7.lottiefiles.com/packages/lf20_owg7kezi.json"
lottie_dancing = load_lottieurl(lottie_url_dancing)
lottie_url_api_loading = "https://assets2.lottiefiles.com/packages/lf20_rsgxuwx0.json"
lottie_api_loading = load_lottieurl(lottie_url_api_loading)
lottie_url_model_loading = "https://assets1.lottiefiles.com/packages/lf20_c9uz3mrt.json"
lottie_model_loading = load_lottieurl(lottie_url_model_loading)

#pretty stats
def display_dial(title, value, color):
        st.markdown(
            div(
                style=styles(
                    text_align="center",
                    color=color,
                    padding=(rem(0.8), 0, rem(3), 0),
                )
            )(
                h2(style=styles(font_size=rem(0.8), font_weight=400, padding=0))(title),
                big(style=styles(font_size=rem(2), font_weight=400, line_height=1))(
                    value
                ),
            ),
            unsafe_allow_html=True,
        )

def processing(d):
    if isinstance(d, dict):
        with st_lottie_spinner(lottie_model_loading, key='xd'):
            # url = "http://127.0.0.1:8000/vid_process"
            url = "https://syncv6-eagwezifvq-an.a.run.app/vid_process"
            params = {k:d[k] for k in d if k!='dim'}
            response = requests.get(url, params=params).json()

        #Create df
        st.write(response)
        d = {
            'Time': response['timestamps'],
            'Error': response['scores']
        }
        df = pd.DataFrame(d)
        df['idx'] = df.index
        
        #graph on-click
        def go_to_frame(trace, points, selector):
            # index = df.index[df['Time']==].tolist()
            st.write("test: ", trace, points, selector)
            st.image(f'https://storage.googleapis.com/sync_testinput/screencaps/frame1.jpg')

        # fig = go.FigureWidget([go.Line(x=d['Time'], y=d['Error'])])
        # image_placeholder = st.empty()
        fig = px.line(df, x='Time', y='Error', title='Synchronisation Analysis',
                        hover_name='idx')
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)
        fig.update_traces(line_color="yellow")
        fig = go.FigureWidget(fig.data, fig.layout)
        fig.data[0].on_click(go_to_frame)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # fig = px.line(df, x="Time", y="Error")
        # st.plotly_chart(fig, use_container_width=True)

        #Load processed video
        placeholder = st.empty()
        video_url = response['output_url']
        placeholder.video(video_url)

        with st.expander("**Score Card:**"):
            #overall score sensitive to outliers
            scaler = MinMaxScaler()
            d['scaled'] = scaler.fit_transform(np.array(d['Error']).reshape(-1,1))
            st.write("Overall: ", d['scaled'].mean())
            #split dataframe into equal parts
            split = np.array_split(d, 4)
            st.write("Score for each quartile:")
            for i, df in enumerate(split):
                st.write(i, ": ", df['scaled'].mean())

        with st.expander("**Model info:**"):
            st.dataframe(df)
            

def main():

    #build header
    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        st_lottie(lottie_dancing, key="dance_left")
    with col2:
        st.markdown("<h1 style='text-align: center; color: yellow;'>Dance Synchronisation</h1>", unsafe_allow_html=True)
    with col3:
        st_lottie(lottie_dancing, key="dance_right")


    #Receive video file from user upload
    uploaded_video = st.file_uploader("**Upload video for evaluation**", ['mp4'], key='dance')
    #If video has been uploaded
    if uploaded_video is not None:

        with st_lottie_spinner(lottie_model_loading):
            url = "https://syncv6-eagwezifvq-an.a.run.app/vid_stats"
            # url = "http://127.0.0.1:8000/vid_stats"
            files = {"file": (uploaded_video.name, uploaded_video, "multipart/form-data")}
            stats = requests.post(url, files=files).json()

        _, b, _ = st.columns([1,4,1])
        with b:
            show_vid = st.video(uploaded_video)

        process_vid = False
        a, b, c, _, d = st.columns([2,2,2,1,2])
        with a:
            display_dial("FPS", f"{stats['fps']}", "#1C83E1")
        with b:
            display_dial("FRAMES", f"{stats['frame_count']}", "#1C83E1")
        with c:
            display_dial("DIMENSION", f"{stats['dim']}", "#1C83E1")
        with d:
            if st.button("Start"):
                show_vid.empty()
                process_vid = True

        if process_vid:
            processing(stats)

if __name__ == '__main__':
    main()
