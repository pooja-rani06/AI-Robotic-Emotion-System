import cv2
import numpy as np
from collections import deque
import mediapipe as mp
from hsemotion_onnx.facial_emotions import HSEmotionRecognizer
import matplotlib.pyplot as plt
import time
import os
import random
from pygame import mixer
import speech_recognition as sr
import pyttsx3
# --- Secure API Key Imports ---
from dotenv import load_dotenv 
# --- Gemini API Imports ---
from google import genai
from google.genai import types 

# ---------------- Initialization ---------------- #
MODEL_NAME = 'enet_b2_8'
fer = HSEmotionRecognizer(model_name=MODEL_NAME)
mp_fd = mp.solutions.face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.6)

# ---------------- Voice Setup ---------------- #
recognizer = sr.Recognizer()
# Note: pyttsx3 engine is initialized inside speak() for stability
# engine = pyttsx3.init() # Commented out

# ---------------- Gemini AI Setup ---------------- #
load_dotenv() # Load variables from the .env file
GEMINI_API_KEY = os.getenv("your gemini key") # Get the key securely from the environment

client = None
chat = None
SYSTEM_PROMPT = "You are an interactive, emotional AI assistant. Speak naturally, like Gemini AI."

try:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not found. Check your .env file.")
        
    # 1. Connect the API Key by passing the retrieved environment variable
    client = genai.Client(api_key=GEMINI_API_KEY) 
    
    # 2. Initialize a chat session for conversation memory and system instruction
    chat = client.chats.create(
        model="gemini-2.5-flash", 
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
    )
    print("Gemini Chat Session Initialized.")
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    if client is None:
        print("FATAL: Gemini features will be disabled. Ensure your API key is valid and check your network connection.")


# ---------------- Emotion Settings ---------------- #
CLASSES = ['Happiness', 'Neutral', 'Sadness']
SMOOTH_N = 8
prob_buf = deque(maxlen=SMOOTH_N)

# ---------------- Song Folders ---------------- #
# >>>>>>>>>>>>>> ACTION REQUIRED: PASTE YOUR ABSOLUTE PATH HERE <<<<<<<<<<<<<<
# REPLACE THE PATH BELOW with the EXACT location of your SONGS DC folder!
BASE_SONG_PATH = r"songs"
# Example if it was in the root of C: BASE_SONG_PATH = r"C:\SONGS DC"
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

SONG_FOLDERS = {
    "Happiness": os.path.join(BASE_SONG_PATH, "happy_songs"),
    "Sadness": os.path.join(BASE_SONG_PATH, "sad_songs"),
    "Neutral": os.path.join(BASE_SONG_PATH, "neutral_songs")
}

mixer.init()

# ---------------- Helper Functions ---------------- #
def speak(text):
    """Voice output with expressive style (Text AND Voice, with stability fixes)"""
    print(f"AI 🧠: {text}") # Keep text output as requested
    
    # Re-initialize the engine locally for stability (common pyttsx3 fix)
    try:
        local_engine = pyttsx3.init()
        
        # Set to the most stable voice (often index 0)
        voices = local_engine.getProperty('voices')
        if voices:
            local_engine.setProperty('voice', voices[0].id)
        
        local_engine.setProperty('rate', 165)
        local_engine.say(text)
        local_engine.runAndWait() 
    except Exception as e:
        print(f"FATAL Speech Error: pyttsx3 failed to speak. Error: {e}")
        print("Check Windows audio drivers and SAPI5 settings.")


