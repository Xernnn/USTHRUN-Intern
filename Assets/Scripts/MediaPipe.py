import cv2
import mediapipe as mp
import keyboard as kb
import time
import numpy as np
import ctypes

# Get screen size
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)

# Set fixed window location and size (1/4 of the screen size)
fixed_width = screen_width // 4
fixed_height = screen_height // 4
window_x = 0  # Position at the bottom-right corner
window_y = 0

# Create a named window with no border
cv2.namedWindow('MediaPipe Pose', cv2.WINDOW_NORMAL) 
cv2.moveWindow('MediaPipe Pose', window_x, window_y)
cv2.resizeWindow('MediaPipe Pose', fixed_width, fixed_height)

# Remove window borders
cv2.setWindowProperty('MediaPipe Pose', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
cv2.setWindowProperty('MediaPipe Pose', cv2.WND_PROP_TOPMOST, 1)

# Get window handle
hwnd = ctypes.windll.user32.FindWindowW(None, "MediaPipe Pose")

# Remove title bar and border (GWL_STYLE) and make window layered and transparent to mouse events (GWL_EXSTYLE)
ctypes.windll.user32.SetWindowLongW(hwnd, -16, ctypes.windll.user32.GetWindowLongW(hwnd, -16) & ~0x00800000)  # WS_CAPTION
ctypes.windll.user32.SetWindowLongW(hwnd, -20, ctypes.windll.user32.GetWindowLongW(hwnd, -20) | 0x80000 | 0x20)  # WS_EX_LAYERED | WS_EX_TRANSPARENT

# Set window opacity (0-255, where 0 is fully transparent and 255 is fully opaque)
opacity = 192  # Example value, adjust as needed
ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, opacity, 0x2)

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands

# Parameters for pose detection
bool = False
threshold_clap = 0.08
threshold_horizontal = 0
threshold_vertical = -0.2
prev_frame_width = 0
prev_frame_height = 0

# Initialize the fixed variables
left_fixed = 0
right_fixed = 0
upper_fixed = 0
lower_fixed = 0

def pose_detection(image, pose):
    global bool, prev_frame_width, prev_frame_height, left_fixed, right_fixed, upper_fixed, lower_fixed
    height, width, _ = image.shape
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    if results.pose_landmarks:
        center_width = int((results.pose_landmarks.landmark[11].x + results.pose_landmarks.landmark[12].x
                            + (results.pose_landmarks.landmark[23].x + results.pose_landmarks.landmark[24].x) / 2) / 3 * width)
        center_height = int((results.pose_landmarks.landmark[11].y + results.pose_landmarks.landmark[12].y
                             + (results.pose_landmarks.landmark[23].y + results.pose_landmarks.landmark[24].y) / 2) / 3 * height)
        cv2.circle(image, (center_width, center_height), radius=10, color=(0, 0, 255), thickness=-1)

        if prev_frame_width == 0 and prev_frame_height:
            prev_frame_width = center_width
            prev_frame_height = center_height

        if not bool:
            left = int(results.pose_landmarks.landmark[11].x * width)
            right = int(results.pose_landmarks.landmark[12].x * width)
            left_fixed = int(left + (left - right) * threshold_horizontal)
            right_fixed = int(right - (left - right) * threshold_horizontal)

            upper = int(results.pose_landmarks.landmark[12].y * height)
            lower = int(results.pose_landmarks.landmark[24].y * height)
            upper_fixed = int(upper - (lower - upper) * threshold_vertical)
            lower_fixed = int(lower + (lower - upper) * threshold_vertical)

        width_clap_l = int(results.pose_landmarks.landmark[19].x * width)
        width_clap_r = int(results.pose_landmarks.landmark[20].x * width)

        if (width_clap_l - width_clap_r) / width < threshold_clap and not bool:
            bool = True
            print("locked")
            kb.send("space")

        if bool:
            # Draw the rectangle
            cv2.rectangle(image, (left_fixed, upper_fixed), (right_fixed, lower_fixed), (255, 0, 0), 2)

            if center_width <= right_fixed and prev_frame_width > right_fixed:
                print("right")
                kb.send("right")
            if center_width >= left_fixed and prev_frame_width < left_fixed:
                print("left")
                kb.send("left")
            if center_width > right_fixed and prev_frame_width <= right_fixed:
                print("left")
                kb.send("left")
            if center_width < left_fixed and prev_frame_width >= left_fixed:
                print("right")
                kb.send("right")
            if center_height <= upper_fixed and prev_frame_height > upper_fixed:
                print("jump")
                kb.send("up")
            if center_height >= lower_fixed and prev_frame_height < lower_fixed:
                print("crouch")
                kb.send("down")

        prev_frame_width = center_width
        prev_frame_height = center_height

    return image

def hand_detection(image, hands, process_left_hand=False):
    height, width, _ = image.shape
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            if process_left_hand:
                hand_center_x = int((hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].x + 
                                     hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP].x + 
                                     hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x) / 3 * width)
                hand_center_y = int((hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].y + 
                                     hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP].y + 
                                     hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y) / 3 * height)
                cv2.circle(image, (hand_center_x, hand_center_y), radius=10, color=(0, 0, 255), thickness=-1)
            else:
                hand_center_x = int((hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].x + 
                                     hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP].x + 
                                     hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x) / 3 * width)
                hand_center_y = int((hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].y + 
                                     hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP].y + 
                                     hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y) / 3 * height)
                cv2.circle(image, (hand_center_x, hand_center_y), radius=10, color=(0, 0, 255), thickness=-1)
            break  # Process only the first detected hand
    return image

def main():
    cap = cv2.VideoCapture(0)
    prev_frame_time = 0
    new_frame_time = 0

    # Model switch variable
    model = 'pose'
    process_left_hand = False

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose, \
         mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:

        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                break

            # Resize the image to fixed dimensions with appropriate interpolation
            image = cv2.resize(image, (fixed_width, fixed_height), interpolation=cv2.INTER_LINEAR)

            # Switch models on spacebar press
            if kb.is_pressed('space'):
                if model == 'pose':
                    model = 'hands'
                else:
                    model = 'pose'
                time.sleep(0.5)  # To prevent multiple toggles on a single press

            # Switch hand processing on enter press
            if kb.is_pressed('enter'):
                process_left_hand = not process_left_hand
                time.sleep(0.5)  # To prevent multiple toggles on a single press

            if model == 'pose':
                image = pose_detection(image, pose)
            elif model == 'hands':
                image = hand_detection(image, hands, process_left_hand)

            image = cv2.flip(image, 1)
            # font = cv2.FONT_HERSHEY_SIMPLEX
            # new_frame_time = time.time()
            # fps = 1 / (new_frame_time - prev_frame_time)
            # prev_frame_time = new_frame_time
            # fps = int(fps)
            # fps = str(fps)
            # cv2.putText(image, fps, (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA)

            cv2.imshow('MediaPipe Pose', image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
