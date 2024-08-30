import mediapipe as mp 
import cv2
import time
import math

# Variáveis de controle
startTime = 0
flagZeroTime = True
flagcaptured = False

alpha = 0.2
font = cv2.FONT_HERSHEY_SIMPLEX

foregroundOriginal = cv2.imread('C:\\xampp\\htdocs\\move_logo\\Eletromidia_logo.png') #win
#foregroundOriginal = cv2.imread('Eletromidia_logo.png') #linux
scale_percent = 25  # Percentual do tamanho original
widthOrg = int(foregroundOriginal.shape[1] * scale_percent / 100)
heightOrg = int(foregroundOriginal.shape[0] * scale_percent / 100)
foreground = cv2.resize(foregroundOriginal, (widthOrg, heightOrg), interpolation=cv2.INTER_AREA)

# Amplitude e frequência do movimento senoidal
amplitude = 200  # Amplitude do movimento
frequency = 0.1  # Frequência do movimento

# Posições iniciais do logo
forgX1 = 400
forgY1 = 400
forgX2 = forgX1 + widthOrg
forgY2 = forgY1 + heightOrg

mp_drawing = mp.solutions.drawing_utils  # Utilitário de desenho - Ajuda a renderizar os marcos
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

        # Garantir que as coordenadas estejam dentro dos limites do frame
        h, w, _ = frame.shape
        if forgX1 < 0: forgX1, forgX2 = 0, widthOrg
        if forgY1 < 0: forgY1, forgY2 = 0, heightOrg
        if forgX2 > w: forgX1, forgX2 = w - widthOrg, w
        if forgY2 > h: forgY1, forgY2 = h - heightOrg, h

        # Selecionar a região no fundo onde queremos adicionar a imagem
        added_image = cv2.addWeighted(frame[forgY1:forgY2, forgX1:forgX2], alpha, foreground[0:heightOrg, 0:widthOrg, :], 1 - alpha, 0)
        # Alterar a região com o resultado
        frame[forgY1:forgY2, forgX1:forgX2] = added_image

        # Iniciar a detecção
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True

        fingerTipX, fingerTipY = 0, 0

        if results.multi_hand_landmarks:
            for handLMS in results.multi_hand_landmarks:
                for id, lm in enumerate(handLMS.landmark):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    
                    if id == 8:  # Ponta do dedo indicador
                        cv2.circle(frame, (cx, cy), 15, (0, 255, 0), -1)
                        fingerTipX, fingerTipY = cx, cy

                        # Verifica se o dedo indicador está sobre a imagem
                        if forgX1 <= fingerTipX <= forgX2 and forgY1 <= fingerTipY <= forgY2:
                            if not flagcaptured:
                                flagcaptured = True
                                offsetX = fingerTipX - forgX1
                                offsetY = fingerTipY - forgY1

                            # Atualizar a posição do logo com o movimento do dedo
                            forgX1 = fingerTipX - offsetX
                            forgY1 = fingerTipY - offsetY
                            forgX2 = forgX1 + widthOrg
                            forgY2 = forgY1 + heightOrg
                        else:
                            flagcaptured = False

        # Converte de RGB de volta para BGR para exibição correta
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imshow('image', frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
