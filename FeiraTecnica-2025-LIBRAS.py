import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import math

# Inicializações
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Para armazenar o movimento do dedo
trajetoria = deque(maxlen = 120)  # guarda os últimos 120 frames

# Estado de gravação
gravando = False
ultima_letra = None
rotacao_inicial = None
rotacao_final = None
last_time = 0
intervalo = 2

def extrair_coordenadas(landmarks, frame):
    h, w, _ = frame.shape
    
    indices = {
        'centro': 0,
        'polegar': 4,
        'indicador': 8,
        'medio': 12,
        'anelar': 16,
        'mindinho': 20
    }

    coordenadas = {
        dedo: (
            int(landmarks[i].x * w),
            int(landmarks[i].y * h),
            landmarks[i].z
        )
        for dedo, i in indices.items()
    }

    return coordenadas

def calcular_rotacao_horizontal(diff, info_mao):
    if info_mao == 'Left':
        if diff > 0.065: return 'tras'
        elif diff < -0.065: return 'frente'
    else:
        if diff > 0.065: return 'frente'
        elif diff < -0.065: return 'tras'
    if -0.045 < diff < 0.045: return 'lado'
    return 'diagonal'

class LetraBase:
    def estados(self, landmarks):    

        y_palmatopo = min(landmarks[i].y for i in [5, 9, 13, 17])
        
        def dedo_levantado(ponta, media):
            if ponta != 20:
                return landmarks[ponta].y < landmarks[media].y and landmarks[media].y - landmarks[ponta].y > 0.08
            else:
                return landmarks[ponta].y < landmarks[media].y and landmarks[media].y - landmarks[ponta].y > 0.06
        
        def dedo_parcial(ponta, anti_ponta, media, base):
            return (
                landmarks[ponta].y > landmarks[anti_ponta].y and 
                landmarks[ponta].y < landmarks[base].y and
                landmarks[base].y - landmarks[media].y > 0.02 and
                abs(landmarks[base].x - landmarks[media].x) < 0.03
            )
        
        def dedo_abaixado(ponta, anti_ponta, base):
            return landmarks[ponta].y > landmarks[anti_ponta].y and landmarks[ponta].y - landmarks[base].y > 0.15
        
        def dedo_C(ponta, media, base):
            dedos = [8, 12, 16, 18]
            return (
                abs(landmarks[ponta].x - landmarks[media].x) > 0.05 and 
                landmarks[base].y > landmarks[media].y and
                all(landmarks[4].y - landmarks[i].y > 0.041 for i in dedos)
            )
        
        def dedo_O(ponta, media, base):
            return (
                abs(landmarks[media].x - landmarks[base].x) > 0.04 and 
                landmarks[ponta].y > landmarks[media].y and
                landmarks[4].y - landmarks[ponta].y < 0.04
            )
        
        return {
            'polegar': landmarks[4].y < y_palmatopo,
            'indicador': dedo_levantado(8, 6),
            'medio': dedo_levantado(12, 10),
            'anelar': dedo_levantado(16, 14),
            'mindinho': dedo_levantado(20, 18),
            'polegar_parcial': landmarks[4].y < landmarks[3].y,
            'indicador_parcial': dedo_parcial(8, 7, 6, 5),
            'medio_parcial': dedo_parcial(12, 11, 10, 9),
            'anelar_parcial': dedo_parcial(16, 15, 14, 13),
            'mindinho_parcial': dedo_parcial(20, 19, 18, 17),
            'indicador_abaixado': dedo_abaixado(8, 7, 5),
            'medio_abaixado': dedo_abaixado(12, 11, 9),
            'anelar_abaixado': dedo_abaixado(16, 15, 13),
            'mindinho_abaixado': dedo_abaixado(20, 19, 17),
            'polegar_C': landmarks[4].y < landmarks[3].y and abs(landmarks[4].x - landmarks[2].x) > 0.01,
            'indicador_C': dedo_C(8, 6, 5),
            'medio_C': dedo_C(12, 10, 9),
            'anelar_C': dedo_C(16, 14, 13),
            'mindinho_C': dedo_C(20, 18, 17),
            'polegar_O': landmarks[4].y < landmarks[3].y and abs(landmarks[4].x - landmarks[2].x) > 0.01,
            'indicador_O': dedo_O(8, 6, 5),
            'medio_O': dedo_O(12, 10, 9),
            'anelar_O': dedo_O(16, 14, 13),
            'mindinho_O': dedo_O(20, 18, 17)
        }
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):
        raise NotImplementedError("Subclasses devem implementar o detectar")
    
    def detectar_mudanca(trajetoria):
        vetores = []
        for i in range(1, trajetoria // 4, 4):
            dx = trajetoria[i + 4]['indicador'][0] - trajetoria[i]['indicador'][0]
            dy = trajetoria[i + 4]['indicador'][1] - trajetoria[i]['indicador'][1]
            vetores.append((dx, dy))
        pontos = []
        for i in range(vetores):
            dx = vetores[i][0]
            if dx > 0:
                if dx > vetores[i + 1][0]:
                    pontos.append(dx)
            elif dx < vetores[i + 1][0]:
                    pontos.append(dx)

    # Calcula o ângulo em graus de dois pontos
    def calcular_angulo(p1, p2):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        angulo = math.degrees(math.atan2(dy, dx)) 
        return angulo

class letra_A(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):
        if info_mao == 'Left':
            polegar_correto = landmarks[4].x > landmarks[5].x 
        else:
            polegar_correto = landmarks[4].x < landmarks[5].x

        return (
            polegar_correto and
            estados['polegar'] and
            not estados['indicador'] and
            not estados['medio'] and
            not estados['mindinho'] and
            not estados['indicador_parcial'] and
            not estados['medio_parcial'] and
            not estados['mindinho_parcial'] and
            rotacao_final in ['frente', 'diagonal']
        )

class letra_B(LetraBase):
    
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):
        if info_mao == 'Left':
            polegar_correto = landmarks[4].x < landmarks[5].x
        else:
            polegar_correto = landmarks[4].x > landmarks[5].x
        return (
            polegar_correto and
            estados['indicador'] and
            estados['medio'] and
            estados['anelar'] and
            estados['mindinho'] and 
            rotacao_final in ['frente', 'diagonal']
        )

