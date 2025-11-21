import cv2
import mediapipe as mp
import pyautogui
import signal
import sys

class HandController:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_draw = mp.solutions.drawing_utils
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Tracking states
        self.prev_hand = None
        self.hand_landmarks = None
        self.left_clicked = False
        self.right_clicked = False
        self.double_clicked = False
        self.dragging = False

    def update_finger_status(self):
        """Update finger states for gesture detection."""
        if not self.hand_landmarks:
            return

        def is_finger_down(tip, base):
            return self.hand_landmarks.landmark[tip].y > self.hand_landmarks.landmark[base].y
        
        self.fingers = {
            "index": is_finger_down(8, 5),
            "middle": is_finger_down(12, 9),
            "ring": is_finger_down(16, 13),
            "little": is_finger_down(20, 17),
            "thumb": is_finger_down(4, 2)
        }

        self.all_fingers_down = all(self.fingers.values())
        self.all_fingers_up = not any(self.fingers.values())

    def get_position(self, hand_x, hand_y):
        """Smooth cursor movement and prevent excessive jumps."""
        old_x, old_y = pyautogui.position()
        current_x = int(hand_x * self.screen_width)
        current_y = int(hand_y * self.screen_height)

        # Exponential smoothing for smoother movement
        if self.prev_hand:
            current_x = int(0.7 * self.prev_hand[0] + 0.3 * current_x)
            current_y = int(0.7 * self.prev_hand[1] + 0.3 * current_y)

        self.prev_hand = (current_x, current_y)

        # Boundary protection
        threshold = 5
        current_x = max(threshold, min(self.screen_width - threshold, current_x))
        current_y = max(threshold, min(self.screen_height - threshold, current_y))

        return current_x, current_y

    def handle_cursor(self):
        """Move cursor based on index finger position."""
        if not self.hand_landmarks:
            return
        
        x, y = self.get_position(
            self.hand_landmarks.landmark[9].x,
            self.hand_landmarks.landmark[9].y
        )

        if not (self.all_fingers_up and self.fingers["thumb"]):  
            pyautogui.moveTo(x, y, duration=0)

    def handle_scrolling(self):
        """Detect scrolling gestures."""
        if self.fingers["little"] and not self.fingers["index"]:
            pyautogui.scroll(120)
            print("Scrolling Up")
        elif self.fingers["index"] and not self.fingers["little"]:
            pyautogui.scroll(-120)
            print("Scrolling Down")

    def handle_clicking(self):
        """Detect left click, right click, and double click gestures."""
        if not self.hand_landmarks:
            return

        left_click = self.fingers["index"] and not self.fingers["middle"]
        right_click = self.fingers["middle"] and not self.fingers["index"]
        double_click = self.fingers["ring"] and not self.fingers["index"] and not self.fingers["middle"]

        try:
            if left_click and not self.left_clicked:
                pyautogui.click()
                self.left_clicked = True
                print("Left Click")
            elif not left_click:
                self.left_clicked = False

            if right_click and not self.right_clicked:
                pyautogui.rightClick()
                self.right_clicked = True
                print("Right Click")
            elif not right_click:
                self.right_clicked = False

            if double_click and not self.double_clicked:
                pyautogui.doubleClick()
                self.double_clicked = True
                print("Double Click")
            elif not double_click:
                self.double_clicked = False

        except Exception as e:
            print(f"Click Error: {e}")

    def run(self):
        """Main loop to capture frames and process gestures."""
        while self.cap.isOpened():
            success, img = self.cap.read()
            if not success:
                continue

            img = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(img_rgb)

            if results.multi_hand_landmarks:
                self.hand_landmarks = results.multi_hand_landmarks[0]
                self.mp_draw.draw_landmarks(img, self.hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                self.update_finger_status()
                self.handle_cursor()
                self.handle_scrolling()
                self.handle_clicking()

            cv2.imshow('Hand Tracker', img)
            if cv2.waitKey(5) & 0xFF == 27:  # Exit on 'ESC' key
                break

        self.cap.release()
        cv2.destroyAllWindows()

def run_system_control():
    controller = HandController()
    controller.run()

def exit_gracefully(signal_num, frame):
    print("Stopping System Control...")
    sys.exit(0)

signal.signal(signal.SIGTERM, exit_gracefully)

if __name__ == "__main__":
    run_system_control()
