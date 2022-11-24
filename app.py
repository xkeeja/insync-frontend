import streamlit as st
import requests
import pandas as pd
import matplotlib as plt
import seaborn as sns
import numpy as np
import time
from google.cloud import storage
from google.oauth2 import service_account

# Set up google cloud
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = storage.Client(credentials=credentials)
bucket = client.bucket("dance-sync-user-upload")

# Retreive from backend
def get_file(source_blob, save_as, source_bucket=''):
    bucket = client.bucket(source_bucket)
    blob = bucket.blob(source_blob)
    result = None
    #Keep trying to fetch blob until it exists
    while result is None:
        try:
            result = blob.download_to_filename(save_as)
        except:
            time.sleep(1)
            pass
    return result


def main():

    st.header("Dance Synchronisation")

    #Receive video file from user upload
    uploaded_video = st.file_uploader("**Upload video for evaluation**", ['mp4', 'gif'], key='dance')
    # frame_count = 0
    #If video has been uploaded
    if uploaded_video is not None:

        url = "http://127.0.0.1:8000/vid_process_from_st"
        files = {"file": (uploaded_video.name, uploaded_video, "multipart/form-data")}
        response = requests.post(url, files=files).json()

        # with st.spinner('Uploading to cloud...'):
        #     #save binary to tempfile then post
        #     with open("video.gif", "wb") as f:
        #         f.write(uploaded_video.getbuffer())
        #     blob = bucket.blob('video.gif')
        #     blob.upload_from_filename('video.gif')
        # st.success(f"Uploaded video to {bucket} as 'video.gif'")

        # #Send video upload confirmation to api
        # API_ENDPOINT = "http://127.0.0.1:8000/vid_process_from_st"
        # API_KEY = ""
        # api_data = {'api_key':API_KEY, 'upload': True}
        # requests.post(url = API_ENDPOINT, data = api_data)

        with st.spinner('Analysing dance moves...'):
            #Retreive database
            df = pd.read_csv(get_file(source_blob='', save_as='data.csv'))
            #Retrieve video
            video = get_file(source_blob='', save_as='video.mp4')
        st.balloons()

        #Plot results
        st.line_chart(data=df, x=df['time'], y=df['sync'])

        #Display video
        video_file = open('video.mp4', 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes)

if __name__ == '__main__':
	main()