class letra_C(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):
        return (
            estados['polegar_C'] and
            estados['indicador_C'] and
            estados['medio_C'] and
            estados['anelar_C'] and
            estados['mindinho_C'] and
            rotacao_final in ['lado', 'diagonal']
        )
    
class letra_D(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):
        return (
            estados['polegar_parcial'] and
            estados['indicador'] and
            not estados['medio'] and
            not estados['anelar'] and
            not estados['mindinho'] and
            abs(landmarks[4].y - landmarks[11].y) < 0.1 and
            abs(landmarks[4].x - landmarks[12].x) < 0.1 and
            landmarks[4].y > landmarks[11].y and
            rotacao_final in ['frente', 'diagonal']
        )

class letra_E(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):
        return (
            estados['indicador_parcial'] and
            not estados['indicador'] and
            estados['medio_parcial'] and
            not estados['medio'] and
            estados['anelar_parcial'] and
            not estados['anelar'] and
            not estados['mindinho'] and
            rotacao_final in ['frente', 'diagonal']
     )

class letra_G(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):
        return (
            estados['polegar'] and
            estados['indicador'] and
            not estados['medio'] and
            not estados['anelar'] and
            not estados['mindinho'] and
            landmarks[4].y < landmarks[11].y and
            rotacao_final in ['frente', 'tras']
        )

class letra_H(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):
        return (
            estados['polegar'] and
            estados['indicador'] and
            estados['medio'] and
            not estados['anelar'] and
            not estados['mindinho'] and
            rotacao_inicial in ['frente', 'diagonal'] and
            rotacao_final in ['tras', 'diagonal']
        )

class letra_I(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):
        return (
            estados['polegar'] and
            estados['mindinho'] and
            not estados['indicador'] and
            not estados['medio'] and
            not estados['anelar'] and
            abs(landmarks[4].x - landmarks[5].x) < 0.08 and
            rotacao_final in ['frente', 'diagonal']
        )

class letra_J(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):
        if dx is None:
            dx = 0
        return (
            abs(dx) > 10 and
            estados['polegar'] and
            estados['mindinho'] and
            not estados['indicador'] and
            not estados['medio'] and
            not estados['anelar'] and
            rotacao_inicial in ['frente', 'diagonal'] and
            rotacao_final in ['tras', 'diagonal']
        )

