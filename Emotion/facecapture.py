import cv2
import mediapipe as mp
import math

# Initialize MediaPipe face detection and drawing utils
mp_face_detection = mp.solutions.face_detection        # Face detection module
mp_face_mesh = mp.solutions.face_mesh                  # Face mesh module
mp_drawing = mp.solutions.drawing_utils                # Drawing helper functions

# Start webcam
cap = cv2.VideoCapture(0)                              # Open default camera (index 0)

# Initialize Face Detection and Face Mesh
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

# --------- MAIN LOOP (Runs continuously to capture frames) --------- #
while True:
    ret, frame = cap.read()                            # Capture a single frame from webcam
    if not ret:                                        # If frame not captured correctly
        break                                          # Exit the loop

    # Convert frame from BGR to RGB (because MediaPipe uses RGB images)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the RGB frame using MediaPipe Face Detection
    results = face_detection.process(rgb_frame)

    # Get the frame dimensions
    h, w, c = frame.shape

    # Create empty list to store information of all detected faces
    faces = []

    # ---------------- FACE DETECTION ---------------- #
    if results.detections:                             # If one or more faces detected
        for detection in results.detections:           # Loop through each detected face
            # Get relative bounding box of face (values between 0–1)
            bboxC = detection.location_data.relative_bounding_box

            # Convert relative coordinates to actual pixel coordinates
            x1 = int(bboxC.xmin * w)
            y1 = int(bboxC.ymin * h)
            x2 = int((bboxC.xmin + bboxC.width) * w)
            y2 = int((bboxC.ymin + bboxC.height) * h)

            # Calculate face center (average of box corners)
            face_cx = (x1 + x2) // 2
            face_cy = (y1 + y2) // 2

            # Calculate screen center
            center_x, center_y = w // 2, h // 2

            # Compute distance of face center from screen center using Euclidean distance
            distance = math.sqrt((center_x - face_cx)**2 + (center_y - face_cy)**2)

            # Store face information: bounding box, center, and distance
            faces.append({
                'bbox': (x1, y1, x2, y2),
                'center': (face_cx, face_cy),
                'distance': distance
            })

        # ---------------- SORT FACES BY DISTANCE ---------------- #
        # Sort all detected faces by distance from screen center
        faces.sort(key=lambda f: f['distance'])

        # ---------------- DRAW BOUNDING BOXES ---------------- #
        for i, face in enumerate(faces):               # Loop through all faces
            x1, y1, x2, y2 = face['bbox']              # Get face box coordinates
            label = f"Face {i+1} (Dist: {int(face['distance'])})"

            # Draw rectangle around the face
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Write label text above the box showing face number and distance
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)

            # Draw small blue circle at face center
            cv2.circle(frame, face['center'], 4, (255, 0, 0), -1)

        # ---------------- PROCESS NEAREST FACE ONLY ---------------- #
        # Pick the nearest face (first one in sorted list)
        nearest_face = faces[0]
        x1, y1, x2, y2 = nearest_face['bbox']

        # Extract region of interest (face area only)
        face_roi = rgb_frame[y1:y2, x1:x2]

        # Run face mesh detection only on that nearest face region
        face_mesh_results = face_mesh.process(face_roi)

        # ---------------- DRAW FACE MESH LANDMARKS ---------------- #
        if face_mesh_results.multi_face_landmarks:
            for landmarks in face_mesh_results.multi_face_landmarks:
                for lm in landmarks.landmark:          # Loop through each landmark point
                    # Convert normalized landmark coordinates to full image coordinates
                    x = int(x1 + lm.x * (x2 - x1))
                    y = int(y1 + lm.y * (y2 - y1))

                    # Draw small red dot for each landmark
                    cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)

    # ---------------- DRAW SCREEN CENTER ---------------- #
    cv2.circle(frame, (w // 2, h // 2), 5, (255, 255, 255), -1)  # Draw white dot at screen center
    cv2.putText(frame, "Screen Center", (w//2 - 70, h//2 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # ---------------- DISPLAY RESULT FRAME ---------------- #
    cv2.imshow("Nearest Face Mesh Detection", frame)

    # ---------------- EXIT CONDITION ---------------- #
    # If the 'q' key is pressed, exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ---------------- CLEANUP ---------------- #
cap.release()                   # Release camera resource
cv2.destroyAllWindows()          # Close all OpenCV windows



