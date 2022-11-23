import streamlit as st
import cv2 as cv
import tempfile
from google.cloud import storage
from google.oauth2 import service_account

st.header("Dance Synchronisation")

## Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = storage.Client(credentials=credentials)

#Receive video file from user upload
uploaded_video = st.file_uploader("**Upload video for evaluation**", ['mp4', 'gif'], key='dance')
if uploaded_video is not None:
    #Convert from bytesio to cv
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_video.read())
    vf = cv.VideoCapture(tfile.name)
    #Upload to google bucket
    bucket = client.bucket("dance-sync-user-upload")
    blob = bucket.blob("user_upload")
    blob.upload_from_filename(vf)
