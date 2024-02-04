import cv2
import numpy as np
import time
import pandas as pd


# Carregar o modelo YOLO pré-treinado
net = cv2.dnn.readNet(r'C:\Users\ronaldo.pereira\Documents\2024\01-visao-computacional\head_counting\yolov4.weights', r'C:\Users\ronaldo.pereira\Documents\2024\01-visao-computacional\head_counting\yolov4.cfg')

# Carregar as classes de objetos
with open(r"C:\Users\ronaldo.pereira\Documents\2024\01-visao-computacional\head_counting\coco.names", "r") as f:
    classes = f.read().strip().split("\n")

# Inicializar a webcam
cap = cv2.VideoCapture(0)

# Definir cor verde para todas as pessoas detectadas
green_color = (0, 255, 0)

# Variável para contar o número de pessoas detectadas
person_count = 0
detection_times = {}
start_time = None

while True:
    # Ler o frame da webcam
    _, frame = cap.read()

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
                person_id = len(detection_times) + 1
                if person_id not in detection_times:
                    detection_times[person_id] = {'start_time': time.time(), 'total_exposure': 0}
                else:
                    detection_times[person_id]['total_exposure'] += time.time() - detection_times[person_id]['last_detection_time']
                detection_times[person_id]['last_detection_time'] = time.time()

    # Remover pessoas não detectadas há mais de 5 segundos
    current_time = time.time()
    outdated_ids = [person_id for person_id, detection_info in detection_times.items()
                    if current_time - detection_info['last_detection_time'] > 5]
    for person_id in outdated_ids:
        del detection_times[person_id]

    # Aplicar supressão de não-máximos para remover bounding boxes sobrepostos
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    # Desenhar bounding boxes na imagem original
    font = cv2.FONT_HERSHEY_PLAIN

    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = f"Person: {confidences[i]:.2f}"

            # Calcular o tempo de detecção
            person_id = i + 1
            if person_id in detection_times:
                total_exposure = detection_times[person_id]['total_exposure']
                detection_time = time.time() - detection_times[person_id]['start_time']
                detection_times[person_id]['last_detection_time'] = time.time()
            else:
                total_exposure = 0
                detection_time = 0
                detection_times[person_id] = {'start_time': time.time(), 'total_exposure': 0, 'last_detection_time': time.time()}

            # Exibir o tempo de detecção na parte superior ao lado do nome da pessoa
            cv2.putText(frame, f"Time: {int(detection_time // 3600):02d}:{int((detection_time % 3600) // 60):02d}:{int(detection_time % 60):02d}", (x, y - 20), font, 1, green_color, 1)
            cv2.rectangle(frame, (x, y), (x + w, y + h), green_color, 2)
            cv2.putText(frame, label, (x, y - 5), font, 1, green_color, 1)

    # Exibir o número de pessoas detectadas
    cv2.putText(frame, f"People Count: {len(indexes)}", (10, 30), font, 1, (255, 255, 255), 1)

    # Exibir o frame
    cv2.imshow("YOLOv4 Detection", frame)

    # Sair do loop quando a tecla 'q' for pressionada
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar os recursos
cap.release()
cv2.destroyAllWindows()