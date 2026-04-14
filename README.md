# AI-Based Interactive Emotion-Aware System

## 🚀 Overview
This project presents a multimodal AI system capable of detecting human emotions in real time and responding through voice interaction and emotion-aware responses such as music playback.

The system integrates computer vision, machine learning, and conversational AI into a unified perception-to-action pipeline, with ongoing extensions towards robotic actuation.

The system has been tested for real-time emotion detection and interaction using webcam-based input.

---

## 🧠 Key Features
- Real-time face detection using MediaPipe  
- Emotion recognition using DeepFace and ONNX-based models  
- Voice interaction using SpeechRecognition and pyttsx3  
- Context-aware conversational responses using Gemini AI  
- Emotion-driven music recommendation system  
- Continuous perception-to-decision pipeline  

---

## 🔄 System Architecture

```
Camera Input → Face Detection → Emotion Recognition  
→ Decision Logic → Voice Response / Music Playback  

→ (Future Extension: Robotic Actuation)
```

---

## 🛠️ Tech Stack
- Programming: Python  
- Computer Vision: OpenCV, MediaPipe  
- Emotion Recognition: DeepFace, HSEmotion (ONNX)  
- AI/LLM: Gemini API  
- Speech Processing: SpeechRecognition, pyttsx3  
- Audio: Pygame  

---

## 📁 Project Structure

```
AI-Robotic-Emotion-System/
│── main.py
│── interaction.py
│── emotion.py
│── facecapture.py
│── README.md
```

---

## ▶️ How to Run

### 1. Clone the repository
```bash
git clone https://github.com/pooja-rani06/AI-Robotic-Emotion-System.git
cd AI-Robotic-Emotion-System
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file in the root directory and add:
```
GEMINI_API_KEY=your_api_key_here
```

⚠️ Do NOT expose your API key publicly.

### 4. Run the project
```bash
python main.py
```

---

## 🎙️ Usage
- Say **"capture my emotion"** → starts emotion detection and music response  
- Say **"stop"** or **"bye"** → exits the system  

---

## 👥 Contribution
This is a collaborative project developed as part of ongoing work.

**My contributions include:**
- Designing and implementing the emotion detection pipeline  
- Developing voice interaction modules (speech-to-text and text-to-speech)  
- Integrating conversational AI using Gemini API  
- Building the end-to-end perception-to-action system workflow  

---

## 📌 Project Status
This project is currently under active development.

- Core modules for emotion detection and interaction are functional  
- System integration is ongoing  
- Hardware-level actuation (robotic response) is under development  

---

## 🎯 Motivation
This project explores emotion-aware human-AI interaction, an important area in:
- Affective Computing  
- Human-Computer Interaction (HCI)  
- Social Robotics  

The goal is to build systems that can understand and respond to human emotional states in real time.

---

## 🚀 Future Work
- Integration with robotic facial actuation systems  
- Real-time servo-based expression control  
- Improved emotion classification using advanced models  
- Multimodal interaction (vision + speech + physical response)  
- Deployment on embedded platforms (e.g., Raspberry Pi)  

---

## ⚠️ Notes
- This repository contains the software pipeline of the system  
- Some components are part of an ongoing collaborative project and are not fully included here  

---

## 📬 Contact
If you are interested in this work or collaboration opportunities, feel free to connect via GitHub or LinkedIn.
