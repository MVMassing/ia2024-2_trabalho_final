import cv2
import mediapipe as mp
import numpy as np
import time
from playsound import playsound
import os

# Inicializa o MediaPipe Pose e a webcam
mp_pose = mp.solutions.pose
mp_desenho = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)

# Define o arquivo de som de alerta
alerta = "sentar_na_mesa.wav"

# Variáveis para calibração inicial
calibrado = False
quadros_calibracao = 0
calibracao_angulo_ombro = []
calibracao_angulo_pescoco = []
ultimo_alerta = 0
tempo_alerta = 10  # Intervalo mínimo entre alertas (segundos)
tempo_minimo_postura_ruim = 3  # Tempo mínimo em postura ruim para disparar o alerta (segundos)
tempo_postura_ruim_iniciado = None

# Função para calcular o ângulo
def calcular_angulo(ponto1, ponto2, ponto3):
    angulo = np.arctan2(ponto3[1] - ponto2[1], ponto3[0] - ponto2[0]) - np.arctan2(ponto1[1] - ponto2[1], ponto1[0] - ponto2[0])
    return np.abs(angulo * 180.0 / np.pi)

# Função para desenhar o ângulo na tela
def desenhar_angulo(frame, ponto1, ponto2, ponto3, angulo, cor):
    cv2.line(frame, ponto1, ponto2, cor, 3)
    cv2.line(frame, ponto2, ponto3, cor, 3)
    cv2.putText(frame, str(int(angulo)), (ponto2[0] - 50, ponto2[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2, cv2.LINE_AA)

# Função para dar feedback sobre a postura
def feedback_postura(angulo_ombro, limite_ombro_min, limite_ombro_max, angulo_pescoco, limite_pescoco_min, limite_pescoco_max):
    global tempo_postura_ruim_iniciado, ultimo_alerta
    tempo_atual = time.time()
    
    if angulo_ombro < limite_ombro_min or angulo_ombro > limite_ombro_max or angulo_pescoco < limite_pescoco_min or angulo_pescoco > limite_pescoco_max:
        status = "Postura Ruim"
        cor = (0, 0, 255)  # Vermelho
        
        # Se a postura ruim for detectada, inicia o tempo
        if tempo_postura_ruim_iniciado is None:
            tempo_postura_ruim_iniciado = tempo_atual
        # Se já passou o tempo mínimo de postura ruim, dispara o alarme
        elif tempo_atual - tempo_postura_ruim_iniciado >= tempo_minimo_postura_ruim:
            if tempo_atual - ultimo_alerta > tempo_alerta:
                print("Postura ruim detectada!")
                if os.path.exists(alerta):
                    playsound(alerta)  # Toca o som
                ultimo_alerta = tempo_atual
    else:
        status = "Postura Boa"
        cor = (0, 255, 0)  # Verde
        # Se a postura é boa, reinicia o tempo
        tempo_postura_ruim_iniciado = None

    # Exibe as informações da imagem
    cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2, cv2.LINE_AA)
    cv2.putText(frame, f"Ombro: {angulo_ombro:.1f}/{limite_ombro_min:.1f}-{limite_ombro_max:.1f}", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, f"Pescoco: {angulo_pescoco:.1f}/{limite_pescoco_min:.1f}-{limite_pescoco_max:.1f}", (10, 90), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

# Loop principal para captura e processamento da imagem da webcam
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue

    # Conversão de BGR para RGB para o MediaPipe
    quadro_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultados = pose.process(quadro_rgb)

    if resultados.pose_landmarks:
        pontos = resultados.pose_landmarks.landmark

        # Extração de marcadores principais do corpo
        ombro_esquerdo = (int(pontos[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * frame.shape[1]),
                          int(pontos[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * frame.shape[0]))
        ombro_direito = (int(pontos[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * frame.shape[1]),
                         int(pontos[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y * frame.shape[0]))
        orelha_esquerda = (int(pontos[mp_pose.PoseLandmark.LEFT_EAR.value].x * frame.shape[1]),
                           int(pontos[mp_pose.PoseLandmark.LEFT_EAR.value].y * frame.shape[0]))
        orelha_direita = (int(pontos[mp_pose.PoseLandmark.RIGHT_EAR.value].x * frame.shape[1]),
                          int(pontos[mp_pose.PoseLandmark.RIGHT_EAR.value].y * frame.shape[0]))

        # Cálculo de ângulos
        angulo_ombro = calcular_angulo(ombro_esquerdo, ombro_direito, (ombro_direito[0], 0))
        angulo_pescoco = calcular_angulo(orelha_esquerda, ombro_esquerdo, (ombro_esquerdo[0], 0))

        # Calibração
        if not calibrado and quadros_calibracao < 30:
            calibracao_angulo_ombro.append(angulo_ombro)
            calibracao_angulo_pescoco.append(angulo_pescoco)
            quadros_calibracao += 1
            cv2.putText(frame, f"Calibrando... {quadros_calibracao}/30", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
        elif not calibrado:
            margem = 5  # Margem de tolerância em graus para disparar o alarme (segundos)
            limite_ombro_min = np.mean(calibracao_angulo_ombro) - margem
            limite_ombro_max = np.mean(calibracao_angulo_ombro) + margem
            limite_pescoco_min = np.mean(calibracao_angulo_pescoco) - margem
            limite_pescoco_max = np.mean(calibracao_angulo_pescoco) + margem
            calibrado = True
            print(f"Calibração concluída. Limite Ombro: {limite_ombro_min:.1f}-{limite_ombro_max:.1f}, Limite Pescoço: {limite_pescoco_min:.1f}-{limite_pescoco_max:.1f}")

        # Desenha o esqueleto e os ângulos na tela
        mp_desenho.draw_landmarks(frame, resultados.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        meio = ((ombro_esquerdo[0] + ombro_direito[0]) // 2, (ombro_esquerdo[1] + ombro_direito[1]) // 2)
        desenhar_angulo(frame, ombro_esquerdo, meio, (meio[0], 0), angulo_ombro, (255, 0, 0))
        desenhar_angulo(frame, orelha_esquerda, ombro_esquerdo, (ombro_esquerdo[0], 0), angulo_pescoco, (0, 255, 0))

        # FEEDBACK
        if calibrado:
            feedback_postura(angulo_ombro, limite_ombro_min, limite_ombro_max, angulo_pescoco, limite_pescoco_min, limite_pescoco_max)

    # Mostra o vídeo
    cv2.imshow("Corretor Postural", frame)
    
    # Fecha o programa teclando 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
