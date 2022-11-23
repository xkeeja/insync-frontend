import streamlit as st
import cv2 as cv
import tempfile
from google.cloud import storage

st.header("Dance Synchronisation")

#Receive video file from user upload
uploaded_video = st.file_uploader("**Upload video for evaluation**", ['mp4', 'gif'], key='dance')
if uploaded_video is not None:
    #Convert from bytesio to cv
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_video.read())
    vf = cv.VideoCapture(tfile.name)
    #Upload to google bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket("dance-sync-user-upload")
    blob = bucket.blob("user_upload")
    blob.upload_from_filename(vf)
