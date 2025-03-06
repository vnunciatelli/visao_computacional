# Importando as bibliotecas
import cv2
import torch
import time
import math
import numpy as np
from sort import Sort  # Importar o rastreador SORT

# Carregar o modelo YOLOv5 pré-treinado
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # 'yolov5s' é o modelo pequeno

# Verificar se a GPU está disponível
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = model.to(device)  # Mover o modelo para a GPU

# Definir o limiar de confiança
model.conf = 0.7  # Ajustar o limiar de confiança (0 a 1)

# Video capture from camera (1 for external camera)
video = cv2.VideoCapture(1)

# Constant Declaration
WIDTH = 1280
HEIGHT = 720
PPM = 50  # Pixels por metro (ajuste conforme necessário)
MIN_DISTANCE = 5  # Distância mínima em pixels para considerar movimento

# Função para calcular a velocidade
def estimateSpeed(location1, location2, fps):
    d_pixels = math.sqrt(math.pow(location2[0] - location1[0], 2) + math.pow(location2[1] - location1[1], 2))
    d_meters = d_pixels / PPM
    speed = d_meters * fps * 3.6  # Conversão para km/h
    return speed

# Inicializar o rastreador SORT
tracker = Sort(min_hits=3, iou_threshold=0.3)  # Ajustar parâmetros do SORT

# Dicionários para rastreamento
carLocations = {}  # Armazenar as posições dos carros
speed = {}  # Armazenar as velocidades dos carros

# Configuração do vídeo de saída (opcional)
out = cv2.VideoWriter('outTraffic.avi', cv2.VideoWriter_fourcc('X','V','I','D'), 10, (WIDTH, HEIGHT))

while True:
    start_time = time.time()
    rc, image = video.read()
    if not rc:  # Se não conseguir capturar o frame, saia do loop
        break

    # Redimensionar o frame para melhorar o desempenho
    resized_image = cv2.resize(image, (640, 360))  # Reduzir para 640x360

    # Converter o frame para RGB (YOLO espera imagens em RGB)
    frame_rgb = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)

    # Passar o frame pelo modelo YOLO
    results = model(frame_rgb)

    # Filtrar detecções para carros (classe 2 no YOLO)
    detections = results.xyxy[0].numpy()
    car_detections = [det for det in detections if int(det[5]) == 2]  # Classe 2 é 'carro'

    # Calcular o fator de escala
    scale_x = image.shape[1] / 640  # Fator de escala na direção X
    scale_y = image.shape[0] / 360  # Fator de escala na direção Y

    # Preparar as detecções para o SORT
    dets = []
    for det in car_detections:
        x1, y1, x2, y2, conf, cls = det
        # Ajustar as coordenadas para a resolução original
        dets.append([x1 * scale_x, y1 * scale_y, x2 * scale_x, y2 * scale_y, conf])

    # Atualizar o rastreador SORT
    tracks = tracker.update(np.array(dets))

    # Processar os rastreamentos
    for track in tracks:
        x1, y1, x2, y2, track_id = track
        car_id = int(track_id)  # ID único para cada carro

        # Atualizar posições dos carros
        if car_id not in carLocations:
            carLocations[car_id] = []
        carLocations[car_id].append((x1, y1, x2, y2))

        # Calcular velocidade se houver posições anteriores
        if len(carLocations[car_id]) > 1:
            prev_x1, prev_y1, prev_x2, prev_y2 = carLocations[car_id][-2]
            d_pixels = math.sqrt(math.pow(x1 - prev_x1, 2) + math.pow(y1 - prev_y1, 2))

            if d_pixels > MIN_DISTANCE:
                speed[car_id] = estimateSpeed((prev_x1, prev_y1), (x1, y1), video.get(cv2.CAP_PROP_FPS))
            else:
                speed[car_id] = 0  # Carro parado

        # Desenhar bounding box e velocidade
        cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        if car_id in speed and speed[car_id] is not None:
            cv2.putText(image, f"{speed[car_id]:.2f} km/h", (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

    # Exibir o frame resultante
    cv2.imshow('Result', image)

    # Salvar o frame no vídeo de saída (opcional)
    out.write(image)

    # Parar o loop se a tecla 'ESC' for pressionada
    if cv2.waitKey(1) == 27:
        break

    # Calcular FPS
    end_time = time.time()
    fps = 1.0 / (end_time - start_time)

# Liberar recursos
cv2.destroyAllWindows()
out.release()
video.release()