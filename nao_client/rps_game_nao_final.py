# -*- coding: utf-8 -*-
import socket
import pickle
import numpy as np
import cv2
from naoqi import ALProxy
import time
import struct
import os
import datetime

# =============================================================
# CONFIGURACIÓN
# =============================================================
ROBOT_IP = "127.0.0.1"      # Simulador NAO (Choregraphe)
PORT = 9559

SERVER_IP = "127.0.0.1"     # Servidor Python 3 en tu PC
SERVER_PORT = 8000

RESOLUTION = 2              # 640x480
COLOR_SPACE = 11            # RGB
FPS = 6

LABELS = {"0": "piedra", "1": "papel", "2": "tijeras"}

# Crear carpeta de capturas si no existe
CAPTURE_DIR = "capturas_rps"
if not os.path.exists(CAPTURE_DIR):
    os.makedirs(CAPTURE_DIR)


# =============================================================
# FUNCIÓN PARA GUARDAR IMAGEN
# =============================================================
def save_image(img, player_id):
    """Guarda la imagen como PNG con timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = "{}/jugador_{}_{}.png".format(CAPTURE_DIR, player_id, timestamp)
    cv2.imwrite(filename, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    print("Imagen guardada:", filename)


# =============================================================
# CAPTURA DE IMAGEN DEL NAO
# =============================================================
def capture_image(video_proxy):
    """Captura un frame RGB del NAO/simulador y devuelve un np.array."""
    try:
        nameId = video_proxy.subscribeCamera(
            "rps_cam",
            0,
            RESOLUTION,
            COLOR_SPACE,
            FPS
        )

        frame = video_proxy.getImageRemote(nameId)
        video_proxy.unsubscribe(nameId)

        width, height = frame[0], frame[1]
        array = frame[6]

        img = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))
        return img

    except Exception as e:
        print("ERROR capturando imagen:", e)
        return None


# =============================================================
# ENVÍO AL SERVIDOR PYTHON 3 (framing)
# =============================================================
def send_to_server(img):
    """Envía la imagen al servidor Python 3 y devuelve la predicción."""
    try:
        data = pickle.dumps(img, protocol=2)
        data_len = struct.pack("!I", len(data))

        sock = socket.socket()
        sock.connect((SERVER_IP, SERVER_PORT))

        sock.sendall(data_len)
        sock.sendall(data)
        sock.shutdown(socket.SHUT_WR)

        result = sock.recv(1024)
        sock.close()

        return result.decode("utf-8")

    except Exception as e:
        print("ERROR enviando imagen al servidor:", e)
        return "-1"


# =============================================================
# LÓGICA DEL GANADOR
# =============================================================
def decide_winner(move1, move2):
    m1 = int(move1)
    m2 = int(move2)

    if m1 == m2:
        return "empate"

    rules = {
        0: 2,
        1: 0,
        2: 1
    }

    if rules[m1] == m2:
        return "j1"
    else:
        return "j2"


# =============================================================
# PROGRAMA PRINCIPAL
# =============================================================
def main():
    print("Conectando al NAO/simulador...")
    video = ALProxy("ALVideoDevice", ROBOT_IP, PORT)
    tts = ALProxy("ALTextToSpeech", ROBOT_IP, PORT)

    tts.say("Iniciando el juego de piedra papel o tijeras.")

    # ----------------------------
    # JUGADOR 1
    # ----------------------------
    tts.say("Jugador uno, muestra tu mano ahora.")
    time.sleep(3)  # Espera de 3 segundos

    img1 = capture_image(video)
    if img1 is None:
        tts.say("Error capturando la mano del jugador uno.")
        return

    save_image(img1, 1)

    pred1 = send_to_server(img1)
    if pred1 not in LABELS:
        tts.say("No pude reconocer la mano del jugador uno.")
        return

    tts.say("Jugador uno eligió " + LABELS[pred1])

    # ----------------------------
    # JUGADOR 2
    # ----------------------------
    tts.say("Jugador dos, muestra tu mano ahora.")
    time.sleep(3)  # Espera de 3 segundos

    img2 = capture_image(video)
    if img2 is None:
        tts.say("Error capturando la mano del jugador dos.")
        return

    save_image(img2, 2)

    pred2 = send_to_server(img2)
    if pred2 not in LABELS:
        tts.say("No pude reconocer la mano del jugador dos.")
        return

    tts.say("Jugador dos eligió " + LABELS[pred2])

    # ----------------------------
    # GANADOR
    # ----------------------------
    ganador = decide_winner(pred1, pred2)

    if ganador == "empate":
        tts.say("Es un empate.")
    elif ganador == "j1":
        tts.say("Gana el jugador uno con " + LABELS[pred1])
    else:
        tts.say("Gana el jugador dos con " + LABELS[pred2])

    print("GANADOR:", ganador)


# =============================================================
if __name__ == "__main__":
    main()
