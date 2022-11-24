import streamlit as st
import cv2 as cv
from PIL import Image
import requests
from google.cloud import storage
from google.oauth2 import service_account

## Set up google cloud api
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = storage.Client(credentials=credentials)
bucket = client.bucket("dance-sync-user-upload")

# def post_video(binary):
#     with open(binary, mode='wb') as f:
#             f.write(uploaded_video.read())
#     with open(vid, 'rb') as f:
#         r = requests.post('http://httpbin.org/post', files={vid: f})

def fetch_results(file):
	base_url = "http://myapi:8000/api/dance?".format(file)
	resp = requests.get(base_url)
	return resp.json()

def main():

    st.header("Dance Synchronisation")

    #Receive video file from user upload
    uploaded_video = st.file_uploader("**Upload video for evaluation**", ['mp4', 'gif'], key='dance')
    frame_count = 0
    #If video has been uploaded
    if uploaded_video is not None:
        # vid = uploaded_video.name
        # with open(vid, mode='wb') as f:
        #     f.write(uploaded_video.read())
        # with open(vid, 'rb') as f:
        #     r = requests.post('http://httpbin.org/post', files={vid: f})
        bytes_data = uploaded_video.getvalue()
        st.write(bytes_data)

        # vidcap = cv.VideoCapture(vid)
        # frame_count = int(vidcap.get(cv.CAP_PROP_FRAME_COUNT))

        # for frame in range(frame_count):
        #     #convert cv frame to pillow image
        #     img = vidcap.read()[1] # get next frame from video
        #     pil_img = Image.fromarray(img)
        #     file = f"img_{frame}.jpg"
        #     pil_img.save(file)
        #     #Upload to google bucket
        #     blob = bucket.blob(file)
        #     blob.upload_from_filename(file)
        #     #Next frame
        #     st.write("Uploaded image ", frame)

        #Delete images from bucket
        # for frame in range(frame_count):
        #     blob = bucket.blob(f"img_{frame}.jpg")
        #     blob.delete()

        st.balloons()

if __name__ == '__main__':
	main()
