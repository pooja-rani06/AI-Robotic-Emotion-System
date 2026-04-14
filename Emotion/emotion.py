# ---------------------- Import Required Libraries ----------------------

import cv2                # OpenCV → for computer vision (camera, drawing, image processing)
import math               # For mathematical operations (distance calculation)
from deepface import DeepFace   # DeepFace → for facial analysis (emotion, age, etc.)
import mediapipe as mp     # MediaPipe → for fast and efficient face detection

# ----------------------------------------------------------------------
# Function: simplify_emotion()
# Purpose: To simplify detailed emotions into 3 general categories
# ----------------------------------------------------------------------

def simplify_emotion(emotion):
    """
    Simplifies the detected emotion into 3 broad categories:
    'Happy', 'Sad', and 'Neutral'.
    """

    # Convert emotion string to lowercase to handle case variations
    emotion = emotion.lower()

    # Group positive emotions into "Happy"
    if emotion in ["happy", "surprise"]:
        return "Happy"

    # Group negative emotions into "Sad"
    elif emotion in ["sad", "fear", "disgust", "angry"]:
        return "Sad"

    # Any other emotion is treated as "Neutral"
    return "Neutral"


# ----------------------------------------------------------------------
# Step 1: Initialize camera and face detection module
# ----------------------------------------------------------------------

# Open webcam (0 = default camera)
cap = cv2.VideoCapture(0)

# Initialize MediaPipe's face detection with a minimum confidence of 0.5
face_detection = mp.solutions.face_detection.FaceDetection(0.5)


# ----------------------------------------------------------------------
# Step 2: Continuously capture video frames and process them
# ----------------------------------------------------------------------

while True:
    # Capture one frame from webcam
    ret, frame = cap.read()

    # If frame not captured properly (ret=False), break the loop
    if not ret:
        break

    # Get frame dimensions (height and width)
    h, w = frame.shape[:2]

    # Convert BGR (OpenCV format) → RGB (MediaPipe & DeepFace format)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Perform face detection using MediaPipe
    results = face_detection.process(rgb)

    # ------------------------------------------------------------------
    # If no face is detected in the frame, stop the program immediately
    # ------------------------------------------------------------------
    if not results.detections:
        print("No face detected. Exiting...")
        break

    # ------------------------------------------------------------------
    # Step 3: Among detected faces, find the one closest to the screen center
    # ------------------------------------------------------------------

    faces = []  # To store each face’s distance from center and bounding box

    for det in results.detections:
        # Extract relative bounding box (values between 0 and 1)
        box = det.location_data.relative_bounding_box

        # Convert relative box values to absolute pixel coordinates
        x1 = int(box.xmin * w)
        y1 = int(box.ymin * h)
        x2 = int((box.xmin + box.width) * w)
        y2 = int((box.ymin + box.height) * h)

        # Find face center
        cx, cy = (x1 + x2)//2, (y1 + y2)//2

        # Calculate Euclidean distance from screen center
        dist = math.hypot(cx - w//2, cy - h//2)

        # Store (distance, bounding box)
        faces.append((dist, (x1, y1, x2, y2)))

    # Choose the face nearest to the screen center
    _, (x1, y1, x2, y2) = min(faces, key=lambda f: f[0])

    # Crop the detected face region of interest (ROI)
    face_roi = rgb[y1:y2, x1:x2]


    # ------------------------------------------------------------------
    # Step 4: Use DeepFace to detect emotion on the selected face
    # ------------------------------------------------------------------

    try:
        # DeepFace.analyze() performs emotion analysis
        # - Converts face ROI to BGR (DeepFace expects BGR)
        # - actions=['emotion'] means only emotion analysis (not age/gender/race)
        # - enforce_detection=False prevents crash if face partially visible
        result = DeepFace.analyze(
            cv2.cvtColor(face_roi, cv2.COLOR_RGB2BGR),
            actions=['emotion'],
            enforce_detection=False
        )

        # Extract the dominant emotion (e.g., 'happy', 'sad', etc.)
        dominant_emotion = result[0]['dominant_emotion']

        # Simplify the emotion into 3 categories (Happy, Sad, Neutral)
        emotion = simplify_emotion(dominant_emotion)

    except:
        # If analysis fails for any reason (blur, low light, etc.)
        emotion = "Unknown"


    # ------------------------------------------------------------------
    # Step 5: Draw visual elements on the frame (bounding box, emotion label)
    # ------------------------------------------------------------------

    # Draw rectangle around the detected face
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

    # Put emotion label text below the face box
    cv2.putText(frame, f"Emotion: {emotion}", (x1, y2 + 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    # Draw a white dot in the middle of the screen (center marker)
    cv2.circle(frame, (w//2, h//2), 5, (255, 255, 255), -1)


    # ------------------------------------------------------------------
    # Step 6: Show the processed video frame in a display window
    # ------------------------------------------------------------------

    cv2.imshow("Face + Emotion Detection", frame)

    # If user presses 'q', exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# ----------------------------------------------------------------------
# Step 7: Cleanup → release resources and close windows
# ----------------------------------------------------------------------

# Stop the webcam
cap.release()

# Close all OpenCV windows
cv2.destroyAllWindows()

print("Camera released. Program ended.")
