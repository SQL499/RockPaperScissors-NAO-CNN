# -*- coding: utf-8 -*-
import cv2
import socket
import pickle
import struct

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8000

cap = cv2.VideoCapture(0)

while True:
    ret, img = cap.read()
    if not ret:
        break

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    data = pickle.dumps(img, protocol=2)
    data_len = struct.pack("!I", len(data))

    sock = socket.socket()
    sock.connect((SERVER_IP, SERVER_PORT))
    sock.sendall(data_len)
    sock.sendall(data)

    sock.shutdown(socket.SHUT_WR)
    pred = sock.recv(1024)
    sock.close()

    print("Predicción:", pred)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
