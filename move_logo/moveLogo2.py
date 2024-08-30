import mediapipe as mp 
import cv2
import time
import math

# create an overlay image. You can use any image

startTime = 0
flagZeroTime = True
flagcaptured = False

alpha = 0.2
font = cv2.FONT_HERSHEY_SIMPLEX

foregroundOriginal = cv2.imread('C:\\xampp\\htdocs\\move_logo\\Eletromidia_logo.png') #win
#foregroundOriginal = cv2.imread('Eletromidia_logo.png') #linux
scale_percent = 25  # percent of original size
widthOrg = int(foregroundOriginal.shape[1] * scale_percent / 100)
heightOrg = int(foregroundOriginal.shape[0] * scale_percent / 100)
foreground = cv2.resize(foregroundOriginal, (widthOrg, heightOrg), interpolation=cv2.INTER_AREA)

# Amplitude e frequência do movimento senoidal
amplitude = 200  # Amplitude do movimento (pode ajustar conforme desejado)
frequency = 0.1  # Frequência do movimento (pode ajustar conforme desejado)

# Posições iniciais do logo
forgX1 = 400
forgY1 = 400
forgX2 = forgX1 + widthOrg
forgY2 = forgY1 + heightOrg

mp_drawing = mp.solutions.drawing_utils  # drawing utility - Help to render the landmarks
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)
cap.set(3, 1024)
cap.set(4, 768)

with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.4) as hands:

    while cap.isOpened():

        re, frame = cap.read()
        frame = cv2.flip(frame, 1)

        # Movimento senoidal
        if not flagcaptured:
            offset_x = amplitude * math.sin(time.time() * frequency)
            offset_y = amplitude * math.cos(time.time() * frequency)

            # Atualizar posições do logo com o movimento senoidal quando não está sendo capturado
            forgX1 = int(200 + offset_x)
            forgY1 = int(200 + offset_y)
            forgX2 = forgX1 + widthOrg
            forgY2 = forgY1 + heightOrg

        # Select the region in the background where we want to add the image and add the images using cv2.addWeighted()
        added_image = cv2.addWeighted(frame[forgY1:forgY2, forgX1:forgX2], alpha, foreground[0:heightOrg, 0:widthOrg, :], 1 - alpha, 0)
        # Change the region with the result
        frame[forgY1:forgY2, forgX1:forgX2] = added_image
        
        # Start the detection
        # =======================
        # change it to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True

        thumbX = 1
        thumbY = 1
        fingerTipX = 0
        fingerTipY = 0

        cv2.putText(image, 'PROJETO FINEP', (775, 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(image, 'INTERAGIR COM LOGO', (665, 90), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2, cv2.LINE_AA)
        
        if results.multi_hand_landmarks:

            for handLMS in results.multi_hand_landmarks:
                for id, lm in enumerate(handLMS.landmark):
                    h, w, c = image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    
                    if id == 4:  # this is the thumb landmark
                        cv2.circle(image, (cx, cy), 15, (255, 0, 255), -1)
                        thumbX = cx
                        thumbY = cy
                                            
                    if id == 12:  # this is the finger landmark
                        cv2.circle(image, (cx, cy), 15, (255, 0, 255), -1)
                        fingerTipX = cx
                        fingerTipY = cy

                    if id == 16:  # Higher finger
                        cv2.circle(image, (cx, cy), 15, (255, 0, 255), -1)
                        higherFingerX = cx
                        higherFingerY = cy 
  
                cv2.rectangle(image, (1 * thumbX, 1 * thumbY), (1 * fingerTipX, 1 * fingerTipY), (255, 255, 0), 2)

                if flagcaptured:
                    cv2.circle(image, (40, 30), 20, (255, 0, 0), -1)  # red circle means it was captured 
                    cv2.putText(image, 'CAPTURADO!', (20, 120), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                    
                    if fingerTipX - thumbX > 25 and thumbY - fingerTipY > 25:
                        newXpos = int((fingerTipX - thumbX) / 2) - int(widthOrg / 2)
                        newYpos = int((fingerTipY - thumbY) / 2) - int(heightOrg / 2)

                        forgX1 = thumbX + newXpos
                        forgX2 = forgX1 + widthOrg

                        forgY1 = thumbY + newYpos
                        forgY2 = forgY1 + heightOrg

                    if higherFingerY < forgY1: 
                        flagcaptured = False
                
                else:
                    if thumbX <= forgX1 and fingerTipX >= forgX2:
                        if flagZeroTime:
                            startTime = time.time()
                            flagZeroTime = False
                        else:
                            if time.time() - startTime > 1:
                                flagcaptured = True
                    else:
                        flagZeroTime = True

        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imshow('image', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()