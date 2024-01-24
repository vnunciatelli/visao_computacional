import cv2
import time

# Inicializar o detector de faces da OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Inicializar a webcam
cap = cv2.VideoCapture(0)

# Inicializar variáveis
start_times = {}  # Dicionário para armazenar os tempos de início associados a cada face

while True:
    # Ler o frame da webcam
    ret, frame = cap.read()

    # Converter o frame para escala de cinza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detectar faces no frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Rastrear cada face detectada
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        face_key = (x, y, w, h)  # Chave única para cada face
        if face_key not in start_times:
            start_times[face_key] = time.time()  # Iniciar o cronômetro se ainda não estiver em execução

        # Calcular o tempo decorrido
        elapsed_time = time.time() - start_times[face_key]

        # Exibir o tempo decorrido acima de cada face
        cv2.putText(frame, f'Tempo: {elapsed_time:.2f} segundos', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Exibir o frame
    cv2.imshow('Detecção Facial', frame)

    # Sair do loop quando a tecla 'q' for pressionada
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Exibir os tempos individuais quando o programa for encerrado
for face_key, start_time in start_times.items():
    elapsed_time = time.time() - start_time
    print(f'Tempo para a face {face_key}: {elapsed_time:.2f} segundos')

# Liberar os recursos
cap.release()
cv2.destroyAllWindows()
