from pathlib import Path
#Imports for streamlit
import streamlit as st
import av
import cv2
from streamlit_webrtc import (
    RTCConfiguration,
    VideoProcessorBase,
    WebRtcMode,
    webrtc_streamer,
)
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.app_logo import add_logo

#Imports for ml model
import numpy as np
import mediapipe as mp
from keras.models import load_model


st.set_page_config(
    page_title="MoodGroove",
    page_icon="🎵",
)

page_bg_img = """
<style>

div.stButton > button:first-child {
    all: unset;
    width: 100px;
    height: 40px;
    font-size: 60px;
    font-weight: 800;
    font-family: sans-serif;
    background: transparent;
    border: none;
    position: relative;
    color: white;
    cursor: pointer;
    z-index: 1;
    padding: 10px 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    white-space: nowrap;
    user-select: none;
    -webkit-user-select: none;
    touch-action: manipulation;

}
div.stButton > button:before, div.stButton > button:after {
    content: '';
    position: absolute;
    bottom: 0;
    right: 0;
    z-index: -99999;
    transition: all .4s;
}

div.stButton > button:before {
    transform: translate(0%, 0%);
    width: 100%;
    height: 100%;
    background:#FF2400;
    border-radius: 10px;
}
div.stButton > button:after {
  transform: translate(10px, 10px);
  width: 10px;
  height: 10px;
  background: transparent;
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  border-radius: 100px;
}

div.stButton > button:hover::before {
    transform: translate(5%, 20%);
    width: 110%;
    height: 110%;
}


div.stButton > button:hover::after {
    border-radius: 10px;
    transform: translate(0, 0);
    width: 100%;
    height: 100%;
}

div.stButton > button:active::after {
    transition: 0s;
    transform: translate(0, 5%);
}



[data-testid="stAppViewContainer"] {
background-image: url("https://wallpapercave.com/wp/wp2130046.jpg");
background-position: top left;
background-repeat: no-repeat;
background-attachment: local;
}

[data-testid="stSidebar"] > div:first-child {
background-position: center; 
background-repeat: no-repeat;
background-attachment: fixed;
background : black;
}

[data-testid="stHeader"] {
background: rgba(0,0,0,0);
}

[data-testid="stToolbar"] {
right: 2rem;
}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)
st.title("MoodGroove 🎧")
st.sidebar.success("Select a page below.")
st.sidebar.text("Developed by Harsh & Aditya")

st.markdown("**Hey there, emotion explorer! Are you ready for a wild ride through the rollercoaster of feelings?** 🎢🎵")
st.markdown("**Welcome to MoodGroove, where our AI dives headfirst into your emotional world! Using your webcam, we analyze your vibes and cook up the perfect playlist just for you. ** 🎶")
st.markdown("**Think of us as your personal mood-based DJ! Whether you're feeling like a happy-go-lucky panda or riding the moody blues, MoodGroove has your back. Our AI detects your vibes and serves up tunes that match your moment.** 🐼🎉")
st.markdown("**So, get ready for a whirlwind of emotions and music. MoodGroove turns your webcam into a mood ring, your screen into a dance floor, and your heart into a DJ booth. Strap in 🚀 , hit that webcam 📷 , and let the musical journey begin!** 🎢🎵")

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{
        "urls": ["stun:stun.l.google.com:19302"]
    }]})

# CWD path
HERE = Path(__file__).parent

model = load_model("model.h5")
label = np.load("label.npy")

holistic = mp.solutions.holistic
hands = mp.solutions.hands
holis = holistic.Holistic()
drawing = mp.solutions.drawing_utils

if "run" not in st.session_state:
    st.session_state["run"] = ""

run = np.load("emotion.npy")[0]

try:
    emotion = np.load("emotion.npy")[0]
except:
    emotion = ""

    
class EmotionProcessor(VideoProcessorBase):
    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        frm = frame.to_ndarray(format="bgr24")
        frm = cv2.flip(frm, 1)  
        res = holis.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))
        
        lst = []
        if res.face_landmarks:
            for i in res.face_landmarks.landmark:
                lst.append(i.x - res.face_landmarks.landmark[1].x)
                lst.append(i.y - res.face_landmarks.landmark[1].y)
        
            if res.left_hand_landmarks:
                for i in res.left_hand_landmarks.landmark:
                    lst.append(i.x - res.left_hand_landmarks.landmark[8].x)
                    lst.append(i.y - res.left_hand_landmarks.landmark[8].y)
            else:
                for i in range(42):
                    lst.append(0.0)
        
            if res.right_hand_landmarks:
                for i in res.right_hand_landmarks.landmark:
                    lst.append(i.x - res.right_hand_landmarks.landmark[8].x)
                    lst.append(i.y - res.right_hand_landmarks.landmark[8].y)
            else:
                for i in range(42):
                    lst.append(0.0)
        
            lst = np.array(lst).reshape(1, -1)
        
            pred = label[np.argmax(model.predict(lst))]
            print(pred)
            cv2.putText(frm, pred, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            
            np.save("emotion.npy",np.array([pred]))
            
            emotion = pred
       
        drawing.draw_landmarks(frm, res.face_landmarks, holistic.FACEMESH_CONTOURS)
        drawing.draw_landmarks(frm, res.left_hand_landmarks, hands.HAND_CONNECTIONS) 
        drawing.draw_landmarks(frm, res.right_hand_landmarks, hands.HAND_CONNECTIONS)
    
        return av.VideoFrame.from_ndarray(frm, format="bgr24")
    


webrtc_streamer(key="key", desired_playing_state=st.session_state.get("run", "") == "true" ,mode=WebRtcMode.SENDRECV,  rtc_configuration=RTC_CONFIGURATION, video_processor_factory=EmotionProcessor, media_stream_constraints={
        "video": True,
        "audio": False
    },
    async_processing=True)


col1, col2, col6 = st.columns([1, 1, 1])

with col1:
    start_btn = st.button("Start")
with col6:
    stop_btn = st.button("Stop")

if start_btn:
    st.session_state["run"] = "true"
    st.experimental_rerun()

if stop_btn:
    st.session_state["run"] = "false"
    st.experimental_rerun()
else:
    if not emotion:
        pass
    else:
        np.save("emotion.npy", np.array([""]))
        st.session_state["emotion"] = run
        st.success("Your current emotion is: " + emotion)
        st.subheader("Choose your streaming service")

col3, col4, col5 = st.columns(3)

with col4:
    btn = st.button("Spotify")
    if btn:
        switch_page("Spotify")

with col5:
    btn2 = st.button("Youtube")
    if btn2:
        switch_page("Youtube")

with col3:
    btn3 = st.button("Soundcloud")
    if btn3:
        switch_page("Soundcloud")