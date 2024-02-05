from flask import Flask, render_template, Response, jsonify
from flask_bootstrap import Bootstrap
import cv2
import dlib
import time
from datetime import timedelta

app = Flask(__name__)
Bootstrap(app)

# Variável de sensibilidade para o reconhecimento facial (ajustável conforme necessário)
sensitivity_factor = 2

# Inicializa o detector de faces do dlib com a sensibilidade configurada
detector = dlib.get_frontal_face_detector()

# Dicionário para armazenar informações sobre cada pessoa
people_info = {}

# Inicializa a câmera
cap = cv2.VideoCapture(0)

def generate_frames():
    global people_info

    while True:
        # Lê o frame da câmera
        ret, frame = cap.read()

        # Converte o frame para escala de cinza
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detecta faces no frame com a sensibilidade configurada
        faces = detector(gray, sensitivity_factor)

        # Atualiza o contador de pessoas
        total_people_count = len(people_info)

        for face in faces:
            x, y, w, h = face.left(), face.top(), face.width(), face.height()

            # Adiciona um retângulo verde ao redor da face detectada
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Obtém o ID da pessoa com base nas coordenadas da face
            person_id = f"{x}_{y}"

            # Se a pessoa não estiver no dicionário, adiciona com o tempo atual
            if person_id not in people_info:
                people_info[person_id] = {"start_time": time.time(), "looking_at_camera": True}

            # Calcula o tempo que a pessoa está olhando para a câmera
            elapsed_time = time.time() - people_info[person_id]["start_time"]

            # Atualiza a informação sobre o tempo que a pessoa está olhando para a câmera
            people_info[person_id]["looking_at_camera"] = True

            # Exibe o ID da pessoa e o tempo que está olhando para a câmera
            cv2.putText(frame, f"ID: {person_id} - Tempo: {str(timedelta(seconds=round(elapsed_time)))}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # Verifica pessoas que não estão olhando para a câmera
        for person_id, info in people_info.items():
            if info["looking_at_camera"]:
                info["looking_at_camera"] = False
            else:
                # Contabiliza pessoas que não estão olhando para a câmera
                print(f"Pessoa {person_id} não está olhando para a câmera! Tempo total: {str(timedelta(seconds=round(elapsed_time)))}")
                # Pode-se adicionar mais lógica aqui, como salvar os resultados em um arquivo, banco de dados, etc.

        # Converte o frame para JPEG
        _, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/')
def index():
    not_looking_count = sum(1 for info in people_info.values() if not info["looking_at_camera"])
    return render_template('index.html', total_people_count=len(people_info), not_looking_count=not_looking_count)

@app.route('/get_people_count')
def get_people_count():
    unique_people = set([info["person_id"] for info in people_info.values()])
    return jsonify({'total_people_count': len(unique_people)})

@app.route('/get_not_looking_count')
def get_not_looking_count():
    not_looking_count = sum(1 for info in people_info.values() if not info["looking_at_camera"])
    return jsonify({'not_looking_count': not_looking_count})

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)