import tensorflow as tf
import numpy as np
import keyboard as kb
import cv2
import time
import ctypes
import os

# Get screen size
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)

# Set fixed window location and size
fixed_width = screen_width // 4
fixed_height = screen_height // 4
window_x = 0
window_y = 0

# Create a named window with no border
cv2.namedWindow('MoveNet Pose', cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty('MoveNet Pose', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.moveWindow('MoveNet Pose', window_x, window_y)

# Make window transparent
hwnd = ctypes.windll.user32.FindWindowW(None, "MoveNet Pose")
ctypes.windll.user32.SetWindowLongW(hwnd, -20, ctypes.windll.user32.GetWindowLongW(hwnd, -20) | 0x80000 | 0x20)

# Set window opacity (0-255, where 0 is fully transparent and 255 is fully opaque)
opacity = 192  # Example value, adjust as needed
ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, opacity, 0x2)

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

# Load the TFLite model
pose_model_path = "c:/Users/stdso/Final/Assets/Scripts/3.tflite"  # Adjust the path as needed
if not os.path.exists(pose_model_path):
    raise FileNotFoundError(f"The model file at {pose_model_path} does not exist.")
pose_interpreter = tf.lite.Interpreter(model_path=pose_model_path)
pose_interpreter.allocate_tensors()

hands_model_path = "c:/Users/stdso/Final/Assets/Scripts/hands_model.tflite"  # Add the actual path to the hands model
if not os.path.exists(hands_model_path):
    raise FileNotFoundError(f"The model file at {hands_model_path} does not exist.")
hands_interpreter = tf.lite.Interpreter(model_path=hands_model_path)
hands_interpreter.allocate_tensors()

def process_pose(image):
    global bool, prev_frame_width, prev_frame_height, left_fixed, right_fixed, upper_fixed, lower_fixed
    height, width, _ = image.shape
    image_resized = tf.image.resize_with_pad(np.expand_dims(image.copy(), axis=0), 192, 192)
    input_image = tf.cast(image_resized, dtype=tf.float32)

    input_details = pose_interpreter.get_input_details()
    output_details = pose_interpreter.get_output_details()

    pose_interpreter.set_tensor(input_details[0]['index'], np.array(input_image))
    pose_interpreter.invoke()

    keypoints_with_scores = pose_interpreter.get_tensor(output_details[0]['index'])
    keypoints = np.squeeze(np.multiply(keypoints_with_scores, [height, width, 1]))

    for keypoint in keypoints:
        ky, kx, ks = keypoint
        if ks > threshold_clap:
            cv2.circle(image, (int(kx), int(ky)), 4, (0, 255, 0), -1)

    center_width = int((keypoints[5][1] + keypoints[6][1] + (keypoints[11][1] + keypoints[12][1]) / 2) / 3 * width)
    center_height = int((keypoints[5][0] + keypoints[6][0] + (keypoints[11][0] + keypoints[12][0]) / 2) / 3 * height)
    cv2.circle(image, (center_width, center_height), radius=10, color=(0, 0, 255), thickness=-1)

    if prev_frame_width == 0 and prev_frame_height == 0:
        prev_frame_width = center_width
        prev_frame_height = center_height

    if not bool:
        left = int(keypoints[5][1] * width)
        right = int(keypoints[6][1] * width)
        left_fixed = int(left + (left - right) * threshold_horizontal)
        right_fixed = int(right - (left - right) * threshold_horizontal)

        upper = int(keypoints[6][0] * height)
        lower = int(keypoints[12][0] * height)
        upper_fixed = int(upper - (lower - upper) * threshold_vertical)
        lower_fixed = int(lower + (lower - upper) * threshold_vertical)

    width_clap_l = int(keypoints[9][1] * width)
    width_clap_r = int(keypoints[10][1] * width)

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

def process_hands(image, process_left_hand=False):
    height, width, _ = image.shape
    image_resized = tf.image.resize_with_pad(np.expand_dims(image.copy(), axis=0), 192, 192)
    input_image = tf.cast(image_resized, dtype=tf.float32)

    input_details = hands_interpreter.get_input_details()
    output_details = hands_interpreter.get_output_details()

    hands_interpreter.set_tensor(input_details[0]['index'], np.array(input_image))
    hands_interpreter.invoke()

    keypoints_with_scores = hands_interpreter.get_tensor(output_details[0]['index'])
    keypoints = np.squeeze(np.multiply(keypoints_with_scores, [height, width, 1]))

    for hand_landmarks in keypoints:
        if process_left_hand:
            hand_center_x = int((hand_landmarks[5][1] + hand_landmarks[17][1] + hand_landmarks[0][1]) / 3 * width)
            hand_center_y = int((hand_landmarks[5][0] + hand_landmarks[17][0] + hand_landmarks[0][0]) / 3 * height)
        else:
            hand_center_x = int((hand_landmarks[5][1] + hand_landmarks[17][1] + hand_landmarks[0][1]) / 3 * width)
            hand_center_y = int((hand_landmarks[5][0] + hand_landmarks[17][0] + hand_landmarks[0][0]) / 3 * height)
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
            image = process_pose(image)
        elif model == 'hands':
            image = process_hands(image, process_left_hand)

        image = cv2.flip(image, 1)

        font = cv2.FONT_HERSHEY_SIMPLEX
        new_frame_time = time.time()
        fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time
        fps = int(fps)
        fps = str(fps)
        cv2.putText(image, fps, (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA)

        cv2.imshow('MoveNet Pose', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
