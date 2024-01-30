import cv2
import mediapipe as mp
import time
import numpy as np

# Inicialização do módulo de detecção facial e de cabeça
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)
head_detection = mp.solutions.holistic

# Carregar o modelo YOLO pré-treinado
net = cv2.dnn.readNet(r'C:\Users\ronaldo.pereira\Documents\2024\01-visao-computacional\head_counting\yolov3.weights', r'C:\Users\ronaldo.pereira\Documents\2024\01-visao-computacional\head_counting\yolov3.cfg')

# Carregar as classes de objetos
with open(r"C:\Users\ronaldo.pereira\Documents\2024\01-visao-computacional\head_counting\coco.names", "r") as f:
    classes = f.read().strip().split("\n")

# Obter as camadas de saída do modelo YOLO
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Inicializar a webcam e variáveis
cap = cv2.VideoCapture(0)
detected_heads = {}  # Dicionário para armazenar informações de cada cabeça detectada
head_timers = {}     # Dicionário para rastrear os tempos decorridos para cada cabeça
next_head_id = 1     # Próximo ID a ser atribuído a uma nova cabeça
total_unique_heads = 0  # Variável para rastrear o número total de IDs únicos atribuídos
max_inactive_time = 5  # Tempo máximo de inatividade (em segundos) antes de remover uma cabeça detectada

while True:
    # Ler o frame da webcam
    ret, frame = cap.read()

    # Converter o frame para RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Executar a detecção de rostos
    results = face_detection.process(rgb_frame)

    # Verificar se há detecções de rostos
    if results.detections:
        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            ih, iw, _ = frame.shape
            bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                   int(bboxC.width * iw), int(bboxC.height * ih)

            # Atualizar a posição e o tempo da cabeça detectada
            head_id = None
            for id, head_info in detected_heads.items():
                prev_bbox, prev_time = head_info['bbox'], head_info['time']
                x, y, w, h = bbox
                prev_x, prev_y, prev_w, prev_h = prev_bbox
                if (prev_x - w / 2) < x < (prev_x + prev_w + w / 2) and \
                   (prev_y - h / 2) < y < (prev_y + prev_h + h / 2) and \
                   (time.time() - prev_time) < max_inactive_time:
                    head_id = id
                    head_info['bbox'] = bbox
                    head_info['time'] = time.time()
                    break

            if head_id is None:
                head_id = next_head_id
                detected_heads[head_id] = {'bbox': bbox, 'time': time.time()}
                head_timers[head_id] = time.time()
                next_head_id += 1
                total_unique_heads += 1

            # Desenhar um retângulo ao redor da cabeça
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (0, 255, 0), 2)

            # Exibir o número da cabeça e o tempo decorrido
            cx, cy = bbox[0] + bbox[2] // 2, bbox[1] + bbox[3] // 2
            cv2.putText(frame, str(head_id), (cx - 10, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            elapsed_time = time.time() - head_timers[head_id]
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f'Time: {int(hours)}h {int(minutes)}m {int(seconds)}s'
            cv2.putText(frame, time_str, (cx - 10, cy + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Exibir o número total de IDs únicos na tela
            cv2.putText(frame, f'Total IDs: {total_unique_heads}', (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    # Redimensionar o frame para o tamanho esperado pelo modelo YOLO
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

    # Passar o blob pela rede neural YOLO
    net.setInput(blob)
    outs = net.forward(output_layers)

    # Processar as saídas da rede neural YOLO
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5:  # Confiança mínima para considerar a detecção válida
                # Obter as coordenadas do bounding box
                center_x = int(detection[0] * frame.shape[1])
                center_y = int(detection[1] * frame.shape[0])
                w = int(detection[2] * frame.shape[1])
                h = int(detection[3] * frame.shape[0])

                # Desenhar o bounding box e exibir a classe do objeto
                cv2.rectangle(frame, (center_x - w // 2, center_y - h // 2), (center_x + w // 2, center_y + h // 2), (0, 255, 0), 2)
                cv2.putText(frame, classes[class_id], (center_x, center_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Exibir o frame
    cv2.imshow('Face and Head Detection', frame)

    # Sair do loop quando a tecla 'q' for pressionada
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar os recursos
cap.release()
cv2.destroyAllWindows()