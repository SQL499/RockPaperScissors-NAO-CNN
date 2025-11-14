import socket
import pickle
import numpy as np
import tensorflow as tf
import cv2
import struct
from tensorflow.keras.applications.mobilenet_v3 import preprocess_input

print("SERVIDOR FINAL EJECUTANDOSE")

HOST = "0.0.0.0"
PORT = 8000
IMG_SIZE = 224

print("Cargando modelo...")
model = tf.keras.models.load_model("modelo_rps_mobilenetv3.keras")
print("Modelo cargado correctamente.")

def recv_exact(conn, size):
    """Recibir exactamente size bytes o devolver None."""
    data = b""
    while len(data) < size:
        chunk = conn.recv(size - len(data))
        if not chunk:
            return None
        data += chunk
    return data

def preprocess_image(img):
    # Resize
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    img = img.astype("float32")

    # MobileNetV3 preprocessing
    img = preprocess_input(img)

    # Expand dims -> shape (1, 224, 224, 3)
    img = np.expand_dims(img, axis=0)
    return img

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print("Servidor de inferencia escuchando en {}:{}".format(HOST, PORT))

while True:
    conn, addr = server.accept()
    print("Cliente conectado desde {}".format(addr))

    # ======= Recibir tamaño =======
    raw_size = recv_exact(conn, 4)
    if raw_size is None:
        print("Error: no se pudo leer el tamaño.")
        conn.close()
        continue

    data_size = struct.unpack("!I", raw_size)[0]

    # ======= Recibir datos completos =======
    data = recv_exact(conn, data_size)
    if data is None:
        print("Error: paquete incompleto.")
        conn.close()
        continue

    # ======= Deserializar =======
    try:
        img = pickle.loads(data, encoding='latin1')
    except Exception as e:
        print("Error al deserializar data:", e)
        conn.send(b"-1")
        conn.close()
        continue

    # ======= Inferencia =======
    img_processed = preprocess_image(img)
    pred = model.predict(img_processed)
    result = str(int(np.argmax(pred)))

    print("Predicción enviada:", result)
    conn.send(result.encode())
    conn.close()
