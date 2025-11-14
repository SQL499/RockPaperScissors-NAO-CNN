# -*- coding: utf-8 -*-
import socket
import pickle
import cv2
import numpy as np
import struct

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8000

print("Probando lectura de imagen...")

# IMPORTANTE: usa una imagen local llamada test.jpg en la misma carpeta
img = cv2.imread("dataset/test/paper/paper_d1_test_164.png")

if img is None:
    print("ERROR: test.jpg no existe o no pudo ser cargado.")
    raise SystemExit

print("Tipo:", type(img))
print("Shape:", img.shape)

# Convertir a RGB
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Serializar imagen
data = pickle.dumps(img, protocol=2)
data_length = struct.pack("!I", len(data))  # 4 bytes big-endian

print("Tamaño del paquete:", len(data))

# Conectar al servidor
sock = socket.socket()
sock.connect((SERVER_IP, SERVER_PORT))

# Enviar tamaño + datos
sock.sendall(data_length)
sock.sendall(data)

sock.shutdown(socket.SHUT_WR)

# Recibir resultado
result = sock.recv(1024)
sock.close()

print("Predicción:", result)
