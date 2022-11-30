import streamlit as st
import requests
import math
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time
from htbuilder import div, big, h2, styles
from htbuilder.units import rem
from streamlit_lottie import st_lottie
from streamlit_lottie import st_lottie_spinner
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(page_title="in sync.")

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

@st.experimental_memo
def processing(d):
    # url = "http://127.0.0.1:8000/vid_process"
    url = "https://syncv9-eagwezifvq-an.a.run.app/vid_process"
    params = {k:d[k] for k in d if k!='dim'}
    response = requests.get(url, params=params).json()
    return response
            

@st.experimental_memo
def fetch_stats(uploaded_video):
    url = "https://syncv9-eagwezifvq-an.a.run.app/vid_stats"
    # url = "http://127.0.0.1:8000/vid_stats"
    files = {"file": (uploaded_video.name, uploaded_video, "multipart/form-data")}
    stats = requests.post(url, files=files).json()
    return stats

def main():

    #build header
    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        st_lottie(lottie_dancing, key="dance_left")
    with col2:
        with col2:
            st.markdown("<h1 style='text-align: center; color: RebeccaPurple;'>in sync.</h1>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center; color: #ff008c;'>Your personal AI<br/>synchronisation assistant.</h3>", unsafe_allow_html=True)
    with col3:
        st_lottie(lottie_dancing, key="dance_right")


    #Receive video file from user upload
    uploaded_video = st.file_uploader("**Upload video for evaluation**", ['mp4'], key='dance')
    #If video has been uploaded
    if uploaded_video is not None:

        if 'video' not in st.session_state or uploaded_video.name != st.session_state.video:
            st.session_state.video = uploaded_video.name
            st.session_state.response = None

        show_vid = st.video(uploaded_video)
        with st_lottie_spinner(lottie_model_loading):
            stats = fetch_stats(uploaded_video)

        a, b, c = st.columns([2,2,3])
        with a:
            display_dial("FPS", f"{stats['fps']}", "#ff008c")
        with b:
            display_dial("FRAMES", f"{stats['frame_count']}", "#ff008c")
        with c:
            display_dial("DIMENSION", f"{stats['dim']}", "#ff008c")


        # a, b, c = st.columns(3)
        # with a:
        #     dancers = st.number_input("Number of dancers (1-6):", value=2, min_value=1, max_value=6)
        #     stats['dancers'] = dancers
        # with b:
        #     conf = st.number_input("Model confidence interval (0-100):", value=20, min_value=0, max_value=100)
        #     stats['conf_threshold'] = conf
        # with c:
        #     face = st.selectbox("Ignore faces:", ("True", "False"))
        #     stats['face_ignored'] = face

        # st.markdown(
        #             """
        #             <style>
        #             [data-testid="stSidebar"][aria-expanded="true"] > div:first-child{
        #                 width : 350px
        #             }
        #             [data-testid="stSidebar"][aria-expanded="false"] > div:first-child{
        #                 width : 350px
        #                 margin-left: -350px
        #             }
        #             </style>
        #             """,
        #             unsafe_allow_html=True
        # )
        with st.sidebar:
            dancers = st.number_input("Number of dancers (1-6):", value=2, min_value=1, max_value=6)
            stats['dancers'] = dancers
            conf = st.number_input("Confidence interval (0-100%):", value=20, min_value=0, max_value=100)
            stats['conf_threshold'] = conf / 100
            face = st.selectbox("Ignore faces:", ("True", "False"))
            stats['face_ignored'] = face


        if st.sidebar.checkbox("Click to start (RESET this checkbox to upload new video)"):

            show_vid.empty()
            st.text('')
            
            if st.session_state.response is not None:
                response = st.session_state.response 
            else:
                #clear caches
                fetch_stats.clear()
                processing.clear()
                with st_lottie_spinner(lottie_model_loading, key='xd'):
                    response = processing(stats)
                st.session_state.response = response
            
            #Empty space
            st.text('')

            #Create df
            d = {
                'Time': response['timestamps'],
                'Error': response['scores'],
                'Link_scores': response['link_scores'],
                'Link_names': response['link_names']
            }
            df = pd.DataFrame(d)
            df['frames'] = df.index
            df['Smoothed_error'] = df['Error'].rolling(window=9).mean()
            df['Smoothed_link_error'] = df['Link_scores'].rolling(window=9).mean()
            
            #graph on-click
            def go_to_frame(trace, points, selector):
                # index = df.index[df['Time']==].tolist()
                st.write("test: ", trace, points, selector)
                st.image(f'https://storage.googleapis.com/sync_testinput/screencaps/frame1.jpg')

            # fig = go.FigureWidget([go.Line(x=d['Time'], y=d['Error'])])
            # image_placeholder = st.empty()
            fig = px.line(df, x='frames', y='Smoothed_error', title='Synchronisation Analysis',
                            hover_name='frames', labels={
                                                     "frames": "Frame Number",
                                                     "Smoothed_error": "Mean Absolute Error",
                                                    },
                    )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=False)
            fig.update_traces(line_color="#ff008c")
            fig = go.FigureWidget(fig.data, fig.layout)
            fig.data[0].on_click(go_to_frame)

            fig2 = px.line(df, x='frames', y='Smoothed_link_error', title='Worst Actions',
                            hover_name='Link_names', labels={
                                                     "frames": "Frame Number",
                                                     "Smoothed_link_error": "Max Error Body Part",
                                                    },
                    )
            fig2.update_xaxes(showgrid=False)
            fig2.update_yaxes(showgrid=False)
            fig2.update_traces(line_color="#ff008c")

            #Load processed video
            a, b = st.columns([1,4])
            with a:
                colours = [
                    st.color_picker('Perfect', '#41961A'),
                    st.color_picker('Good Effort', '#A6D96A'),
                    st.color_picker('Average', '#FDAE61'),
                    st.color_picker('You Suck', '#D7191C')
                ]
            with b:
                video_url = response['output_url']
                st.video(video_url)
            
            st.plotly_chart(fig, use_container_width=True)
            st.plotly_chart(fig2, use_container_width=True)

            with st.expander("**Score Card:**"):
                #overall score sensitive to outliers
                scaler = MinMaxScaler()
                df['scaled'] = scaler.fit_transform(np.array(df['Error']).reshape(-1,1))
                overall_score = (1 - df['scaled'].mean()) * 100
                st.write("Overall score: ", overall_score, "%")
                #split dataframe into equal parts
                df_sorted = df.sort_values(by=['Error'])
                split = np.array_split(df_sorted, 4)
                st.write("Score for each quartile:")
                for i, df_sorted in enumerate(split):
                    st.write(i+1, ": ", df_sorted['Error'].mean())

            with st.expander('**View freeze frames:**'):
                frame = st.slider("View frames starting from choice", 0, int(stats['frame_count']), 0, label_visibility='hidden')
                a, b = st.columns(2, gap='medium')
                with a:
                    st.image(f"https://storage.googleapis.com/sync_testinput/screencaps/{response['my_uuid']}/frame{frame}.jpg")
                with b:
                    st.image(f"https://storage.googleapis.com/sync_testinput/screencaps/{response['my_uuid']}/frame{frame+1}.jpg")
                c, d = st.columns(2)
                with c:
                    st.image(f"https://storage.googleapis.com/sync_testinput/screencaps/{response['my_uuid']}/frame{frame+2}.jpg")
                with d:
                    st.image(f"https://storage.googleapis.com/sync_testinput/screencaps/{response['my_uuid']}/frame{frame+3}.jpg")

            with st.expander("**Model info:**"):
                st.dataframe(df)
                # fig3 = go.Figure(data=[go.Table(
                #     header=dict(values=list(df.columns),
                #                 fill_color='paleturquoise',
                #                 align='left'),
                #     cells=dict(values=[df.frames, df.Time, df.Error, df.Link_names, d.Link_scores],
                #                fill_color='lavender',
                #                align='left'))
                # ])
                # st.plotly_chart(fig3)

if __name__ == '__main__':
    main()
