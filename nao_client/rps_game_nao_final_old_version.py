# -*- coding: utf-8 -*-
import socket
import pickle
import numpy as np
import cv2
from naoqi import ALProxy
import time
import struct

# =============================================================
# CONFIGURACIÓN
# =============================================================
ROBOT_IP = "127.0.0.1"      # Simulador NAO (Choregraphe)
# Cuando uses NAO real, cambia a su IP real, ej. "192.168.1.50"

PORT = 9559

SERVER_IP = "127.0.0.1"     # Servidor Python 3 en tu misma PC
SERVER_PORT = 8000

RESOLUTION = 2     # 640x480
COLOR_SPACE = 11    # RGB
FPS = 6

LABELS = {"0": "piedra", "1": "papel", "2": "tijeras"}


# =============================================================
# CAPTURA DE IMAGEN
# =============================================================
def capture_image(video_proxy):
    """Captura un frame RGB del NAO/simulador y devuelve un np.array RGB."""
    try:
        nameId = video_proxy.subscribeCamera(
            "rps_cam",
            0,  # cámara frontal
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
        print("ERROR capturando imagen del NAO:", e)
        return None


# =============================================================
# ENVÍO AL SERVIDOR PYTHON 3 (con FRAMING)
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
        0: 2,  # piedra vence tijeras
        1: 0,  # papel vence piedra
        2: 1   # tijeras vence papel
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

    # ======================
    # TURNO JUGADOR 1
    # ======================
    tts.say("Jugador uno, muestra tu mano.")
    time.sleep(2)

    img1 = capture_image(video)
    if img1 is None:
        tts.say("Hubo un error capturando la imagen del jugador uno.")
        return

    pred1 = send_to_server(img1)
    if pred1 not in LABELS:
        tts.say("No pude reconocer la mano del jugador uno.")
        return

    print("J1:", LABELS[pred1])
    tts.say("Jugador uno eligió " + LABELS[pred1])

    # ======================
    # TURNO JUGADOR 2
    # ======================
    tts.say("Jugador dos, muestra tu mano.")
    time.sleep(2)

    img2 = capture_image(video)
    if img2 is None:
        tts.say("Hubo un error capturando la imagen del jugador dos.")
        return

    pred2 = send_to_server(img2)
    if pred2 not in LABELS:
        tts.say("No pude reconocer la mano del jugador dos.")
        return

    print("J2:", LABELS[pred2])
    tts.say("Jugador dos eligió " + LABELS[pred2])

    # ======================
    # DECISIÓN FINAL
    # ======================
    ganador = decide_winner(pred1, pred2)

    if ganador == "empate":
        tts.say("Es un empate.")
    elif ganador == "j1":
        tts.say("Gana el jugador uno con " + LABELS[pred1])
    else:
        tts.say("Gana el jugador dos con " + LABELS[pred2])

    print("Resultado:", ganador)


# =============================================================
if __name__ == "__main__":
    main()
