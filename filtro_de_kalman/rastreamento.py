import cv2
import numpy as np

# Inicializa o Filtro de Kalman
kalman = cv2.KalmanFilter(4, 2)  # 4 variáveis de estado (x, y, dx, dy), 2 observáveis (x, y)
kalman.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
kalman.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
kalman.processNoiseCov = np.eye(4, dtype=np.float32) * 0.03

# Captura de vídeo
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Converte para HSV e aplica filtro de cor (ajuste para sua necessidade)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (30, 150, 50), (50, 255, 255))  # Exemplo: detecta objetos verdes
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Pega o maior contorno detectado
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        cx, cy = x + w // 2, y + h // 2  # Centro do objeto

        # Atualiza o Filtro de Kalman com a medição atual
        measured = np.array([[np.float32(cx)], [np.float32(cy)]])
        kalman.correct(measured)

        # Faz a predição da próxima posição
        predicted = kalman.predict()
        px, py = int(predicted[0]), int(predicted[1])

        # Desenha as trajetórias no frame
        cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)  # Observado (verde)
        cv2.circle(frame, (px, py), 10, (0, 0, 255), 2)   # Predito (vermelho)

    cv2.imshow("Filtro de Kalman - Rastreamento", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()