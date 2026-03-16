import cv2
import pyautogui
import mediapipe as mp
import math
import time
click_start_time=None
click_times=[]
click_cooldown=0.5
scroll_mode=False
freeze_cursor=False

mp_hands=mp.solutions.hands
mp_drawing=mp.solutions.drawing_utils

HANDS=mp_hands.Hands(max_num_hands=1,min_detection_confidence=0.7)
screen_w,screen_h=pyautogui.size()
print("speed controlled by hand")
prev_x,prev_y=0,0

cap=cv2.VideoCapture(0)
if not cap.isOpened():
   print("cant open camera")
   exit()
while True:
   ret,frame=cap.read()
   if not ret:
      print("cant receive frame")
      break
   frame=cv2.flip(frame,1)
   cvt=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

   result=HANDS.process(cvt)
   if result.multi_hand_landmarks:
      for handLms in result.multi_hand_landmarks:

         mp_drawing.draw_landmarks(frame,handLms,mp_hands.HAND_CONNECTIONS)
         thumb_tip=handLms.landmark[4]
         index_tip=handLms.landmark[8]
         middle_tip=handLms.landmark[12]
         ring_tip=handLms.landmark[16]
         pinky_tip=handLms.landmark[20]
         fingers=[

           1 if handLms.landmark[tip].y<handLms.landmark[tip-2].y else 0 for tip in [8,12,16,20]

         ]
      dist=math.hypot(index_tip.x-thumb_tip.x,index_tip.y-thumb_tip.y)
      if dist<0.06:
         if not freeze_cursor:
            freeze_cursor=True
            click_times.append(time.time())
            # double click
          
            if len(click_times)>=2 and click_times[-1]-click_times[-2]<0.4:
               pyautogui.doubleClick()

               cv2.putText(frame,'double click',(10,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),2)
               click_times=[]
            else:
               pyautogui.click()
               cv2.putText(frame,'single click',(10,50),cv2.FONT_HERSHEY_DUPLEX,1,(255,255,0),2)
      else:
         freeze_cursor=False   
              
   cv2.imshow('frame',frame)

   if cv2.waitKey(1)==ord('q'):
      break
cap.release()
cv2.destroyAllWindows()