# 💃💃 in sync
_Your personal AI synchronization assistant._


Is there an objective way to **mathematically quantify** synchronization in dance?


https://user-images.githubusercontent.com/113004083/206090266-18d06a24-b054-4d29-b75a-efcd41fc5f8d.mp4


_Dance video used in demonstration sourced from [Urban Dance Camp YouTube channel](https://youtu.be/9hUZyswpp2w)._

## Streamlit Interface
### Video Upload
![Screenshot 2022-12-06 at 17 51 13](https://user-images.githubusercontent.com/113004083/206093112-54257082-c7f0-4019-9357-36c29520c0ea.png)

### Annotated Output
![Screenshot 2022-12-06 at 17 54 19](https://user-images.githubusercontent.com/113004083/206092598-ad12a1bc-9a06-493b-94ad-9d934b265986.png)

### Synchronization Error
![Screenshot 2022-12-06 at 17 55 15](https://user-images.githubusercontent.com/113004083/206092228-29ef6d8a-a757-45ce-a1f0-a33d518616dc.png)

### Link with Highest Error
![Screenshot 2022-12-06 at 17 56 11](https://user-images.githubusercontent.com/113004083/206092385-c5743711-9659-41d5-bf08-0372cb1f544e.png)

### Frame-by-frame
![Screenshot 2022-12-06 at 17 55 38](https://user-images.githubusercontent.com/113004083/206093265-3b450efc-86b0-48cc-b1dd-00e3ebbf71bb.png)

## Application Backend
API scripts at https://github.com/xkeeja/insync-backend.

## Getting Started
### Setup

Navigate to the base level of the repository
```
cd {your/path/here}/insync-frontend
```

Install requirements
```
pip install -U pip
pip install -r requirements.txt
```

### Local Streamlit
```
make run_streamlit
```

### Set API link
Local (default port) -- FastAPI functions named in [insync-backend](https://github.com/xkeeja/insync-backend)
```
url = "http://127.0.0.1:8000/vid_stats"
url = "http://127.0.0.1:8000/vid_process"
```
Server
```
url = "{your_url_here}/vid_stats"
url = "{your_url_here}/vid_process"
```

### Streamlit Deployment
Main file path = `app.py`

## Built With
- [Python](https://www.python.org/) - Frontend & Backend
- [Streamlit](https://streamlit.io/) - Frontend Deployment
- [GCP](https://cloud.google.com/) - Storage & Backend Deployment
- [TensorFlow](https://tfhub.dev/google/movenet/multipose/lightning/1) - Pose Detection Model
- CSS - Frontend Styling

## Acknowledgements
Inspired by [Kanami](https://www.linkedin.com/in/kanami-oyama-9a666b243/)'s love of dance.

## Team Members
- Kanami Oyama ([GitHub](https://github.com/kanpinpon)) ([LinkedIn](https://www.linkedin.com/in/kanami-oyama-9a666b243/))
- Jaylon Saville ([GitHub](https://github.com/jaysaville)) ([LinkedIn](https://www.linkedin.com/in/jaysaville/))
- Vincent-Victor Rodriguez--Le Roy ([GitHub](https://github.com/Slokem)) ([LinkedIn](https://www.linkedin.com/in/vincent-victor-r-328aa5a8/))

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License
