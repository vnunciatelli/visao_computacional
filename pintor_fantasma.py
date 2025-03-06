import cv2
import numpy as np
import torch
from segment_anything import sam_model_registry, SamPredictor
from tensorflow.keras.applications import vgg19
from tensorflow.keras.models import Model
from tensorflow.keras import backend as K

# Carregar modelo SAM para segmentação
sam = sam_model_registry["vit_b"]("sam_vit_b.pth")  # Certifique-se de ter o modelo baixado
sam.to("cuda" if torch.cuda.is_available() else "cpu")
predictor = SamPredictor(sam)

# Função para capturar imagem da webcam
def capture_image():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    return frame if ret else None

# Função para segmentar o objeto

def segment_object(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    predictor.set_image(image_rgb)
    masks, _, _ = predictor.predict()
    return masks[0] if len(masks) > 0 else None

# Função de Transferência de Estilo Neural
def preprocess_image(image):
    image = cv2.resize(image, (224, 224))
    image = np.expand_dims(image, axis=0)
    image = vgg19.preprocess_input(image)
    return image

def deprocess_image(image):
    image = image.reshape((224, 224, 3))
    image[:, :, 0] += 103.939
    image[:, :, 1] += 116.779
    image[:, :, 2] += 123.68
    image = np.clip(image, 0, 255).astype('uint8')
    return image

def neural_style_transfer(content_image, style_image, iterations=10):
    model = vgg19.VGG19(weights='imagenet', include_top=False)
    layers = dict([(layer.name, layer.output) for layer in model.layers])
    content_layer = 'block5_conv2'
    style_layers = ['block1_conv1', 'block2_conv1', 'block3_conv1', 'block4_conv1', 'block5_conv1']
    
    def gram_matrix(x):
        features = K.batch_flatten(K.permute_dimensions(x, (2, 0, 1)))
        return K.dot(features, K.transpose(features))
    
    def style_loss(style, combination):
        return K.sum(K.square(gram_matrix(style) - gram_matrix(combination)))
    
    content_image = preprocess_image(content_image)
    style_image = preprocess_image(style_image)
    combination_image = K.variable(content_image)
    input_tensor = K.concatenate([content_image, style_image, combination_image], axis=0)
    
    model = Model(inputs=model.input, outputs=[layers[content_layer]] + [layers[l] for l in style_layers])
    outputs = model(input_tensor)
    
    loss = K.variable(0.0)
    loss += K.sum(K.square(outputs[0] - outputs[2]))
    for output in outputs[1:]:
        loss += style_loss(output[1], output[2])
    
    grads = K.gradients(loss, combination_image)[0]
    iterate = K.function([combination_image], [loss, grads])
    
    x = content_image.copy()
    for i in range(iterations):
        loss_value, grad_values = iterate([x])
        x -= grad_values * 0.01
    
    return deprocess_image(x)

# Fluxo do programa
image = capture_image()
if image is not None:
    mask = segment_object(image)
    if mask is not None:
        stylized_image = neural_style_transfer(image, cv2.imread("style.jpg"))
        cv2.imshow("Estilizado", stylized_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Objeto não identificado.")
else:
    print("Erro ao capturar imagem.")
