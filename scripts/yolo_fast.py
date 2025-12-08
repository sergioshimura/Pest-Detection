import sys
import struct
import torch
from ultralytics import YOLO
import cv2
import time
import datetime # <--- ADICIONADO

# ===== CONFIGURAÇÕES =====
RTSP_URL = "rtmp://192.168.3.171:1935/live"
USE_GSTREAMER = False  # mude para True se quiser usar a pipeline GStreamer abaixo
GSTREAMER_PIPELINE = (
    f"rtspsrc location={RTSP_URL} latency=100 ! "
    "rtpjitterbuffer ! "
    "rtph264depay ! h264parse ! avdec_h264 ! "
    "videoconvert ! appsink drop=1 max-buffers=1 sync=false"
)

# O código serial foi mantido comentado como no original
# SERIAL_PORT = '/dev/ttyTHS1'
# SERIAL_BAUD = 115200

# ===== YOLO =====
model = YOLO("pricly_pear_health3.pt")
class_names = model.names

# Se CUDA estiver disponível, usa GPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Usando device: {device}")
print("Iniciando detecção... Pressione Ctrl+C para parar.")


model.to(device)

# ===== Entrada do usuário =====
# Mantido comentado para focar na detecção, descomente se precisar
# try:
#     target_class = int(input("Digite o número da classe que deseja detectar: "))
# except ValueError:
#     print("Entrada inválida! Digite um número inteiro.")
#     sys.exit(1)

def open_capture():
    if USE_GSTREAMER:
        cap = cv2.VideoCapture(GSTREAMER_PIPELINE, cv2.CAP_GSTREAMER)
    else:
        cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap

cap = open_capture()
if not cap.isOpened():
    print("Não foi possível abrir o stream RTSP.")
    sys.exit(1)

last_ok_time = time.time()
RECONNECT_AFTER_SEC = 5

try:
    while True:
        ret, frame = cap.read()

        if not ret or frame is None:
            if time.time() - last_ok_time > RECONNECT_AFTER_SEC:
                print("Sem frames recentes — tentando reconectar ao RTSP...")
                cap.release()
                time.sleep(1)
                cap = open_capture()
                if not cap.isOpened():
                    print("Falha ao reconectar. Tentará novamente...")
                    time.sleep(2)
                last_ok_time = time.time()
            continue

        last_ok_time = time.time()

        # YOLO
        results = model(frame, imgsz=640)

        # Para cada objeto detectado, imprime a informação com timestamp
        for box in results[0].boxes:
            # Captura o timestamp no momento da detecção
            timestamp = datetime.datetime.now().isoformat()
            
            # Extrai os dados da detecção
            confidence = float(box.conf[0].item())
            class_id = int(box.cls[0].item())
            class_name = class_names.get(class_id, "Desconhecido")

            # Imprime o log de detecção no terminal
            print(f"Timestamp: {timestamp}, Detecção: Classe '{class_name}' ({class_id}), Confiança: {confidence:.2f}")

        # VISUALIZAÇÃO DE VÍDEO REMOVIDA PARA MELHORAR VELOCIDADE
        # cv2.imshow("RTSP Camera", frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

except KeyboardInterrupt:
    print("\nScript interrompido pelo usuário (Ctrl+C).")
except Exception as e:
    print(f"Erro inesperado: {e}")
finally:
    # Cleanup
    print("Encerrando o programa e liberando recursos.")
    cap.release()
    # cv2.destroyAllWindows() # Não é mais necessário