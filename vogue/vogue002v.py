import cv2
import numpy as np
import time
import pandas as pd
from flask import Flask, render_template, Response

app = Flask(__name__)

# Carregar o modelo YOLO pré-treinado
net = cv2.dnn.readNet(r'C:\Users\nunci\ELETROMIDIA\visao_computacional\head_counting\yolov4.weights', r'C:\Users\nunci\ELETROMIDIA\visao_computacional\head_counting\yolov4.cfg')

# Carregar as classes de objetos
with open(r"C:\Users\nunci\ELETROMIDIA\visao_computacional\head_counting\coco.names", "r") as f:
    classes = f.read().strip().split("\n")

# Inicializar a webcam
cap = cv2.VideoCapture(0)

# Definir cor verde para todas as pessoas detectadas
green_color = (0, 255, 0)

# Variável para contar o número de pessoas detectadas
person_count = 0
detection_times = {}
start_time = None

def generate_frames():

    while True:
        # Ler o frame da webcam
        _, frame = cap.read()

        # Redimensionar o frame para o tamanho esperado pelo modelo YOLOv4 (608x608)
        blob = cv2.dnn.blobFromImage(frame, 1/255, (320, 320), (0, 0, 0), swapRB=True, crop=False)

        # Passar o blob pela rede neural YOLOv4
        net.setInput(blob)
        output_layers_names = net.getUnconnectedOutLayersNames()
        layer_outputs = net.forward(output_layers_names)
        global boxes
        boxes = []
        global confidences
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
                    global person_id
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
        global indexes
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
                    global total_exposure
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

        # Atualizar as variáveis no frontend
        app.updateInfo(len(indexes), f"Person: {confidences[i]:.2f}", f"{int(detection_time // 3600):02d}:{int((detection_time % 3600) // 60):02d}:{int(detection_time % 60):02d}")

        # Retornar o frame como JPEG
        _, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
        time.sleep(0.01)

# Adicione esta função no seu script Flask para atualizar as variáveis no frontend
        
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_info')
def update_info():
    people_count = len(indexes)
    person_info = f"Person: {confidences[len(indexes)]:.2f}" if indexes else "N/A"
    detection_time = f"{int(detection_time // 3600):02d}:{int((detection_time % 3600) // 60):02d}:{int(detection_time % 60):02d}" if indexes else "N/A"
    return {'people_count': people_count, 'person_info': person_info, 'detection_time': detection_time}

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)

# Liberar os recursos
cap.release()
cv2.destroyAllWindows()