class letra_K(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):
        
        n = len(trajetoria)
        if n < 5:
            return False # Poucos pontos para traçar um X
        
        return(
            estados['polegar'] and
            estados['indicador'] and
            not estados['anelar'] and
            not estados['mindinho'] and
            landmarks[12].z < landmarks[10].z and
            landmarks[12].z < landmarks[9].z and
            landmarks[12].y < landmarks[9].y and
            trajetoria[-1]['indicador'][1] - trajetoria[0]['indicador'][1] > 10
        )

class letra_L(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):
    
        if info_mao == 'Left':
            polegar_correto = landmarks[4].x - landmarks[3].x > 0.1 and landmarks[4].x > landmarks[3].x
        else:
            polegar_correto = landmarks[3].x  - landmarks[4].x < 0.1 and landmarks[4].x < landmarks[3].x

        return(
            polegar_correto and
            estados['indicador'] and
            not estados['polegar'] and
            not estados['medio'] and
            not estados['anelar'] and
            not estados['mindinho'] and
            rotacao_final in ['frente', 'diagonal']
        )

class letra_M(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):
        return (
            estados['indicador_abaixado'] and
            estados['medio_abaixado'] and
            estados['anelar_abaixado'] and
            not estados['mindinho_abaixado']
        )
    
class letra_N(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):
        return (
            estados['indicador_abaixado'] and
            estados['medio_abaixado'] and
            not estados['anelar_abaixado'] and
            not estados['mindinho_abaixado']
        )

class letra_O(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):
        return (
            estados['polegar_O'] and
            estados['indicador_O'] and
            estados['medio_O'] and
            estados['anelar_O'] and
            estados['mindinho_O'] and
            rotacao_final in ['lado', 'diagonal']
        )

class letra_Q(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):
        return (
            estados['indicador_abaixado'] and
            not estados['medio_abaixado'] and
            not estados['anelar_abaixado'] and
            not estados['mindinho_abaixado']
        )

class letra_S(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):
        if info_mao == 'Left':
            polegar_correto = landmarks[4].x < landmarks[3].x and landmarks[3].x - landmarks[4].x > 0.02
        else:
            polegar_correto = landmarks[4].x > landmarks[3].x and landmarks[4].x - landmarks[3].x > 0.02

        return (
            polegar_correto and
            not estados['indicador'] and
            not estados['medio'] and
            not estados['mindinho'] and
            not estados['indicador_parcial'] and
            not estados['medio_parcial'] and
            not estados['mindinho_parcial'] and
            rotacao_final in ['frente', 'diagonal']
        )
    
class letra_U(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):
        if info_mao == 'Left':
            polegar_correto = landmarks[4].x < landmarks[5].x
        else:
            polegar_correto = landmarks[4].x > landmarks[5].x

        diff_correta = abs(landmarks[12].x - landmarks[8].x) < 0.06

        return (
            polegar_correto and
            diff_correta and
            estados['indicador'] and
            estados['medio'] and
            not estados['anelar'] and
            not estados['mindinho'] and
            rotacao_final in ['frente', 'tras']
        )

class letra_V(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):

        if info_mao == 'Left':
            polegar_correto = landmarks[4].x < landmarks[5].x
        else:
            polegar_correto = landmarks[4].x > landmarks[5].x

        diff_correta = abs(landmarks[12].x - landmarks[8].x) > 0.061

        return (
            polegar_correto and
            diff_correta and
            estados['indicador'] and
            estados['medio'] and
            not estados['anelar'] and
            not estados['mindinho'] and
            rotacao_final in ['frente', 'tras']
        )

class letra_W(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):

        if info_mao == 'Left':
            polegar_correto = landmarks[4].x < landmarks[5].x
        else:
            polegar_correto = landmarks[4].x > landmarks[5].x

        return (
            polegar_correto and
            estados['indicador'] and
            estados['medio'] and
            estados['anelar'] and
            not estados['mindinho'] and
            rotacao_final in ['frente', 'diagonal']
        )

class letra_Y(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):

        if info_mao == 'Left':
            polegar_correto = landmarks[4].x > landmarks[2].x
        else:
            polegar_correto = landmarks[4].x < landmarks[2].x

        return (
            estados['mindinho'] and
            not estados['indicador'] and
            not estados['medio'] and
            not estados['anelar'] and
            polegar_correto and
            abs(landmarks[4].x - landmarks[2].x) > 0.05 and
            rotacao_final in ['frente', 'diagonal']
        )

