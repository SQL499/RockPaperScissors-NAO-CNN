# Rock Paper Scissors – NAO Robot + CNN

Proyecto desarrollado como parte de la Práctica Calificada 3 (PC3) del curso Machine Learning (CC57). Implementa un sistema de visión artificial que permite al robot NAO reconocer jugadas del juego Piedra–Papel–Tijeras usando un modelo de Deep Learning ejecutado en un servidor externo.

## Arquitectura General

El sistema utiliza un enfoque cliente-servidor:

- **Robot NAO (Python 2.7):**
  - Captura imágenes mediante `ALVideoDevice`
  - Serializa las imágenes con `pickle` (protocol=2)
  - Envía las imágenes por socket TCP
  - Recibe la predicción del modelo y anuncia el resultado mediante TTS

- **Servidor de Inferencia (Python 3.x):**
  - Deserializa la imagen recibida
  - Preprocesa la imagen para MobileNetV3
  - Ejecuta el modelo CNN entrenado
  - Devuelve la clase predicha al NAO

- **Modelo CNN:**
  - Arquitectura: **MobileNetV3 Small**
  - Entrenado con un dataset fusionado de 3 repositorios de Kaggle
  - Clases: piedra (0), papel (1), tijeras (2)

## Tecnologías Utilizadas

### Robot NAO
- Python 2.7
- NAOqi SDK
- ALVideoDevice
- ALTextToSpeech

### Servidor
- Python 3.12
- TensorFlow 2.17
- OpenCV
- Sockets TCP
- MobileNetV3 Small

## Estructura del Proyecto

```
RockPaperScissors-NAO-CNN/
│
├── dataset/
│   ├── build_dataset.ipynb
│   └── links datasets.txt
│
├── modelo/
│   ├── Modelo CNN.ipynb
│   └── modelo_rps_mobilenetv3.keras
│
├── servidor/
│   └── servidor_tf_final.py
│
├── nao_client/
│   └── rps_game_nao_final.py
│
├── utils/
│   ├── test_webcam_to_server.py
│   └── test_client_py27_final.py
│
├── docs/
│   ├── diagrama de arquitectura.png
│   └── capturas_evidencia/
│
├── README.md
├── requirements.txt
└── .gitignore
```

## Cómo ejecutar el servidor

```bash
cd servidor/
python servidor_tf_final.py
```

## Cómo ejecutar el cliente NAO

```bash
cd nao_client/
python rps_game_nao_final.py
```

## Flujo del Juego

1. NAO anuncia el turno del Jugador 1  
2. Captura imagen → envía al servidor  
3. Recibe predicción → NAO la anuncia  
4. Repite con el Jugador 2  
5. Determina ganador usando reglas del juego  
6. NAO anuncia el resultado  

## Video de demostración

[(Click aqui para ver el video)
](https://youtu.be/U8wy0HrLsic )
