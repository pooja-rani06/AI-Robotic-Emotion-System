# ---------------------- Import all needed libraries ----------------------
import speech_recognition as sr      # to listen to what we say (speech to text)
import pyttsx3                       # to make the bot talk (text to speech)
from datetime import datetime        # to tell time when asked
import google.generativeai as genai  # to connect with Gemini AI model

# ---------------------- Connect Gemini API ----------------------
# Here we connect to Gemini using our API key
genai.configure(api_key="your api key")

# We choose the Gemini model we want to use (this one is fast)
model = genai.GenerativeModel("gemini-2.5-flash")

# ---------------------- Create speech recognizer ----------------------
# This helps our program understand the user’s voice
r = sr.Recognizer()

# ---------------------- Function to make bot talk ----------------------
def speak(text):
    """
    This function will take some text and speak it out loud.
    """
    print(f"Bot: {text}")   # print text on screen also
    
    # Create a voice engine
    engine = pyttsx3.init('sapi5')   # 'sapi5' works well on Windows
    
    # Get voices from system
    voices = engine.getProperty('voices')
    
    # Choose a female voice (index 1)
    engine.setProperty('voice', voices[0].id)
    
    # Set speaking speed
    engine.setProperty('rate', 175)
    
    # Make the bot say the text
    engine.say(text)
    
    # Actually play the sound
    engine.runAndWait()
    
    # Stop the engine after speaking
    engine.stop()

# ---------------------- Function to listen to our voice ----------------------
def listen():
    """
    This function will listen to what we say and convert it to text.
    """
    with sr.Microphone() as source:
        print("\nListening...")
        speak("listening")
        
        # Adjust mic for background noise
        r.adjust_for_ambient_noise(source, duration=1)
        
        # Record our voice
        audio = r.listen(source)
        
        try:
            # Convert speech to text using Google’s recognizer
            text = r.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()
        
        except sr.UnknownValueError:
            # If it doesn’t understand our speech
            speak("Sorry, I didn't catch that.")
            return ""
        
        except sr.RequestError:
            # If internet or Google’s API is not working
            speak("Network error. Please check your internet connection.")
            return ""

# ---------------------- Main function that controls everything ----------------------
def main():
    """
    This is where the full program runs.
    The bot will keep listening and replying until we say 'stop' or 'bye'.
    """
    speak("Hello! I am your voice assistant. How can I help you today?")
    
    while True:
        # Listen to what user says
        query = listen()

        # If nothing was said, just keep listening
        if not query:
            continue
        
        speak("responding")

        # Some basic commands
        if "hello" in query:
            speak("Hi there! How are you?")
        
        elif "time" in query:
            now = datetime.now().strftime("%H:%M:%S")
            speak(f"The current time is {now}")
        
        elif "your name" in query:
            speak("I am your personal AI voice assistant.")
        
        # To stop the program
        elif "stop" in query or "bye" in query:
            speak("Goodbye! Have a great day.")
            break
        
        # For any other question, ask Gemini AI
        else:
            response = model.generate_content(query)
            speak(response.text)

# ---------------------- Start the program ----------------------
if __name__ == "__main__":
    main()
