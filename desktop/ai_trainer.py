import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow logging (0=all, 1=info, 2=warning, 3=error)
os.environ['GLOG_minloglevel'] = '3'  # Suppress Glog logging

import cv2
import mediapipe as mp
import time
import numpy as np
import pose_module as pm

# Suppress absl warnings
import logging
logging.getLogger('absl').setLevel(logging.ERROR)

wCam, hCam = 1280, 720

script_dir = os.path.dirname(os.path.abspath(__file__))
# Input source: True = webcam (calibration available), False = the video file below
USE_WEBCAM = False
VideoPath = os.path.join(script_dir, "videos", "1.mp4")
ImagePath = os.path.join(script_dir, "videos", "dips.jpeg")  # for single-image testing (see main loop)

cap = cv2.VideoCapture(0 if USE_WEBCAM else VideoPath)
if not cap.isOpened():
    raise SystemExit(f"Could not open {'webcam' if USE_WEBCAM else VideoPath}")
using_webcam = USE_WEBCAM

# Default angle range
min_angle = 25
max_angle = 150
calibrated = False
detector = pm.PoseDetector()

# Ask for calibration if using webcam
if using_webcam:
    calibrate_choice = input("Do you want to calibrate the angle range? (y/n): ").strip().lower()
    if calibrate_choice == 'y':
        # Ask for calibration mode
        calibration_mode_choice = input("Choose calibration mode - Manual (m) or Automatic (a): ").strip().lower()

        temp_min_angle = None
        temp_max_angle = None
        calibration_mode = True

        # AUTOMATIC CALIBRATION MODE
        if calibration_mode_choice == 'a':
            print("\n--- AUTOMATIC CALIBRATION MODE ---")
            print("Get ready! Calibration will start in a moment...\n")

            # Phase 1: Calibrate MIN angle
            print("PHASE 1: Calibrating MINIMUM angle (arm fully contracted)")
            print("Position yourself with arm contracted. Starting in 5 seconds...\n")
            time.sleep(5)

            countdown_duration = 7
            start_time = time.time()
            min_angle_samples = []

            while time.time() - start_time < countdown_duration:
                success, img = cap.read()
                if not success:
                    break
                img = cv2.resize(img, (wCam, hCam))

                img = detector.findPose(img, draw= False)
                id_cx_cy = detector.findPosition(img, draw=False, landmark_id=20)

                elapsed = time.time() - start_time
                remaining = int(countdown_duration - elapsed)

                # Display header
                cv2.rectangle(img, (200, 30), (1080, 180), (0, 100, 255), cv2.FILLED)
                cv2.putText(img, "CALIBRATING MIN ANGLE", (250, 100),
                           cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                cv2.putText(img, f"Time Remaining: {remaining}s", (380, 160),
                           cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                if id_cx_cy:
                    angle = detector.findAngle(img, 11, 13, 15, draw=True)
                    min_angle_samples.append(angle)

                    # Display current angle
                    cv2.rectangle(img, (400, 220), (880, 320), (255, 255, 255), cv2.FILLED)
                    cv2.putText(img, f"Current: {int(angle)}", (430, 290),
                               cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 255), 5)

                cv2.imshow("Calibration", img)
                cv2.waitKey(1)

            if min_angle_samples:
                temp_min_angle = sum(min_angle_samples) / len(min_angle_samples)
                print(f"MIN angle captured: {int(temp_min_angle)}\n")

            # Phase 2: Calibrate MAX angle
            print("PHASE 2: Calibrating MAXIMUM angle (arm fully extended)")
            print("Position yourself with arm extended. Starting in 3 seconds...\n")
            time.sleep(3)

            start_time = time.time()
            max_angle_samples = []

            while time.time() - start_time < countdown_duration:
                success, img = cap.read()
                if not success:
                    break
                img = cv2.resize(img, (wCam, hCam))

                img = detector.findPose(img, draw= False)
                id_cx_cy = detector.findPosition(img, draw=False, landmark_id=20)

                elapsed = time.time() - start_time
                remaining = int(countdown_duration - elapsed)

                # Display header
                cv2.rectangle(img, (200, 30), (1080, 180), (0, 255, 100), cv2.FILLED)
                cv2.putText(img, "CALIBRATING MAX ANGLE", (230, 100),
                           cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                cv2.putText(img, f"Time Remaining: {remaining}s", (380, 160),
                           cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                if id_cx_cy:
                    angle = detector.findAngle(img, 11, 13, 15, draw=True)
                    max_angle_samples.append(angle)

                    # Display current angle
                    cv2.rectangle(img, (400, 220), (880, 320), (255, 255, 255), cv2.FILLED)
                    cv2.putText(img, f"Current: {int(angle)}", (430, 290),
                               cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 255), 5)

                cv2.imshow("Calibration", img)
                cv2.waitKey(1)

            if max_angle_samples:
                temp_max_angle = sum(max_angle_samples) / len(max_angle_samples)
                print(f"MAX angle captured: {int(temp_max_angle)}\n")

            # Validate and finalize
            if temp_min_angle is not None and temp_max_angle is not None:
                if temp_min_angle < temp_max_angle:
                    min_angle = temp_min_angle
                    max_angle = temp_max_angle
                    calibrated = True
                    print(f"Automatic calibration complete!")
                    print(f"Min angle: {int(min_angle)}, Max angle: {int(max_angle)}\n")
                else:
                    print("Error: Captured MIN angle is greater than MAX angle.")
                    print(f"Using default values: MIN={min_angle}, MAX={max_angle}\n")
            else:
                print("Error: Could not capture angles. Using default values.\n")

            cv2.destroyAllWindows()
            cap.release()
            cap = cv2.VideoCapture(0)

        # MANUAL CALIBRATION MODE
        else:
            print("\n--- MANUAL CALIBRATION MODE ---")
            print("Position yourself in front of the camera")
            print("Press 'n' to set MINIMUM angle (arm fully contracted)")
            print("Press 'm' to set MAXIMUM angle (arm fully extended)")
            print("Press 'c' to COMPLETE calibration")
            print("Press 'q' to quit\n")

            while calibration_mode:
                success, img = cap.read()
                if not success:
                    break
                img = cv2.resize(img, (wCam, hCam))

                img = detector.findPose(img, draw=False)
                id_cx_cy = detector.findPosition(img, draw=False, landmark_id=20)

                if id_cx_cy:
                    # Find the current angle
                    angle = detector.findAngle(img, 11, 13, 15, draw=True)

                    # Display current angle prominently
                    cv2.rectangle(img, (400, 50), (880, 150), (255, 255, 255), cv2.FILLED)
                    cv2.putText(img, f"Current Angle: {int(angle)}", (420, 120),
                               cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 255), 5)

                    # Display calibration instructions
                    cv2.putText(img, "Press 'n' for MIN | 'm' for MAX | 'c' to COMPLETE",
                               (250, 200), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

                    # Display current calibration values
                    if temp_min_angle is not None:
                        cv2.putText(img, f"MIN Angle: {int(temp_min_angle)}", (50, 300),
                                   cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
                    else:
                        cv2.putText(img, "MIN Angle: Not Set", (50, 300),
                                   cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

                    if temp_max_angle is not None:
                        cv2.putText(img, f"MAX Angle: {int(temp_max_angle)}", (50, 370),
                                   cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
                    else:
                        cv2.putText(img, "MAX Angle: Not Set", (50, 370),
                                   cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

                cv2.imshow("Calibration", img)
                key = cv2.waitKey(1) & 0xFF

                if key == ord('n'):
                    if id_cx_cy:
                        temp_min_angle = angle
                        print(f"Minimum angle set to: {int(temp_min_angle)}")
                elif key == ord('m'):
                    if id_cx_cy:
                        temp_max_angle = angle
                        print(f"Maximum angle set to: {int(temp_max_angle)}")
                elif key == ord('c'):
                    if temp_min_angle is not None and temp_max_angle is not None:
                        # Ensure min is less than max
                        if temp_min_angle < temp_max_angle:
                            min_angle = temp_min_angle
                            max_angle = temp_max_angle
                            calibrated = True
                            print(f"\nCalibration complete!")
                            print(f"Min angle: {int(min_angle)}, Max angle: {int(max_angle)}")
                            calibration_mode = False
                        else:
                            print("Error: MIN angle must be less than MAX angle. Please recalibrate.")
                            temp_min_angle = None
                            temp_max_angle = None
                    else:
                        print("Please set both MIN and MAX angles before completing calibration.")
                elif key == ord('q'):
                    print("Calibration cancelled. Using default values.")
                    calibration_mode = False

            cv2.destroyAllWindows()
            # Reset capture for main loop
            cap.release()
            cap = cv2.VideoCapture(0)
    else:
        print(f"Using default angle range: MIN={min_angle}, MAX={max_angle}")

pTime = 0
count = 0
dir = 0

while True:
    success, img = cap.read()
    if not success:
        break
    img = cv2.resize(img, (wCam, hCam))
    # img = cv2.imread(ImagePath)
    # img = cv2.resize(img, (600, 600))
    
    img = detector.findPose(img, draw= False)
    id_cx_cy = detector.findPosition(img, draw=False, landmark_id=20) # Tracking the 20th landmark

    if id_cx_cy:
        # Find the angle for the Left Arm
        angle = detector.findAngle(img, 11, 13, 15, draw=True)
        per = np.interp(angle, (min_angle, max_angle), (0, 100))
        bar = np.interp(angle, (min_angle, max_angle), (650, 100))

        color = (255, 0, 255)
        # Check for the direction of the arm and curls
        if per == 100:
            color = (0, 255, 0)
            if dir == 0:
                count += 0.5
                dir = 1
        if per == 0:
            if dir == 1:
                count += 0.5
                dir = 0

        # Display the counts
        if count < 10:
            cv2.rectangle(img, (0, 520), (200, 720), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, str(int(count)), (35, 690), cv2.FONT_HERSHEY_PLAIN, 13, (255, 0, 0), 18)
        else:
            cv2.rectangle(img, (0, 520), (320, 720), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, str(int(count)), (25, 690), cv2.FONT_HERSHEY_PLAIN, 13, (255, 0, 0), 18)

        # Display the bar
        cv2.rectangle(img, (1100, 100), (1175, 650), color, 3)
        cv2.rectangle(img, (1100, int(bar)), (1175, 650), color, cv2.FILLED)
        cv2.putText(img, f"{int(per)} %", (1080, 75), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f"FPS: {int(fps)}", (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2) # Displaying the fps on the image with scale 3, purple color and thickness 3
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Releasing the camera and closing the window
cap.release()
cv2.destroyAllWindows()