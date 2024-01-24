import cv2
import mediapipe as mp
import time

# Inicializar o módulo de detecção facial do MediaPipe
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
face_detection = mp_face_detection.FaceDetection()

# Inicializar a webcam
cap = cv2.VideoCapture(0)

# Inicializar variáveis
face_timers = {}  # Dicionário para rastrear os tempos decorridos para cada face
start_time = time.time()  # Variável para rastrear o tempo total

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
        for face_id, detection in enumerate(results.detections):
            bboxC = detection.location_data.relative_bounding_box
            ih, iw, _ = frame.shape
            bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                   int(bboxC.width * iw), int(bboxC.height * ih)

            # Iniciar o cronômetro para a face se for nova
            if face_id not in face_timers:
                face_timers[face_id] = time.time()

            # Calcular o tempo decorrido para a face atual
            elapsed_time = time.time() - face_timers[face_id]

            # Converter o tempo decorrido em horas, minutos e segundos
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Calcular o centro e raio para o círculo
            cx, cy = bbox[0] + bbox[2] // 2, bbox[1] + bbox[3] // 2
            radius = max(bbox[2] // 2, bbox[3] // 2)

            # Desenhar um círculo ao redor da face
            cv2.circle(frame, (cx, cy), radius, (0, 255, 0), 2)

            # Exibir o número da face acima do círculo
            face_number_str = str(face_id + 1)
            cv2.putText(frame, face_number_str, (cx - radius, cy - radius - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Exibir o tempo decorrido próximo ao círculo
            time_str = f'Tempo: {int(hours)}h {int(minutes)}m {int(seconds)}s'
            cv2.putText(frame, time_str, (cx - radius, cy + radius + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

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
