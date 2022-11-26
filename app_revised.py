import streamlit as st
import requests
import math
import pandas as pd
import matplotlib as plt
import seaborn as sns
import numpy as np
# import time
from htbuilder import div, big, h2, styles
from htbuilder.units import rem
from streamlit_lottie import st_lottie
from streamlit_lottie import st_lottie_spinner
# from google.cloud import storage
# from google.oauth2 import service_account

st.set_page_config(layout="wide", page_title="Dance Synchronisation")

#load css
with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# # Set up google cloud
# credentials = service_account.Credentials.from_service_account_info(
#     st.secrets["gcp_service_account"]
# )
# client = storage.Client(credentials=credentials)
# bucket = client.bucket("dance-sync-user-upload")

# Retreive from backend
# def get_file(source_blob, save_as, source_bucket=bucket):
#     # bucket = client.bucket(source_bucket)
#     blob = bucket.blob(source_blob)
#     result = False
#     #Keep trying to fetch blob until it exists
#     start = time.time()
#     while result is False:
#         try:
#             blob.download_to_filename(save_as)
#             result = True
#         except:
#             time.sleep(1)
#             if time.time() - start > 10:
#                 break
#             pass
#     return result

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
        # url = "https://syncv4-eagwezifvq-an.a.run.app/vid_process"
        params = {
            "vid_name": stats['vid_name'],
            "output_name": stats['output_name'],
            "frame_count": stats['frame_count'],
            "fps": stats['fps']
            }
        response = requests.get(url, params=params).json()
        
        # #Retreive database
        # if get_file(source_blob='data.csv', save_as='data.csv'):
        #     df = pd.read_csv('data.csv')
        # else:
        #     st.error("Dataframe request timeout")
        # # try:
        # #     url = "https://syncv3-eagwezifvq-an.a.run.app/vid_processed"
        # #     data = requests.get(url)
        # #     df = pd.json_normalize(data, record_path =['data'])
        # # except:
        # #     st.error("Database retrieval failed")
        # #Retrieve video
        # if not get_file(source_blob='video.mp4', save_as='video.mp4'):
        #     st.error("Video request timeout")

    #Create df
    d = {
        'Time': response['timestamps'],
        'Sync': response['scores']
    }
    df = pd.DataFrame(d)
    
    #Plot results
    df['Sync'] = df['Sync'] - 0.5
    st.line_chart(data=df, x='Time', y='Sync')

    #Load processed video
    video_url = response['output_url']
    st.video(video_url)
    # video_file = open('video.mp4', 'rb')
    # video_bytes = video_file.read()
    # st.video(video_bytes)

    #Timestamp buttons
    sorted_df = df.sort_values(by=['Sync']).round(2).head(5)
    timestamps = sorted_df['Time'].to_list()
    sync = sorted_df['Sync'].to_list()

    with st.expander("**Your top five areas for improvement:**"):
        # ## button method for displaying top 5 improvement areas
        # # bool, moment, description
        # button_col, video_col = st.columns(2)
        # with button_col:
        #     buttons = [
        #         (st.button("A", "a"), timestamps[0], st.write(f'Time: {timestamps[0]}s, Sync: {sync[0]}')),
        #         (st.button("B", "b"), timestamps[1], st.write(f'Time: {timestamps[1]}s, Sync: {sync[1]}')),
        #         (st.button("C", "c"), timestamps[2], st.write(f'Time: {timestamps[2]}s, Sync: {sync[2]}')),
        #         (st.button("D", "d"), timestamps[3], st.write(f'Time: {timestamps[3]}s, Sync: {sync[3]}')),
        #         (st.button("E", "e"), timestamps[4], st.write(f'Time: {timestamps[4]}s, Sync: {sync[4]}'))
        #     ]
        # #empty placeholder to reload widget when different button is pressed
        # with video_col:
        #     placeholder = st.empty()
        #     time_chosen = [v for k, v, t in buttons if k == True]  # return time associated with a clicked button
        #     if time_chosen:
        #         placeholder.empty()
        #         placeholder.video(video_url, start_time=math.floor(time_chosen[0]))
        
        # radio method for displaying top 5 improvement areas
        choice1 = f'Time: {timestamps[0]}s, Sync: {sync[0]}'
        choice2 = f'Time: {timestamps[1]}s, Sync: {sync[1]}'
        choice3 = f'Time: {timestamps[2]}s, Sync: {sync[2]}'
        choice4 = f'Time: {timestamps[3]}s, Sync: {sync[3]}'
        choice5 = f'Time: {timestamps[4]}s, Sync: {sync[4]}'
        
        radio = st.radio('**Select a timestamp**', (choice1, choice2, choice3, choice4, choice5,))
        
        if radio == choice1:
            st.video(video_url, start_time=math.floor(timestamps[0]))
        elif radio == choice2:
            st.video(video_url, start_time=math.floor(timestamps[1]))
        elif radio == choice2:
            st.video(video_url, start_time=math.floor(timestamps[2]))
        elif radio == choice2:
            st.video(video_url, start_time=math.floor(timestamps[3]))
        else:
            st.video(video_url, start_time=math.floor(timestamps[4]))
        
            
    with st.expander("**Model info:**"):
    # df = pd.DataFrame(
    #     np.random.randn(50, 20),
    #     columns=('col %d' % i for i in range(20)))
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
            # url = "https://syncv3-eagwezifvq-an.a.run.app/vid_stats"
            url = "http://127.0.0.1:8000/vid_stats"
            files = {"file": (uploaded_video.name, uploaded_video, "multipart/form-data")}
            stats = requests.post(url, files=files).json()

        _, b, _ = st.columns([1,4,1])
        with b:
            show_vid = st.video(uploaded_video)

        process_vid = False
        a, b, c, _, d = st.columns(5)
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