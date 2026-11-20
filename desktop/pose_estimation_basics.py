import cv2
import mediapipe as mp
import time
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
video_path = os.path.join(script_dir, "videos", "1.mp4")

cap = cv2.VideoCapture(0) # Capturing the pose video

mpPose = mp.solutions.pose # Importing the pose module from mediapipe
pose = mpPose.Pose() # Creating a pose object
mpDraw = mp.solutions.drawing_utils # Importing the drawing utils module to draw the 33 landmarks and connections
pTime = 0 

while True:
    success, img = cap.read() # Capturing the video frame by frame
    if not success or img is None:
        break # Exit if video ended or frame is empty
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # Converting the image from BGR to RGB
    results = pose.process(imgRGB) # Processing the image to detect the pose, it outputs a class object
    if results.pose_landmarks: # Checking if the pose is detected from the class object, each landmark has a x, y, c, and visibility values
        mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS) # Drawing the landmarks and connections on the image which is displayed, not the imgRGB
        for id, lm in enumerate(results.pose_landmarks.landmark):
            h, w, c = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            if id == 12:
                cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)    
    cTime = time.time()
    fps = 1 / (cTime - pTime) if cTime > pTime else 0
    pTime = cTime
    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3) # Displaying the fps on the image with scale 3, purple color and thickness 3
    cv2.imshow("Image", img) # Displaying the image
    if cv2.waitKey(1) & 0xFF == ord("q"): # Pressing q to exit the loop
        break