import cv2
import time
import math
import numpy as np
from sort import Sort
from datetime import datetime
from ultralytics import YOLO  # YOLOv8

# Carregar o modelo YOLOv8 para veículos
model_vehicle = YOLO('yolov8n.pt')  # Modelo nano (mais leve)

# Carregar o modelo YOLOv8 para placas
model_plate = YOLO(r'C:\Users\ronaldo.pereira\Documents\Deteccao Velocidade Yolo\license_plate_detector.pt') 

# Configuração da câmera
video = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # Usar DirectShow no Windows
WIDTH, HEIGHT = 640, 360
video.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

# Parâmetros de velocidade
PPM = 50  # Pixels por metro
MIN_DISTANCE = 5  # Distância mínima para considerar movimento
MAX_SPEED = 120  # Velocidade máxima (km/h)

# Inicializar rastreador SORT
tracker = Sort(max_age=10, min_hits=3, iou_threshold=0.3)

# Dicionários para armazenar dados
carLocations = {}
speed = {}
vehicle_classes = {}
license_plates = {}  # Armazenar placas detectadas

# Mapeamento das classes para nomes de veículos
class_names = {
    2: "Carro",
    3: "Moto",
    5: "Onibus",
    7: "Caminhao"
}

# Função para suavização exponencial da velocidade
def exponential_smooth_speed(car_id, current_speed, alpha=0.2):
    if car_id not in speed:
        speed[car_id] = current_speed
    else:
        speed[car_id] = alpha * current_speed + (1 - alpha) * speed[car_id]
    return speed[car_id]

# Função para detectar e ler placas
def detect_license_plate(image, vehicle_bbox):
    x1, y1, x2, y2 = vehicle_bbox
    vehicle_roi = image[int(y1):int(y2), int(x1):int(x2)]
    
    # Detectar placas dentro do ROI do veículo
    results = model_plate(vehicle_roi)
    plates = results[0].boxes.data.cpu().numpy()
    
    for plate in plates:
        x1p, y1p, x2p, y2p, conf, cls = plate
        if conf > 0.5:  # Limiar de confiança para placas
            plate_roi = vehicle_roi[int(y1p):int(y2p), int(x1p):int(x2p)]
            
            # Processar a placa com EasyOCR
            # plate_text = reader.readtext(plate_roi, detail=0, paragraph=True)
            # if plate_text:
            #     return plate_text[0].upper()  # Retornar a placa formatada
    
    return None

# Loop principal
while True:
    start_time = time.time()
    rc, image = video.read()
    if not rc:
        break

    # Redimensionar o frame para melhorar o desempenho
    resized_image = cv2.resize(image, (WIDTH, HEIGHT))

    # Detectar veículos com YOLOv8
    results = model_vehicle(resized_image)
    detections = results[0].boxes.data.cpu().numpy()

    # Filtrar detecções para carros, motos, ônibus e caminhões
    vehicle_detections = [det for det in detections if int(det[5]) in [2, 3, 5, 7]]

    # Rastrear veículos
    dets = [[x1, y1, x2, y2, conf] for x1, y1, x2, y2, conf, cls in vehicle_detections]
    tracks = tracker.update(np.array(dets))

    # Processar rastreamentos
    for track in tracks:
        x1, y1, x2, y2, track_id = track
        car_id = int(track_id)

        # Atualizar posições e velocidade
        carLocations.setdefault(car_id, []).append((x1, y1, x2, y2))
        
        if len(carLocations[car_id]) > 1:
            prev_x1, prev_y1, _, _ = carLocations[car_id][-2]
            current_speed = math.sqrt((x1 - prev_x1)**2 + (y1 - prev_y1)**2) / PPM * video.get(cv2.CAP_PROP_FPS) * 3.6
            smoothed_speed = exponential_smooth_speed(car_id, current_speed)
            speed[car_id] = min(smoothed_speed, MAX_SPEED)

            # Detectar placa apenas uma vez por veículo
            if car_id not in license_plates:
                license_plates[car_id] = detect_license_plate(resized_image, (x1, y1, x2, y2))

        # Desenhar informações
        vehicle_type = class_names.get(vehicle_classes.get(car_id, 2), "Carro")
        label = f"{vehicle_type} {speed.get(car_id, 0):.1f}"
        
        if car_id in license_plates and license_plates[car_id]:
            plate = license_plates[car_id]
            label += f" - Placa: {plate}"
            color = (0, 0, 255)  # Vermelho para veículos com placa detectada
        else:
            color = (0, 255, 0)  # Verde para veículos sem placa detectada
        
        # Desenhar bounding box e texto
        cv2.rectangle(resized_image, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
        cv2.putText(resized_image, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Exibir frame
    cv2.imshow('Monitoramento', resized_image)
    if cv2.waitKey(1) == 27:
        break

# Liberar recursos
cv2.destroyAllWindows()
video.release()