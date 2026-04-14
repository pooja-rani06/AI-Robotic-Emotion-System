import os
import random
import time
import pygame  # Used for playing audio

#  Step 1: Initialize the mixer for playing music
pygame.mixer.init()
#  Step 2: Define the main folder containing all song folders
# 🔹 Replace this path with the folder on your system
MAIN_FOLDER = r"songs"
#  Step 3: Define subfolder paths for each mood
FOLDERS = {
    "happy": os.path.join(MAIN_FOLDER, "happy_songs"),
    "sad": os.path.join(MAIN_FOLDER, "sad_songs"),
    "neutral": os.path.join(MAIN_FOLDER, "neutral_songs")
}
#  Step 4: Ask the user for mood input
mood = input("Enter your mood (happy / sad / neutral): ").strip().lower()
#  Step 5: Validate input and get the corresponding folder
if mood not in FOLDERS:
    print("❌ Invalid mood! Please choose from: happy, sad, or neutral.")
else:
    folder_path = FOLDERS[mood]
    #  Step 6: Get all available songs (.mp3 or .wav) in the folder
    songs = [f for f in os.listdir(folder_path) if f.endswith(('.mp3', '.wav'))]
    if not songs:
        print(f"⚠️ No songs found in folder: {folder_path}")
    else:
        #  Step 7: Pick a random song from the selected mood folder
        song = random.choice(songs)
        song_path = os.path.join(folder_path, song)
        #  Step 8: Play the song for 20 seconds
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        # Wait 20 seconds while the song plays
        time.sleep(20)
        #  Step 9: Stop the song after 20 seconds
        pygame.mixer.music.stop()
        print("⏹️  Music stopped after 20 seconds.")
