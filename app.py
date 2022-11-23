import streamlit as st
import cv2 as cv
from PIL import Image
from google.cloud import storage
from google.oauth2 import service_account

st.header("Dance Synchronisation")

## Set up google cloud api
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = storage.Client(credentials=credentials)
bucket = client.bucket("dance-sync-user-upload")

#Receive video file from user upload
uploaded_video = st.file_uploader("**Upload video for evaluation**", ['mp4', 'gif'], key='dance')
frame_count = 0
#If video has been uploaded
if uploaded_video is not None:
    with st.spinner('Processing video...'):
        vid = uploaded_video.name
        with open(vid, mode='wb') as f:
            f.write(uploaded_video.read())

        vidcap = cv.VideoCapture(vid)
        frame_count = int(vidcap.get(cv.CAP_PROP_FRAME_COUNT))

        for frame in range(frame_count):
            #convert cv frame to pillow image
            img = vidcap.read()[1] # get next frame from video
            pil_img = Image.fromarray(img)
            file = f"img_{frame}.jpg"
            pil_img.save(file)
            #Upload to google bucket
            blob = bucket.blob(file)
            blob.upload_from_filename(file)
            #Next frame
            st.write("Uploaded image ", frame)

        #Delete images from bucket
        # for frame in range(frame_count):
        #     blob = bucket.blob(f"img_{frame}.jpg")
        #     blob.delete()

    st.balloons()
