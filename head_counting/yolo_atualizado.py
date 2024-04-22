#!/usr/bin/python
import fcntl
import socket
import struct
import cv2
import numpy as np
import time
import requests
import datetime
import hashlib

# Inicializar a webcam
cap = cv2.VideoCapture(0)

# Verificar se a webcam foi aberta corretamente
if not cap.isOpened():
    print("Erro ao abrir a webcam.")
    exit()

# URL da API do primeiro código
api_url = 'https://boe-python.eletromidia.com.br/vision/headcount/put'

# Carregar o modelo YOLO pré-treinado
net = cv2.dnn.readNet(r'/home/elemidia/Documentos/Visao_Computacional/yolov4.weights', 
                      r'/home/elemidia/Documentos/Visao_Computacional/yolov4.cfg')

# Carregar as classes de objetos
with open(r'/home/elemidia/Documentos/Visao_Computacional/coco.names', "r") as f:
    classes = f.read().strip().split("\n")

# Variáveis para controlar o tempo
start_time = time.time()
interval_seconds = 30

# Variáveis para armazenar informações de pessoas detectadas
detected_people = set()
total_unique_people = 0

# Função para calcular a distância entre duas coordenadas
def distance(coord1, coord2):
    x1, y1, _, _ = coord1
    x2, y2, _, _ = coord2
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

# Função para contar pessoas únicas
def count_unique_people(detected_people):
    unique_people = set()
    for person1 in detected_people:
        unique = True
        for person2 in unique_people:
            if distance(person1, person2) < 50:
                unique = False
                break
        if unique:
            unique_people.add(person1)
    return len(unique_people)

# Definir o tamanho da janela
cv2.namedWindow('YOLOv4 + Face Detection', cv2.WINDOW_NORMAL)
cv2.resizeWindow('YOLOv4 + Face Detection', 600, 400)


while True:
    # Ler o frame da webcam
    ret, frame = cap.read()

    # Verificar se a leitura do frame foi bem-sucedida
    if not ret:
        print("Erro ao ler o frame da webcam.")
        break

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

    # Contar o número de pessoas únicas
    total_unique_people = count_unique_people(detected_people)

    # Verificar se passaram 30 segundos e fazer a chamada à API
    if time.time() - start_time >= interval_seconds:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'[{current_time}] Após {interval_seconds} segundos, foram detectadas {total_unique_people} pessoas.')

        # Gerar hash MD5 da data e hora atual
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hash_md5 = hashlib.md5()
        hash_md5.update(current_datetime.encode('utf-8'))
        md5_hash = hash_md5.hexdigest()

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', bytes('enp1s0', 'utf-8')[:15]))
        nuc_mac = ''.join('%02x' % b for b in info[18:24])


        

        # Fazer a chamada à API com os dados relevantes
        payload = {
            'csrf': md5_hash,
            'qtd_person': total_unique_people,
            'datahora': current_datetime,
            'artifact': 'face',
            'nucmac' : nuc_mac
        }
        response = requests.post(api_url, data=payload)
        if response.status_code == 200:
            print("Dados enviados com sucesso para a API.")
        else:
            print("Erro ao enviar dados para a API.")
            print("HTTP response:", response.status_code)

        # Reiniciar o contador de tempo
        start_time = time.time()

    # Desenhar bounding boxes na imagem original
    for box in detected_people:
        x, y, w, h = box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Exibir o número total de pessoas únicas detectadas na tela
    cv2.putText(frame, f'Pessoas Detectadas: {total_unique_people}', (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Exibir o frame
    cv2.imshow('YOLOv4 + Face Detection', frame)
     
    # Atraso para reduzir carga de processamento
    time.sleep(0.001)  # Ajuste o valor aqui para definir a frequência de detecção

    # Sair do Loop quando a tecla 'q' for pressionada
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar os recursos
cap.release()
cv2.destroyAllWindows()