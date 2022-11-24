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


def main():

    st.set_page_config(page_title="Dance Synchronisation")
    st.header("Dance Synchronisation")

    #Receive video file from user upload
    uploaded_video = st.file_uploader("**Upload video for evaluation**", ['mp4', 'gif'], key='dance')
    # frame_count = 0
    #If video has been uploaded
    if uploaded_video is not None:

        with st.spinner('Contacting api...'):
            url = "https://syncv2-eagwezifvq-an.a.run.app/vid_process_from_st"
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
            if not get_file(source_blob='video.gif', save_as='video.gif'):
                st.error("Video request timeout")
        st.balloons()

        #Plot results
        st.line_chart(df)

        #Display video
        video_file = open('video.gif', 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes)

if __name__ == '__main__':
	main()
