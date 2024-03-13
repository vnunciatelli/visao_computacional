import cv2
import numpy as np
import time
import requests
import datetime
import hashlib

# Inicializar a webcam
cap = cv2.VideoCapture(0)

# URL da API do primeiro código
api_url = 'https://boe-python.eletromidia.com.br/vision/headcount/put'

# Carregar o modelo YOLO pré-treinado
net = cv2.dnn.readNet(r'C:\Users\ronaldo.pereira\Documents\2024\01-visao-computacional\head_counting\yolov4.weights', 
                      r'C:\Users\ronaldo.pereira\Documents\2024\01-visao-computacional\head_counting\yolov4.cfg')

# Carregar as classes de objetos
with open(r"C:\Users\ronaldo.pereira\Documents\2024\01-visao-computacional\head_counting\coco.names", "r") as f:
    classes = f.read().strip().split("\n")

# Variáveis para controlar o tempo
start_time = time.time()
interval_seconds = 30

# Variáveis para armazenar informações de pessoas detectadas
detected_people = set()
total_unique_people = 0

while True:
    # Iniciar contador de tempo para medir o tempo de processamento de cada loop
    loop_start_time = time.time()

    # Ler o frame da webcam
    ret, frame = cap.read()

    # Redimensionar o frame para o tamanho esperado pelo modelo YOLOv4 (608x608)
    blob = cv2.dnn.blobFromImage(frame, 1/255, (160, 160), (0, 0, 0), swapRB=True, crop=False)

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

            if confidence > 0.7 and class_id == 0:  # Se for uma pessoa com confiança maior que 0.7
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

    # Aplicar supressão de não-máximos para remover bounding boxes sobrepostos
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    # Atualizar o conjunto de pessoas detectadas
    detected_people.clear()
    for i in range(len(boxes)):
        if i in indexes:
            detected_people.add(tuple(boxes[i]))

    # Desenhar bounding boxes na imagem original
    for box in detected_people:
        x, y, w, h = box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Contar o número de pessoas únicas
    total_unique_people = len(detected_people)

    # Verificar se passaram 30 segundos e fazer a chamada à API
    if time.time() - start_time >= interval_seconds:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'[{current_time}] Após {interval_seconds} segundos, foram detectadas {total_unique_people} pessoas.')

        # Gerar hash MD5 da data e hora atual
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hash_md5 = hashlib.md5()
        hash_md5.update(current_datetime.encode('utf-8'))
        md5_hash = hash_md5.hexdigest()

        # Fazer a chamada à API com os dados relevantes
        payload = {
            'csrf': md5_hash,
            'qtd_person': total_unique_people,
            'datahora': current_datetime,
            'artifact': 'face'
        }
        response = requests.post(api_url, data=payload)
        if response.status_code == 200:
            print("Dados enviados com sucesso para a API.")
        else:
            print("Erro ao enviar dados para a API.")
            print("HTTP response:", response.status_code)

        # Reiniciar o contador de tempo
        start_time = time.time()

    # Exibir o número total de pessoas únicas detectadas na tela
    cv2.putText(frame, f'Pessoas Detectadas: {total_unique_people}', (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Exibir o frame
    cv2.imshow('YOLOv4 + Face Detection', frame)

    # Atraso para reduzir carga de processamento
    time.sleep(0.001)

    # Sair do Loop quando a tecla 'q' for pressionada
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar os recursos
cap.release()
cv2.destroyAllWindows()