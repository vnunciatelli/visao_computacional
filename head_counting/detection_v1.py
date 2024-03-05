import requests
import json
import mediapipe as mp
import cv2
import time
import datetime

# Inicialização do módulo de detecção facial e de cabeça
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)
holistic = mp.solutions.holistic.Holistic()

# Inicializar a webcam e variáveis
cap = cv2.VideoCapture(0)
detected_heads = {}  # Dicionário para armazenar informações de cada cabeça detectada
next_head_id = 1     # Próximo ID a ser atribuído a uma nova cabeça
total_unique_heads = 0  # Variável para rastrear o número total de IDs únicos atribuídos

# Variáveis para controlar o tempo
start_time = time.time()
interval_minutes = 0.20

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
                prev_bbox = head_info['bbox']
                x, y, w, h = bbox
                prev_x, prev_y, prev_w, prev_h = prev_bbox
                if (prev_x - w / 2) < x < (prev_x + prev_w + w / 2) and \
                   (prev_y - h / 2) < y < (prev_y + prev_h + h / 2):
                    head_id = id
                    head_info['bbox'] = bbox
                    break

            if head_id is None:
                # Verificar se há características faciais específicas para distinguir entre cabeças
                results_holistic = holistic.process(rgb_frame)
                if results_holistic.face_landmarks:
                    # Se houver landmarks faciais detectados, consideramos uma nova cabeça
                    head_id = next_head_id
                    detected_heads[head_id] = {'bbox': bbox}
                    next_head_id += 1
                    total_unique_heads += 1

            # Desenhar um retângulo ao redor da cabeça
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (0, 255, 0), 2)

            # Exibir o número da cabeça
            cx, cy = bbox[0] + bbox[2] // 2, bbox[1] + bbox[3] // 2
            cv2.putText(frame, f'ID: {head_id}', (cx - 10, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Exibir o número total de IDs únicos na tela
    cv2.putText(frame, f'Pessoas Detectadas: {total_unique_heads}', (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Exibir o frame
    cv2.imshow('Face and Head Detection', frame)

    # Verificar se passaram 5 minutos e exibir a hora em tempo real
    if time.time() - start_time >= interval_minutes * 60:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'[{current_time}] Após {interval_minutes} minutos, foram detectadas {total_unique_heads} pessoas.')
        print(total_unique_heads)
        
        # Fazer uma solicitação POST à sua API local
        dados = {'total_pessoas': total_unique_heads,
                 'data_hora': str(current_time),
                 'uid': detected_heads  # Enviar o dicionário de cabeças detectadas para a API
                 }
        print(dados)
        url = 'http://localhost/vision/main.php'
        response = requests.post(url, data=dados)
        if response.status_code == 200:
            print("Dados enviados com sucesso para a API.")
        else:
            print("Erro ao enviar dados para a API.")
        
        print(response.text)
        print('HTTP response:',response.status_code)
        
        start_time = time.time()  # Reiniciar o tempo

    # Sair do loop quando a tecla 'q' for pressionada
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar os recursos
cap.release()
cv2.destroyAllWindows()