class letra_X(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):
        n = len(trajetoria)
        if n < 5:
            return False # Poucos pontos para traçar um X
        return(
            trajetoria[0]['indicador'][2] < trajetoria[-1]['indicador'][2] and
            landmarks[6].z < landmarks[5].z and
            abs(landmarks[6].x - landmarks[5].x) < 0.051 and 
            abs(landmarks[10].x - landmarks[9].x) > 0.05 and 
            abs(landmarks[14].x - landmarks[13].x) > 0.05 and 
            abs(landmarks[18].x - landmarks[17].x) > 0.05 and
            abs(landmarks[12].x - landmarks[10].x) < 0.05 and 
            abs(landmarks[16].x - landmarks[14].x) < 0.05 and 
            abs(landmarks[20].x - landmarks[18].x) < 0.05 and
            trajetoria[-1]['indicador'][2] - trajetoria[0]['indicador'][2] > 0.01
        )
    
class letra_Z(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None, dx = None):
        n = len(trajetoria)
        if n < 10:
            return False  # Poucos pontos para traçar um Z
        traj = [coord['indicador'][0] for coord in trajetoria]
        vetores = []
        for i in range(0, len(trajetoria) - 4, 4):
            dx = traj[i + 4] - traj[i]
            vetores.append(dx)
        pontos = [traj[0]]
        cont = 1
        if vetores[2] > 0:
            for i in range(2, len(vetores)):
                if cont == 1 and vetores[i] < 0 or cont == 2 and vetores[i] > 0:
                    pontos.append(traj[i * 4])
                    cont += 1
        else:
            for i in range(2, vetores):
                if cont == 1 and vetores[i] > 0 or cont == 2 and vetores[i] < 0:
                    pontos.append(traj[i * 4])
                    cont += 1
        return (
            len(pontos) == 4 and
            trajetoria[-1]['indicador'][1] - trajetoria[0]['indicador'][1] > 10 
        )
# Função simples pra reconhecer "padrões" de movimento
# valores dos pixels aumentam de: baixo -> cima e esquerda -> direita
def detectar(estados, trajetoria, landmarks, info_mao, rotacao_inicial, rotacao_final, dx):
    print("Deslocamento dx:", dx)

    if estados['polegar']: print('Polegar Levantado')
    if estados['indicador']: print('Indicador Levantado')
    if estados['medio']: print('Médio Levantado')
    if estados['anelar']: print('Anelar Levantado')
    if estados['mindinho']: print('Mindinho Levantado')
    if estados['polegar_parcial']: print('Polegar Parcial')
    if estados['indicador_parcial']: print('Indicador Parcial')
    if estados['medio_parcial']: print('Médio Parcial')
    if estados['anelar_parcial']: print('Anelar Parcial')
    if estados['mindinho_parcial']: print('Mindinho Parcial')
    if estados['indicador_abaixado']: print('Indicador Abaixado')
    if estados['medio_abaixado']: print('Médio Abaixado')
    if estados['anelar_abaixado']: print('Anelar Abaixado')
    if estados['mindinho_abaixado']: print('Mindinho Abaixado')
    if estados['polegar_C']: print('Polegar C')
    if estados['indicador_C']: print('Indicador C')
    if estados['medio_C']: print('Médio C')
    if estados['anelar_C']: print('Anelar C')
    if estados['mindinho_C']: print('Mindinho C')
    if estados['polegar_O']: print('Polegar O')
    if estados['indicador_O']: print('Indicador O')
    if estados['medio_O']: print('Médio O')
    if estados['anelar_O']: print('Anelar O')
    if estados['mindinho_O']: print('Mindinho O')

    letras = {
    'A': letra_A(),
    'B': letra_B(),
    'C': letra_C(),
    'D': letra_D(),
    'E': letra_E(),
    'G': letra_G(),
    'H': letra_H(),
    'I': letra_I(),
    'J': letra_J(),
    'K': letra_K(),
    'L': letra_L(),
    'M': letra_M(),
    'N': letra_N(),
    'O': letra_O(),
    'Q': letra_Q(),
    'S': letra_S(),
    'U': letra_U(),
    'V': letra_V(),
    'W': letra_W(),
    'Y': letra_Y(),
    'X': letra_X(),
    'Z': letra_Z()
    }
    
    for letra, detector in letras.items():
        if detector.detectar_letras(estados, trajetoria, landmarks, info_mao, rotacao_inicial, rotacao_final, dx):
            return letra
    return '?'

