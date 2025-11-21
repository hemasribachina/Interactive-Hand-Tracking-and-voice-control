import cv2
import mediapipe as mp
import math
import sys
import signal

# Graceful exit function for termination
def signal_handler(sig, frame):
    print("Exiting Virtual Calculator.")
    cap.release()
    cv2.destroyAllWindows()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)  # Handle CTRL+C to stop

# Hand Tracker Class
class Tracker:
    def __init__(self, static_image_mode=False, max_num_hands=1, 
                 min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.static_image_mode = static_image_mode
        self.max_num_hands = max_num_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        # ✅ Define mp_hands before using it
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=self.static_image_mode,
                                         max_num_hands=self.max_num_hands,
                                         min_detection_confidence=self.min_detection_confidence,
                                         min_tracking_confidence=self.min_tracking_confidence)
        self.mpDraw = mp.solutions.drawing_utils
        self.tracking_id = [8, 12]  # Index and middle finger
    
    def hand_landmark(self, img):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        return img
    
    def tracking(self, img):
        tracking_points = []
        dist = float('inf')  # Use infinity to avoid errors
        x1, y1, x2, y2 = -1, -1, -1, -1

        if self.results.multi_hand_landmarks and len(self.results.multi_hand_landmarks) > 0:
            hand_landmarks = self.results.multi_hand_landmarks[0]
            for id, lm in enumerate(hand_landmarks.landmark):
                if id in self.tracking_id:
                    h, w, c = img.shape
                    x, y = int(lm.x * w), int(lm.y * h)
                    tracking_points.append((x, y))
                    cv2.circle(img, (x, y), 10, (255, 0, 255), cv2.FILLED)
            
            if len(tracking_points) == 2:
                x1, y1 = tracking_points[0]
                x2, y2 = tracking_points[1]
                x_c = (x1 + x2) // 2
                y_c = (y1 + y2) // 2
                cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                cv2.circle(img, (x_c, y_c), 10, (255, 0, 255), cv2.FILLED)
                
                # ✅ Prevent division by zero error
                if x1 != -1 and y1 != -1 and x2 != -1 and y2 != -1:
                    dist = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                    cv2.putText(img, f'distance: {dist:.2f}', (40, 40), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)

        return img, dist, x1, y1

# Button Class
class Button:
    def __init__(self, x, y, w, h, value):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.value = value
        self.font = cv2.FONT_HERSHEY_COMPLEX
        self.font_color = (255, 255, 255)
        self.thick = 1
        self.font_size = 1.2
        self.text_width, self.text_height = cv2.getTextSize(self.value, self.font, self.font_size, self.thick)[0]
    
    def draw(self, img):
        cv2.rectangle(img, (self.x, self.y), (self.x + self.w, self.y + self.h), (50, 50, 50), cv2.FILLED)
        cv2.rectangle(img, (self.x, self.y), (self.x + self.w, self.y + self.h), (10, 10, 10), 3)
        cv2.putText(img, self.value, (self.x + (self.w - self.text_width) // 2, self.y + (self.h + self.text_height) // 2),
                    self.font, self.font_size, self.font_color, self.thick)
        return img
    
    def check_click(self, img, dist, x1, y1):
        if (self.x <= x1 <= self.x + self.w) and (self.y <= y1 <= self.y + self.h) and dist <= 35:
            cv2.rectangle(img, (self.x, self.y), (self.x + self.w, self.y + self.h), (0, 255, 0), cv2.FILLED)
            return True
        return False

# Function to draw the calculator
def draw_calculator(img):
    button_values = [['7', '8', '9', '^', '('],
                     ['4', '5', '6', '*', ')'],
                     ['1', '2', '3', '-', 'DEL'],
                     ['0', '.', '/', '+', '=']]
    button_list = [Button(600 + 80*j, 200 + 80*i, 80, 80, button_values[i][j]) for i in range(4) for j in range(5)]
    button_list.append(Button(840, 520, 160, 80, 'CLEAR'))
    
    for button in button_list:
        img = button.draw(img)
    
    # Equation/Result Box
    cv2.rectangle(img, (600, 100), (1000, 200), (50, 50, 50), cv2.FILLED)
    return img, button_list

if __name__ == "__main__":
    # ✅ Camera Setup with error handling
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Camera not accessible.")
        sys.exit(1)

    cap.set(3, 1280)  # Width
    cap.set(4, 720)   # Height

    tracker = Tracker()
    equation = ''
    delay = 0
    result = ''

    while True:
        success, img = cap.read()
        if not success or img is None:
            print("Failed to capture image.")
            break

        img = cv2.flip(img, 1)
        img = tracker.hand_landmark(img)
        img, button_list = draw_calculator(img)
        img, dist, x1, y1 = tracker.tracking(img)

        if delay > 0:
            delay -= 1

        for button in button_list:
            if button.check_click(img, dist, x1, y1) and delay == 0:
                delay = 10
                value = button.value

                if value == '=':
                    try:
                        result = str(eval(equation))
                        equation = result
                    except Exception:
                        result = "Error"
                        equation = ''
                elif value == 'DEL':
                    equation = equation[:-1]
                elif value == 'CLEAR':
                    equation = ''
                    result = ''
                else:
                    equation += value

        cv2.putText(img, equation, (610, 150), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
        if result:
            cv2.putText(img, f"= {result}", (610, 180), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow('Virtual Calculator', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
