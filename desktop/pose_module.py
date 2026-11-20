import cv2
import mediapipe as mp
import time
import os
import math

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
video_path = os.path.join(script_dir, "videos", "5.mp4")

class PoseDetector:
    def __init__(self, mode = False, upper_body_only = False, smooth = True, detection_confidence=0.5, track_confidence = 0.5):
        self.mode = mode
        self.upper_body_only = upper_body_only
        self.smooth = smooth
        self.detection_confidence = detection_confidence
        self.track_confidence = track_confidence
        self.id_cx_cy = {}
        
        self.mpPose = mp.solutions.pose # Importing the pose module from mediapipe
        self.pose = self.mpPose.Pose(static_image_mode=self.mode, smooth_landmarks=self.smooth, min_detection_confidence=self.detection_confidence, min_tracking_confidence=self.track_confidence) # Creating a pose object
        self.mpDraw = mp.solutions.drawing_utils # Importing the drawing utils module to draw the 33 landmarks and connections
    
    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # Converting the image from BGR to RGB
        self.results = self.pose.process(imgRGB) # Processing the image to detect the pose, it outputs a class object
        if draw:
            if self.results.pose_landmarks: # Checking if the pose is detected from the class object, each landmark has a x, y, c, and visibility values
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS) # Drawing the landmarks and connections on the image which is displayed, not the imgRGB
        return img

    def findPosition(self, img, draw=True, landmark_id = None):
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.id_cx_cy[id] = (cx, cy)
                if draw:
                    if landmark_id is not None:
                        if id == landmark_id:
                            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
            
        return self.id_cx_cy

    def findAngle(self, img, p1, p2, p3, draw=True):
        if self.id_cx_cy:

            # Get the coordinates of the landmarks
            x1, y1 = self.id_cx_cy[p1]
            x2, y2 = self.id_cx_cy[p2]
            x3, y3 = self.id_cx_cy[p3]

            # Calculate the angle
            angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y2 - y1, x2 - x1))
            if angle < 0:
                angle += 360

            # Draw the lines and circles
            if draw:
                cv2.line(img, (x1, y1), (x2, y2), (0, 0, 0), 2)
                cv2.line(img, (x2, y2), (x3, y3), (0, 0, 0), 2)
                cv2.circle(img, (x1, y1), 8, (0, 0, 255), cv2.FILLED)
                cv2.circle(img, (x1, y1), 12, (0, 0, 255), 2)
                cv2.circle(img, (x2, y2), 8, (0, 0, 255), cv2.FILLED)
                cv2.circle(img, (x2, y2), 12, (0, 0, 255), 2)
                cv2.circle(img, (x3, y3), 8, (0, 0, 255), cv2.FILLED)
                cv2.circle(img, (x3, y3), 12, (0, 0, 255), 2)
                # cv2.putText(img, str(int(angle)), (x2, y2 - 20), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
            
            return angle
    
def main():
    cap = cv2.VideoCapture(video_path) # Capturing the pose video
    pTime = 0 
    detector = PoseDetector()
    # detector.upper_body_only = True
    while True:
        success, img = cap.read() # Capturing the video frame by frame
        if not success or img is None:
            break # Exit if video ended or frame is empty
        img = detector.findPose(img)
        id_cx_cy = detector.findPosition(img, draw=True, landmark_id=20) # Tracking the 20th landmark
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3) # Displaying the fps on the image with scale 3, purple color and thickness 3
        cv2.imshow("Image", img) # Displaying the image
        if cv2.waitKey(1) & 0xFF == ord("q"): # Pressing q to exit the loop
            break

    # Releasing the camera and closing the window
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()