gravando = False
rotacao_inicial = None
rotacao_final = None
ultima_letra = '?'
trajetoria = []

def movimento_parado(trajetoria):
    if len(trajetoria) < 41:
        return False
    recentes = trajetoria[-41:]
    tempo_parado = 0
    for i in range(40):
        dx = recentes[i + 1]['indicador'][0] - recentes[i]['indicador'][0]
        dy = recentes[i + 1]['indicador'][1] - recentes[i]['indicador'][1]
        dz = recentes[i + 1]['indicador'][2] - recentes[i]['indicador'][2]
        if abs(dx) < 1 or abs(dy) < 1:
            tempo_parado += 1
    if tempo_parado > 28:
        return True 
    return False

def movimento_andando(trajetoria):
    if len(trajetoria) < 41:
        return False
    recentes = trajetoria[-41:]
    tempo_movendo = 0
    for i in range(40):
        dx = recentes[i + 1]['indicador'][0] - recentes[i]['indicador'][0]
        dy = recentes[i + 1]['indicador'][1] - recentes[i]['indicador'][1]
        dz = recentes[i + 1]['indicador'][2] - recentes[i]['indicador'][2]
        if abs(dx) > 1 or abs(dy) > 1 or abs(dz) > 1:
            tempo_movendo += 1
        print(tempo_movendo)
    if tempo_movendo > 29:
        return True 
    return False

def processar_frame(frame):
    global gravando, rotacao_inicial, rotacao_final, ultima_letra

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultados = hands.process(frame_rgb)

    if resultados.multi_hand_landmarks:
        for idx, mao in enumerate(resultados.multi_hand_landmarks):
            mp_draw.draw_landmarks(frame, mao, mp_hands.HAND_CONNECTIONS)
            info_mao = resultados.multi_handedness[idx].classification[0].label
            landmarks = mao.landmark
            coord = extrair_coordenadas(landmarks, frame)

            trajetoria.append(coord)

            if len(trajetoria) > 1:
                for i in range(1, len(trajetoria)):
                    pt1 = trajetoria[i - 1]['indicador']
                    pt2 = trajetoria[i]['indicador']
                    cv2.line(frame, pt1[:2], pt2[:2], (0, 255, 0), 2)

            if len(trajetoria) > 100:
                trajetoria.pop(0)
            
           # if movimento_andando(trajetoria):
                # trajetoria.clear()
                # gravando = True
            #if gravando:
                #if movimento_parado(trajetoria):
                    #deleta as ultimas 28 posições da lista
            if not gravando:
                del trajetoria[-28:]
                gravando = False
                if len(trajetoria) >= 1:
                    dx = trajetoria[-1]['mindinho'][0] - trajetoria[0]['mindinho'][0]
                    estados = LetraBase().estados(landmarks)
                    diff = landmarks[17].x - landmarks[5].x
                    rotacao_final = calcular_rotacao_horizontal(diff, info_mao)
                    letra = detectar(estados, trajetoria, landmarks, info_mao, rotacao_inicial, rotacao_final, dx)
                    cv2.line(frame, pt1[:2], pt2[:2], (0, 255, 0), 2)

                    if letra != ' ':
                        print("Letra detectada:", letra)
                        ultima_letra = letra
            # Define a rotação inicial uma vez só
            if rotacao_inicial is None:
                diff = landmarks[17].x - landmarks[5].x
                rotacao_inicial = calcular_rotacao_horizontal(diff, info_mao)

    status = "Gravando..." if gravando else "Movimente a Mao para Iniciar"
    cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    return frame

# Captura de vídeo
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    tecla = cv2.waitKey(1) & 0xFF

    if tecla == ord(' '):
            gravando = not gravando
            rotacao_inicial = None
            rotacao_final = None

    if tecla == 27:  # ESC
        break

    frame = processar_frame(frame)
    cv2.putText(frame, f"Letra: {ultima_letra}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
    cv2.imshow("Detector LIBRAS - H/J/Z", frame)

cap.release()
cv2.destroyAllWindows()
