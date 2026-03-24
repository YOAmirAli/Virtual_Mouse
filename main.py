import cv2
import pyautogui
import mediapipe as mp
import math
import time


click_times = []
scroll_mode = False
freeze_cursor = False
screenshot_cooldown = 2
last_screenshot_time = 0  

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

HANDS = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
screen_w, screen_h = pyautogui.size()

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    cvt = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = HANDS.process(cvt)

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
            
        
            thumb_tip = handLms.landmark[4]
            index_tip = handLms.landmark[8]
            
          
            fingers = [1 if handLms.landmark[tip].y < handLms.landmark[tip-2].y else 0 for tip in [8, 12, 16, 20]]

    
            dist = math.hypot(index_tip.x - thumb_tip.x, index_tip.y - thumb_tip.y)
            
            if dist < 0.06:
                if not freeze_cursor:
                    freeze_cursor = True
                    curr_click = time.time()
                    click_times.append(curr_click)
                    
                    if len(click_times) >= 2 and (click_times[-1] - click_times[-2] < 0.4):
                        pyautogui.doubleClick()
                        cv2.putText(frame, 'Double Click', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        click_times = []
                    else:
                        pyautogui.click()
                        cv2.putText(frame, 'Single Click', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            else:
                freeze_cursor = False
    
                screen_x = int(index_tip.x * screen_w)
                screen_y = int(index_tip.y * screen_h)
                pyautogui.moveTo(screen_x, screen_y, duration=0.05)

    
            if sum(fingers) == 4:
                if index_tip.y < 0.4:
                    pyautogui.scroll(60)
                    cv2.putText(frame, "Scroll Up", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                elif index_tip.y > 0.6:
                    pyautogui.scroll(-60)
                    cv2.putText(frame, "Scroll Down", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

          
            if sum(fingers) == 0:
                current_time = time.time()
                if current_time - last_screenshot_time > screenshot_cooldown:
                    pyautogui.screenshot(f"screenshot_{int(current_time)}.png")
                    last_screenshot_time = current_time
        

        if time.time() - last_screenshot_time < 1:
            cv2.putText(frame, "SCREENSHOT TAKEN!", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

    cv2.imshow('Hand Controller', frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
