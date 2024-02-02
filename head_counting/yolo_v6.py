import cv2
import numpy as np
import time
import pandas as pd

# Inicializar o classificador de rostos Haar Cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Carregar o modelo YOLO pré-treinado
net = cv2.dnn.readNet(r'C:\Users\ronaldo.pereira\Documents\2024\01-visao-computacional\head_counting\yolov4.weights', r'C:\Users\ronaldo.pereira\Documents\2024\01-visao-computacional\head_counting\yolov4.cfg')

# Carregar as classes de objetos
with open(r"C:\Users\ronaldo.pereira\Documents\2024\01-visao-computacional\head_counting\coco.names", "r") as f:
    classes = f.read().strip().split("\n")

# Inicializar o classificador de rostos Haar Cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Inicializar a webcam
cap = cv2.VideoCapture(0)

# Definir cor verde para todas as pessoas detectadas
green_color = (0, 255, 0)

# Variáveis para contar o número de pessoas detectadas
person_count = 0
detection_times_faces = {}
detection_times_objects = {}

while True:
    # Ler o frame da webcam
    ret, frame = cap.read()
    
    if not ret:
        break

    # Redimensionar o frame para o tamanho esperado pelo modelo YOLOv4 (608x608)
    blob = cv2.dnn.blobFromImage(frame, 1/255, (320, 320), (0, 0, 0), swapRB=True, crop=False)

    # Passar o blob pela rede neural YOLOv4
    net.setInput(blob)
    output_layers_names = net.getUnconnectedOutLayersNames()
    layer_outputs = net.forward(output_layers_names)

    boxes = []
    confidences = []
    class_ids = []

    # Processar as saídas da rede neural YOLOv4
    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5 and class_id == 0:  # Se for uma pessoa com confiança maior que 0.5
                # Obter as coordenadas do bounding box
                center_x = int(detection[0] * frame.shape[1])
                center_y = int(detection[1] * frame.shape[0])
                w = int(detection[2] * frame.shape[1])
                h = int(detection[3] * frame.shape[0])

                # Calcular os pontos de canto do bounding box
                x = int(center_x - w/2)
                y = int(center_y - h/2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

                # Atualizar o tempo de detecção para esta pessoa
                person_id = len(detection_times_objects) + 1
                if person_id not in detection_times_objects:
                    detection_times_objects[person_id] = {'start_time': time.time(), 'total_exposure': 0}
                else:
                    detection_times_objects[person_id]['total_exposure'] += time.time() - detection_times_objects[person_id]['last_detection_time']
                detection_times_objects[person_id]['last_detection_time'] = time.time()

    # Remover pessoas não detectadas há mais de 5 segundos
    current_time = time.time()
    outdated_ids = [person_id for person_id, detection_info in detection_times_objects.items()
                    if current_time - detection_info['last_detection_time'] > 5]
    for person_id in outdated_ids:
        del detection_times_objects[person_id]

    # Detectar rostos no frame usando Haar Cascade
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Desenhar retângulos ao redor dos rostos detectados e rastrear o tempo de exposição
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        # Calcular o ID da pessoa com base nas coordenadas do retângulo
        person_id = len(detection_times_faces) + 1

        # Rastrear o tempo de detecção para esta pessoa
        current_time = time.time()
        if person_id not in detection_times_faces:
            detection_times_faces[person_id] = {'start_time': current_time, 'total_exposure': 0}
        else:
            detection_times_faces[person_id]['total_exposure'] += current_time - detection_times_faces[person_id]['last_detection_time']
        detection_times_faces[person_id]['last_detection_time'] = current_time

        # Exibir o tempo ao lado do rosto
        elapsed_time = current_time - detection_times_faces[person_id]['start_time']
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        cv2.putText(frame, time_str, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Exibir o número de pessoas detectadas
    cv2.putText(frame, f"People Count: {len(faces)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Exibir o frame
    cv2.imshow('frame', frame)

    # Sair do loop quando a tecla 'q' for pressionada
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar os recursos
cap.release()
cv2.destroyAllWindows()

# Convertendo o dicionário para um DataFrame do pandas para rostos
df_faces = pd.DataFrame.from_dict(detection_times_faces, orient='index')

# Salvando o DataFrame em um arquivo CSV para rostos
df_faces.to_csv('detected_faces_data.csv', index_label='person_id_faces')

# Convertendo o dicionário para um DataFrame do pandas para objetos
df_objects = pd.DataFrame.from_dict(detection_times_objects, orient='index')

# Salvando o DataFrame em um arquivo CSV para objetos
df_objects.to_csv('detected_objects_data.csv', index_label='person_id_objects')

