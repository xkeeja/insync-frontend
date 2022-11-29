import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from htbuilder import div, big, h2, styles
from htbuilder.units import rem
from streamlit_lottie import st_lottie
from streamlit_lottie import st_lottie_spinner


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


def processing(stats):
    with st_lottie_spinner(lottie_model_loading, key='xd'):
        url = "http://127.0.0.1:8000/vid_process"
        # url = "https://syncv6-eagwezifvq-an.a.run.app/vid_process"
        params = {
            "vid_name": stats['vid_name'],
            "output_name": stats['output_name'],
            "frame_count": stats['frame_count'],
            "fps": stats['fps'],
            "width": stats['width'],
            "height": stats['height'],
            "dancers": stats['dancers']
            }
        response = requests.get(url, params=params).json()

    #Create df
    d = {
        'Time': response['timestamps'],
        'Sync Error': response['scores']
    }
    df = pd.DataFrame(d)

    #Calculate moving average for smoother graph
    df['Smoothed Sync Error'] = df['Sync Error'].rolling(window=9).mean()

    #Plot moving average graph
    st.write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    st.write('The following graph shows your absolute synchronisation error, calculated as a difference in pose/angle of major joints relative to each other. A lower value is a smaller difference, and therefore better synchronization. Peaks are areas of lowest synchronisation.')
    # st.line_chart(data=df, x='Time', y='Sync Error')
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df.index, y=list(df['Sync Error'])))
    fig1.update_layout(
            title="Absolute Sync Error Graph",
            xaxis_title="Frame",
            yaxis_title="Absolute Sync Error",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="RebeccaPurple"
                ),
            hovermode='x unified')
    st.plotly_chart(fig1)


    st.write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    st.write('The following graph shows your average synchronisation error, smoothed for easier reference of intervals needing improvement or attention.')
    # st.line_chart(data=df, x='Time', y='Smoothed Sync Error')
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df.index, y=list(df['Smoothed Sync Error'])))
    fig2.update_layout(
            title="Smoothed Sync Error Graph",
            xaxis_title="Frame",
            yaxis_title="Smoothed Sync Error",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="RebeccaPurple"
                ),
            hovermode='x unified')
    st.plotly_chart(fig2)


    #Load processed video
    video_url = response['output_url']
    st.video(video_url)
    # video_file = open('video.mp4', 'rb')
    # video_bytes = video_file.read()
    # st.video(video_bytes)

    #Timestamp buttons
    sorted_df = df.sort_values(by=['Smoothed Sync Error'], ascending=False).round(2).head(5)
    index = sorted_df.head(5).index
    top5imp = [i for i in index]
    timestamps = sorted_df['Time'].to_list()
    sync = sorted_df['Smoothed Sync Error'].to_list()

    with st.expander("**Your top five areas for improvement:**"):
        for i in range(len(index)):
            st.write(f"**Frame {index[i]}**")
            st.write(f'Timestamp: {timestamps[i]}s, Absolute Sync Error: {sync[i]}')
            st.image(f"https://storage.googleapis.com/sync_testinput/screencaps/{response['my_uuid']}/frame{top5imp[i]}.jpg")
            st.write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")


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

        #Post request with video file
        with st_lottie_spinner(lottie_model_loading):
            # url = "https://syncv6-eagwezifvq-an.a.run.app/vid_stats"
            url = "http://127.0.0.1:8000/vid_stats"
            files = {"file": (uploaded_video.name, uploaded_video, "multipart/form-data")}
            stats = requests.post(url, files=files).json()

        #Return uploaded video
        _, b, _ = st.columns([1,4,1])
        with b:
            show_vid = st.video(uploaded_video)
        
        # a, b, c = st.columns(3)
        # with a:
        #     display_dial("FPS", f"{stats['fps']}", "#1C83E1")
        # with b:
        #     display_dial("FRAMES", f"{stats['frame_count']}", "#1C83E1")
        # with c:
        #     display_dial("DIMENSION", f"{stats['dim']}", "#1C83E1")

        _, a, _, b, _ = st.columns([1, 2, 1, 1, 1])
        with a:
            dancers = st.number_input("Enter number of dancers:", min_value=1, max_value=6)
        with b:
            if st.button("Start"):
                show_vid.empty()
                process_vid = True

        process_vid = False
        if process_vid:
            stats['dancers'] = dancers
            processing(stats)

if __name__ == '__main__':
    main()