def listen_command(timeout=5, phrase_limit=10):
    with sr.Microphone() as source:
        print("🎙 Listening...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            text = recognizer.recognize_google(audio)
            print("🗣 You said:", text)
            return text.lower()
        except:
            return None

def ask_gemini(prompt):
    """Real AI response from Gemini with session memory"""
    if chat is None:
        return "I am unable to connect to my brain. Please check the Gemini API setup."
    try:
        # The send_message method automatically handles history and the system instruction
        response = chat.send_message(prompt)
        reply = response.text
        return reply
    except Exception as e:
        print("Gemini AI error:", e)
        return "Oops! I am having trouble connecting to my Gemini brain."

def play_emotion_song(emotion):
    """Plays a song based on emotion for 20 seconds or until user interrupts."""
    folder = SONG_FOLDERS.get(emotion, SONG_FOLDERS["Neutral"])
    
    if not os.path.exists(folder):
        speak(f"I cannot find the songs folder for {emotion} at the path: {folder}. Please check the path and music files.")
        return
        
    songs = [os.path.join(folder, s) for s in os.listdir(folder)
             if s.lower().endswith(('.mp3', '.wav', '.ogg'))]
             
    if not songs:
        speak(f"The {emotion} song folder is empty. Please add some music files.")
        return
        
    song = random.choice(songs)
    song_name = os.path.basename(song)
    
    print(f"🎶 Playing: {song_name}")
    speak(f"I detected a {emotion} mood! Let’s enjoy {song_name} for 20 seconds.") 
    
    try:
        mixer.music.load(song)
        mixer.music.play()
        
        start_time = time.time()
        while time.time() - start_time < 20:  # <-- Stop after 20 seconds
            # Optional: Check for interrupt commands
            interrupt_text = listen_command(timeout=1.0, phrase_limit=5.0)
            if interrupt_text and ("next" in interrupt_text or "stop music" in interrupt_text):
                mixer.music.stop()
                print("🎶 Music stopped by user command.")
                speak("Okay, stopping the music early.")
                return
            time.sleep(0.1)
        
        mixer.music.stop()  # Stop after 20 seconds automatically
        print(f"🎶 Song stopped after 20 seconds: {song_name}")
        speak("That was 20 seconds of your song! I hope you enjoyed it.")
        
    except Exception as e:
        print(f"Music error: {e}")
        speak("I couldn’t play the song. Check if the file is a valid MP3/WAV format.")

# ---------------- Emotion Detection ---------------- #
def capture_emotion_and_play():
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        speak("Error: Could not open camera. Please check your webcam connection.")
        return
        
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    plt.ion()
    fig, ax = plt.subplots()
    bars = ax.bar(CLASSES, [0]*len(CLASSES), color='skyblue')
    ax.set_ylim(0,1)
    ax.set_ylabel("Probability")
    ax.set_title("Detected Emotion Probabilities")

    last_emotion = None
    emotion_start = None

    speak("Starting emotion capture. Look at the camera, I’m watching your expressions!")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = mp_fd.process(rgb)
        h, w = frame.shape[:2]

        if results.detections:
            faces = []
            for det in results.detections:
                bbox = det.location_data.relative_bounding_box
                x1 = max(int(bbox.xmin * w), 0)
                y1 = max(int(bbox.ymin * h), 0)
                x2 = min(int((bbox.xmin + bbox.width) * w), w-1)
                y2 = min(int((bbox.ymin + bbox.height) * h), h-1)
                cx = (x1+x2)//2
                faces.append((abs(cx - w//2), x1, y1, x2, y2))

            faces.sort(key=lambda f: f[0])
            _, x1, y1, x2, y2 = faces[0]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)

            face_crop = frame[y1:y2, x1:x2]
            if face_crop.size != 0:
                _, probs = fer.predict_emotions(face_crop, logits=False)
                if len(probs) >= 7:
                    happy, neutral, sad = probs[4], probs[5], probs[6]
                    avg = np.array([happy, neutral, sad])
                    prob_buf.append(avg)
                    smooth = np.mean(prob_buf, axis=0)
                else:
                    smooth = np.array([0.0, 0.0, 0.0]) 

                for bar, val in zip(bars, smooth):
                    bar.set_height(val)
                fig.canvas.draw()
                fig.canvas.flush_events()

                if np.sum(smooth) > 0.1:
                    cls_id = int(np.argmax(smooth))
                    emotion = CLASSES[cls_id]
                    label = f"{emotion} ({smooth[cls_id]*100:.1f}%)"
                    cv2.putText(frame, label, (x1, max(25, y1-10)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

                    if emotion != last_emotion:
                        last_emotion = emotion
                        emotion_start = time.time()
                    elif time.time() - emotion_start > 4:
                        speak(f"I sense you’re feeling {emotion}. Let’s enjoy a song together!")
                        play_emotion_song(emotion)
                        break
                else:
                    last_emotion = None
                    emotion_start = None

        cv2.imshow("Emotion Capture", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # --- CLEANUP (FIX FOR TKINTER ERROR) ---
    cap.release()
    cv2.destroyAllWindows()
    
    # Add a small delay and explicitly close the figure to prevent the Tkinter crash
    time.sleep(0.1) 
    plt.close(fig) 

# ---------------- Main Loop ---------------- #
if client:
    speak("Hello! I’m your AI assistant. We can chat endlessly. Say 'capture my emotion' whenever you want me to play songs based on your mood!")
else:
    speak("Hello! The AI chat features are currently disabled due to an API key error, but you can still say 'capture my emotion' for music!")

while True:
    text = listen_command()
    if not text:
        continue

    if "capture my emotion" in text or "play songs" in text:
        capture_emotion_and_play()
        break
    elif "stop" in text or "bye" in text:
        speak("Goodbye! I enjoyed talking with you. See you soon!")
        break
    else:
        # Use the ask_gemini function which handles the conversation
        reply = ask_gemini(text)
        speak(reply) 

mixer.quit()