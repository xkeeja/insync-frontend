import streamlit as st
import requests
import pandas as pd
import matplotlib as plt
import seaborn as sns
import numpy as np
import time
from streamlit_lottie import st_lottie
from streamlit_lottie import st_lottie_spinner
from google.cloud import storage
from google.oauth2 import service_account

# Set up google cloud
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = storage.Client(credentials=credentials)
bucket = client.bucket("dance-sync-user-upload")

# Retreive from backend
def get_file(source_blob, save_as, source_bucket=bucket):
    # bucket = client.bucket(source_bucket)
    blob = bucket.blob(source_blob)
    result = False
    #Keep trying to fetch blob until it exists
    start = time.time()
    while result is False:
        try:
            blob.download_to_filename(save_as)
            result = True
        except:
            time.sleep(1)
            if time.time() - start > 10:
                break
            pass
    return result

#animations
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def main():

    st.set_page_config(layout="wide", page_title="Dance Synchronisation")

    #load animations
    lottie_url_dancing = "https://assets7.lottiefiles.com/packages/lf20_owg7kezi.json"
    lottie_dancing = load_lottieurl(lottie_url_dancing)

    #build header
    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        st_lottie(lottie_dancing, key="dance_left")
    with col2:
        st.markdown("<h1 style='text-align: center; color: yellow;'>Dance Synchronisation</h1>", unsafe_allow_html=True)
    with col3:
        st_lottie(lottie_dancing, key="dance_right")


    #Receive video file from user upload
    uploaded_video = st.file_uploader("**Upload video for evaluation**", ['mp4', 'gif'], key='dance')
    # frame_count = 0
    #If video has been uploaded
    if uploaded_video is not None:

        with st.spinner('Contacting api...'):
            url = "https://syncv3-eagwezifvq-an.a.run.app/vid_process_from_st"
            files = {"file": (uploaded_video.name, uploaded_video, "multipart/form-data")}
            response = requests.post(url, files=files).json()
        st.write(response)

        with st.spinner('Analysing dance moves...'):
            #Retreive database
            if get_file(source_blob='data.csv', save_as='data.csv'):
                df = pd.read_csv('data.csv')
            else:
                st.error("Dataframe request timeout")
            #Retrieve video
            if not get_file(source_blob='video.mp4', save_as='video.mp4'):
                st.error("Video request timeout")

        #Plot results
        df['Sync'] = df['Sync'] - 0.5
        st.area_chart(data=df, x='Time', y='Sync', )

        #Timestamp buttons
        sorted_df = df.sort_values(by=['Sync']).round(2).head(5)
        timestamps = sorted_df['Time'].to_list()
        sync = sorted_df['Sync'].to_list()
        # button1, button2, button3, button4, button5 = st.columns(5)
        # with button1:
        #     if st.button('1'):
        st.write("**Your top five miss-steps:**")
        # bool, moment, description
        button_col, video_col = st.columns(2)
        with button_col:
            buttons = [
                (st.button("A", "a"), timestamps[0], st.write(f'Time: {timestamps[0]}s, Sync: {sync[0]}')),
                (st.button("B", "b"), timestamps[1], st.write(f'Time: {timestamps[1]}s, Sync: {sync[1]}')),
                (st.button("C", "c"), timestamps[2], st.write(f'Time: {timestamps[2]}s, Sync: {sync[2]}')),
                (st.button("D", "d"), timestamps[3], st.write(f'Time: {timestamps[3]}s, Sync: {sync[3]}')),
                (st.button("E", "e"), timestamps[4], st.write(f'Time: {timestamps[4]}s, Sync: {sync[4]}'))
            ]
        #load video data
        video_file = open('video.mp4', 'rb')
        video_bytes = video_file.read()
        #empty placeholder to reload widget when different button is pressed
        with video_col:
            placeholder = st.empty()
            time_chosen = [v for k, v, t in buttons if k == True]  # return time associated with a clicked button
            if time_chosen:
                placeholder.empty()
                placeholder.video(video_bytes, start_time=time_chosen[0])

if __name__ == '__main__':
	main()
