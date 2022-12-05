import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
from htbuilder import div, big, h2, styles
from htbuilder.units import rem
from streamlit_lottie import st_lottie
from streamlit_lottie import st_lottie_spinner
from streamlit_extras.add_vertical_space import add_vertical_space

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
    # url = "https://syncv12-eagwezifvq-an.a.run.app/vid_process"
    url = "http://127.0.0.1:8000/vid_process"
    params = {k:d[k] for k in d if k!='dim'}
    response = requests.get(url, params=params).json()
    return response
            

@st.experimental_memo
def fetch_stats(uploaded_video):
    # url = "https://syncv12-eagwezifvq-an.a.run.app/vid_stats"
    url = "http://127.0.0.1:8000/vid_stats"
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
            st.image('logo_grey.png')
            st.markdown("<h3 style='text-align: center; color: #ff008c;'>Your personal AI<br/>synchronisation assistant.</h3>", unsafe_allow_html=True)
    with col3:
        st_lottie(lottie_dancing, key="dance_right")

    add_vertical_space(3)

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

        with st.sidebar:
            dancers = st.number_input("Number of dancers (1-6):", value=2, min_value=1, max_value=6)
            stats['dancers'] = dancers
            with st.expander("Advanced settings ↓"):
                conf = st.number_input("Minimum confidence threshold (0-100%):", value=0, min_value=0, max_value=100)
                stats['conf_threshold'] = conf / 100
                face = st.selectbox("Ignore faces:", ("True", "False"))
                stats['face_ignored'] = face
                conf_d = st.selectbox("Confidence display:", ("False","True"))
                stats['confidence_display'] = conf_d


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
                'Link_names': response['link_names'],
                'bools': response['scores_bool']
            }
            df = pd.DataFrame(d)
            df['frames'] = df.index

            #separate low confidence frames
            df['good_scores'] = np.where(df['bools'] == False, df['Error'], np.nan)
            df['bad_scores'] = np.where(df['bools'] == True, df['Error'], np.nan)
            #smoother graphs
            df['Smoothed_error'] = df['Error'].rolling(window=10).mean()
            df['Smoothed_link_error'] = df['Link_scores'].rolling(window=10).mean()

            def create_fig(x, y, title, hover_name, labels):
                fig = px.line(df, x=x, y=y, title=title,
                                hover_name=hover_name, labels=labels)
                fig.update_xaxes(showgrid=False)
                fig.update_yaxes(showgrid=False)
                fig.update_traces(line_color="#ff008c")
                return fig

            fig0 = create_fig('frames', 'Smoothed_error', 'Performance Overview',
                                'frames', {'frames': 'Frame Number', 
                                           'Smoothed_error': 'Sync Error (degrees)'})
            fig0.update_layout(hovermode="x unified")

            # fig1 = create_fig('frames', 'good_scores', 'Model Inaccurracy',
            #                     'frames', {'frames': 'Frame Number', 
            #                                'Smoothed_error': 'Mean Absolute Error'})
            # fig1.update_traces(line_color="grey")
            # fig1.add_trace(
            #     go.Scatter(
            #         x=df['frames'],
            #         y=df['bad_scores'],
            #         mode="lines",
            #         line=go.scatter.Line(color="red"),
            #         name='Bad')
            # )

            fig2 = create_fig('frames', 'Smoothed_link_error', 'Link with Highest Error',
                                'Link_names', {'frames': 'Frame Number', 
                                               'Smoothed_link_error': 'Worst Link Error (degrees)'})
            fig2.update_layout(hovermode="x unified")

            #Load processed video
            a, b = st.columns([1,4])
            with a:
                colours = [
                    st.color_picker('Perfect', '#41961A'),
                    st.color_picker('Good Effort', '#A6D96A'),
                    st.color_picker('Average', '#FDAE61'),
                    st.color_picker('De-synced', '#D7191C')
                ]
            with b:
                video_url = response['output_url']
                st.video(video_url)
            
            st.plotly_chart(fig0, use_container_width=True)

            with st.expander('**View freeze frames:**'):
                frame = st.number_input("View frames starting from choice", value=0, min_value=0, max_value=int(df.shape[0]), label_visibility='hidden')
                def frame_url(f):
                    return f"https://storage.googleapis.com/sync_testinput/screencaps/{response['my_uuid']}/frame{f}.jpg"
                a, b = st.columns(2)
                with a:
                    st.image(frame_url(frame))
                with b:
                    st.image(frame_url(frame+1))
                c, d = st.columns(2)
                with c:
                    st.image(frame_url(frame+2))
                with d:
                    st.image(frame_url(frame+3))

            st.plotly_chart(fig2, use_container_width=True)

            with st.expander("**Model info:**"):
                st.dataframe(df)


if __name__ == '__main__':
    main()
