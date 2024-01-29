import cv2
import mediapipe as mp
import time

# Inicialização do módulo de detecção facial
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.8)  # Ajuste este valor conforme necessário

# Inicializar a webcam e variáveis
cap = cv2.VideoCapture(0)
detected_faces = {}  # Dicionário para armazenar informações de cada face detectada
face_timers = {}     # Dicionário para rastrear os tempos decorridos para cada face
start_time = time.time()  # Variável para rastrear o tempo total
next_face_id = 1     # Próximo ID a ser atribuído a uma nova face

# Inicializar variável para rastrear a posição da face no frame anterior
prev_face_position = None

while True:
    # Ler o frame da webcam
    ret, frame = cap.read()

    # Converter o frame para RGB (MediaPipe usa RGB)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Executar a detecção facial
    results = face_detection.process(rgb_frame)

    # Verificar se há detecções
    if results.detections:
        # Rastrear cada face detectada
        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            ih, iw, _ = frame.shape
            bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                   int(bboxC.width * iw), int(bboxC.height * ih)

            # Calcular o centro e raio para o círculo
            cx, cy = bbox[0] + bbox[2] // 2, bbox[1] + bbox[3] // 2
            radius = max(bbox[2] // 2, bbox[3] // 2)

            # Desenhar um retângulo ao redor da face
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (0, 255, 0), 2)

            # Filtragem adicional baseada no movimento da face
            if prev_face_position is not None:
                prev_x, prev_y, _, _ = prev_face_position
                curr_x, curr_y, _, _ = bbox

                # Calcular a diferença entre as posições da face no frame atual e no frame anterior
                diff_x = abs(curr_x - prev_x)
                diff_y = abs(curr_y - prev_y)

                # Definir um limite para a quantidade de movimento permitido
                max_movement = 50  # Ajuste este valor conforme necessário

                # Verificar se a diferença excede o limite de movimento permitido
                if diff_x > max_movement or diff_y > max_movement:
                    # Descartar esta detecção como um falso positivo
                    continue

            # Atualizar a posição da face para o próximo frame
            prev_face_position = bbox

            # Verificar se uma face com coordenadas semelhantes já foi detectada
            face_id = None
            for id, face_info in detected_faces.items():
                if abs(face_info['bbox'][0] - bbox[0]) < 250 and abs(face_info['bbox'][1] - bbox[1]) < 250:
                    face_id = id
                    break

            # Se não houver uma face semelhante, atribuir um novo ID
            if face_id is None:
                face_id = next_face_id
                detected_faces[face_id] = {'bbox': bbox}
                face_timers[face_id] = time.time()
                next_face_id += 1

            # Calcular o tempo decorrido para a face atual
            elapsed_time = time.time() - face_timers[face_id]

            # Converter o tempo decorrido em horas, minutos e segundos
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Exibir o número da face acima do círculo
            cv2.putText(frame, str(face_id), (cx - radius, cy - radius - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Exibir o tempo decorrido próximo ao círculo
            time_str = f'Tempo: {int(hours)}h {int(minutes)}m {int(seconds)}s'
            cv2.putText(frame, time_str, (cx - radius, cy + radius + 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Exibir o frame
            cv2.imshow('Detecção Facial', frame)

            # Adicionar um pequeno atraso (20 milissegundos)
            cv2.waitKey(20)

            # Sair do loop quando a tecla 'q' for pressionada
            if cv2.waitKey(1) & 0xFF == ord('q'):
                 break

# Liberar os recursos
cap.release()
cv2.destroyAllWindows()

