import cv2
from PIL import ImageFont, ImageDraw, Image # Suporta Unicode ( Emojis )
import mediapipe as mp
import numpy as np
from collections import deque, Counter
# Inicializações
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Para armazenar o movimento do dedo
trajetoria = deque(maxlen = 150)  # guarda os últimos 150 frames

# Estado de gravação
gravando = False
ultima_letra = None
rotacao_inicial = None
rotacao_final = None
last_time = 0
intervalo = 2

class LetraBase:
    trajetoria_Z = deque(maxlen = 50)
    def avaliar_criterios(self, *criterios):
        total = len(criterios)
        #conta quantos desses critérios são verdadeiros.
        score = sum(1 for c in criterios if c) / total
        return score
    
    def estados(self, landmarks):    

        y_palmatopo = min(landmarks[i].y for i in [5, 9, 13, 17])
        
        def dedo_levantado(ponta, media):
            if ponta != 20:
                return landmarks[ponta].y < landmarks[media].y and landmarks[media].y - landmarks[ponta].y > 0.06
            else:
                return landmarks[ponta].y < landmarks[media].y and landmarks[media].y - landmarks[ponta].y > 0.04
        
        def dedo_parcial(ponta, anti_ponta, media, base):
            return (
                landmarks[ponta].y > landmarks[anti_ponta].y and 
                landmarks[ponta].y < landmarks[base].y and
                landmarks[base].y - landmarks[media].y > 0.02 and
                abs(landmarks[base].x - landmarks[media].x) < 0.03
            )
        
        def dedo_abaixado(ponta, anti_ponta, base):
            return landmarks[ponta].y > landmarks[anti_ponta].y and landmarks[ponta].y - landmarks[base].y > 0.15
        
        def dedo_deitado(ponta, anti_ponta, media, base):
            y_vals = [landmarks[i].y for i in [ponta, anti_ponta, media, base]]
            return max(y_vals) - min(y_vals) <= 0.02

        def polegar_deitado():
            y_vals = [landmarks[i].y for i in [1,2,3,4]]
            return max(y_vals) - min(y_vals) <= 0.02
        
        def dedo_C(ponta, media, base):
            dedos = [8, 12, 16, 18]
            return (
                abs(landmarks[ponta].x - landmarks[media].x) > 0.05 and 
                landmarks[base].y > landmarks[media].y and
                all(landmarks[4].y - landmarks[i].y > 0.041 for i in dedos)
            )
        
        def dedo_O(ponta, media, base):
            return (
                abs(landmarks[media].x - landmarks[base].x) > 0.07 and  # exige abertura maior
                landmarks[ponta].y > landmarks[media].y and
                abs(landmarks[4].x - landmarks[ponta].x) < 0.05 and     # polegar próximo do dedo
                abs(landmarks[4].y - landmarks[ponta].y) < 0.05
            )
        def mao_abaixada():
            # pense no punho fechado, ai juntando com as defs de dedo abaixado funciona :D
            return (
                # indicador
                landmarks[5].y > landmarks[0].y and

                # medio
                landmarks[9].y > landmarks[0].y and

                # anelar
                landmarks[13].y > landmarks[0].y and

                # mindinho
                landmarks[17].y > landmarks[0].y
            )

        def mao_levantada():
            return (
                # indicador
                landmarks[5].y < landmarks[0].y and

                # medio
                landmarks[9].y < landmarks[0].y and

                # anelar
                landmarks[13].y < landmarks[0].y and

                # mindinho
                landmarks[17].y < landmarks[0].y
            )

        def mao_deitada(tolerancia=0.05):
            base_mao_y = landmarks[0].y
            base_dedos = [5, 9, 13, 17]
            for base in base_dedos:
                diff = abs(landmarks[base].y - base_mao_y)
                if diff > tolerancia:
                    return False
            return True
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
            'mindinho_O': dedo_O(20, 18, 17),
            'polegar_deitado': polegar_deitado(),
            'indicador_deitado': dedo_deitado(8,7,6,5),
            'medio_deitado': dedo_deitado(12,11,10,9),
            'anelar_deitado': dedo_deitado(16, 15, 14, 13),
            'mindinho_deitado': dedo_deitado(20, 18, 17, 16),
            'mao_abaixada': mao_abaixada(),
            'mao_levantada': mao_levantada(),
            'mao_deitada': mao_deitada()
        }
    def detectar_letras(self, estados, trajetoriaSuavizada, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None):
        raise NotImplementedError("Subclasses devem implementar o detectar")

class letra_A(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None):
        if len(trajetoria) > 5:
            return 0.0
        if info_mao == 'Left':
            polegar_correto = landmarks[4].x > landmarks[5].x
        else:
            polegar_correto = landmarks[4].x < landmarks[5].x

        return self.avaliar_criterios(
            polegar_correto,
            estados['polegar'],
            not estados['indicador'],
            not estados['medio'],
            not estados['anelar'],
            not estados['mindinho'],
            not estados['indicador_abaixado'],
            not estados['medio_abaixado'],
            not estados['anelar_abaixado'],
            not estados['mindinho_abaixado'],
            rotacao_final in ['frente', 'diagonal']
        )

class letra_B(LetraBase):

    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None):
        if len(trajetoria) > 5:
            return 0.0
        if info_mao == 'Left':
            polegar_correto = landmarks[4].x < landmarks[5].x
        else:
            polegar_correto = landmarks[4].x > landmarks[5].x
        return self.avaliar_criterios(
            polegar_correto,
            estados['indicador'],
            estados['medio'],
            estados['anelar'],
            estados['mindinho'],
            rotacao_final in ['frente', 'diagonal']
        )

class letra_C(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        if len(trajetoria) > 5:
            return 0.0
        return self.avaliar_criterios(
            estados['polegar_C'],
            estados['indicador_C'],
            estados['medio_C'],
            estados['anelar_C'],
            estados['mindinho_C'],
            rotacao_final in ['lado', 'diagonal']
        )

class letra_D(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        if len(trajetoria) > 5:
            return 0.0
        condicao = abs(landmarks[4].x - landmarks[12].x) < 0.1 and abs(landmarks[4].y - landmarks[12].y) < 0.1
        return self.avaliar_criterios(
            estados['polegar_parcial'],
            estados['indicador'],
            not estados['medio'],
            not estados['anelar'],
            not estados['mindinho'],
            condicao
        )

class letra_E(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        if len(trajetoria) > 5:
            return 0.0
        return self.avaliar_criterios(
            estados['indicador_parcial'],
            not estados['indicador'],
            estados['medio_parcial'],
            not estados['medio'],
            estados['anelar_parcial'],
            not estados['anelar'],
            estados['mindinho_parcial'],
            not estados['mindinho'],
            rotacao_final in ['frente', 'diagonal']
        )

class letra_F(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        if len(trajetoria) > 5:
            return 0.0
        if info_mao == "Left":
            polegar_Fxy = landmarks[4].x > landmarks[8].x
        elif info_mao == "Right":
            polegar_Fxy = landmarks[4].x < landmarks[8].x
        return self.avaliar_criterios(
            polegar_Fxy,
            estados['polegar'],
            estados['medio'],
            estados['anelar'],
            estados['mindinho']
        )

class letra_G(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        # Novo: Proximidade (toque) entre pontas de polegar (4) e indicador (8) — <0.05 em X e Y normalizados
        if len(trajetoria) > 5:
            return 0.0
        toque = abs(landmarks[3].x - landmarks[8].x) < 0.1
        print(f"[DEBUG]: {toque}")
        rotacao_correta = rotacao_final in ['frente','diagonal']
        return self.avaliar_criterios(
            estados['polegar'],  # Polegar totalmente levantado
            estados['indicador'],  # Indicador levantado
            not estados['medio'],  # Médio dobrado
            not estados['anelar'],  # Anelar dobrado
            not estados['mindinho'],  # Mindinho dobrado
            toque,  # Novo: Pontas próximas (diferencia de D)
            rotacao_correta  # Novo: Palma para frente
        )

class letra_H(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        mudanca_rotacao = rotacao_inicial in ['frente', 'diagonal'] and rotacao_final in ['tras', 'diagonal', 'lado']
        polegar_correto = abs(landmarks[3].x - landmarks[8].x) < 0.05

        return self.avaliar_criterios(
            polegar_correto,
            estados['indicador'],
            estados['medio'],
            not estados['anelar'],
            not estados['mindinho'],
            mudanca_rotacao
        )

class letra_I(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        if len(trajetoria) > 5:
            return 0.0
        return self.avaliar_criterios(
            estados['polegar'],
            estados['mindinho'],
            not estados['indicador'],
            not estados['medio'],
            not estados['anelar'],
            abs(landmarks[4].x - landmarks[5].x) < 0.08,
            rotacao_final in ['frente', 'diagonal']
        )

class letra_J(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        dx = 0
        dy = 0
        for x in range(len(trajetoria)):
            trajx = abs(trajetoria[0]['mindinho'][0] - trajetoria[x]['mindinho'][0])
            trajy = abs(trajetoria[0]['mindinho'][1] - trajetoria[x]['mindinho'][1])
            if dx < trajx:
                dx = trajx
            if dy < trajy:
                dy = trajy
        print('DX J: ', dx)
        print('DY J: ', dy)
        return self.avaliar_criterios(
            estados['polegar'],
            estados['mindinho'],
            not estados['indicador'],
            not estados['medio'],
            not estados['anelar'],
            rotacao_inicial in ['frente', 'diagonal'],
            rotacao_final in ['tras', 'diagonal'],
            dx > 50,
            dy > 50
        )

class letra_K(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        n = len(trajetoria)
        if n < 5:
            return False  # Poucos pontos para traçar um X
        return self.avaliar_criterios(
            estados['polegar'],
            estados['indicador'],
            estados['medio'],
            not estados['anelar'],
            not estados['mindinho'],
            abs(trajetoria[-1]['indicador'][1] - trajetoria[0]['indicador'][1]) > 60
        )

class letra_L(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        if len(trajetoria) > 5:
            return 0.0
        polegar_correto = abs(landmarks[4].x - landmarks[2].x) > 0.08
        if info_mao == 'Left':
            dist_correta = landmarks[4].x > landmarks[2].x
        else:
            dist_correta = landmarks[4].x < landmarks[2].x
        return self.avaliar_criterios(
            polegar_correto,
            dist_correta,
            estados['indicador'],
            not estados['medio'],
            not estados['anelar'],
            not estados['mindinho'],
            rotacao_final in ['frente', 'diagonal']
        )

class letra_M(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        if len(trajetoria) > 5:
            return 0.0
        return self.avaliar_criterios(
            estados['indicador_abaixado'],
            estados['medio_abaixado'],
            estados['anelar_abaixado'],
            not estados['mindinho_abaixado'],
            not estados['indicador'],
            not estados['medio'],
            not estados['anelar'],
            not estados['mindinho']
        )

class letra_N(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        if len(trajetoria) > 5:
            return 0.0
        return self.avaliar_criterios(
            estados['indicador_abaixado'],
            estados['medio_abaixado'],
            not estados['anelar_abaixado'],
            not estados['mindinho_abaixado'],
            not estados['indicador'],
            not estados['medio'],
            not estados['anelar'],
            not estados['mindinho']
        )

class letra_O(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        if len(trajetoria) > 5:
            return 0.0
        return self.avaliar_criterios(
            estados['polegar_O'],
            estados['indicador_O'],
            estados['medio_O'],
            estados['anelar_O'],
            estados['mindinho_O'],
            rotacao_final in ['lado', 'diagonal', 'frente'],
            not estados['indicador'],
            not estados['medio'],
            not estados['anelar'],
            not estados['mindinho']
        )
    
class letra_P(LetraBase): 
    def detectar_letras(self, estados, trajetoriaSuavizada, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        print(rotacao_inicial)
        print(rotacao_final)

        if info_mao == 'Left':
            eixo_x_correto = (
                landmarks[9].x < landmarks[12].x and
                landmarks[5].x < landmarks[8].x and
                landmarks[2].x < landmarks[4].x and
                landmarks[16].x < landmarks[13].x and
                landmarks[20].x < landmarks[17].x
            )
        else:
            eixo_x_correto = (
                landmarks[9].x > landmarks[12].x and
                landmarks[5].x > landmarks[8].x and
                landmarks[2].x > landmarks[4].x and
                landmarks[16].x > landmarks[13].x and
                landmarks[20].x > landmarks[17].x
            )
        print("[DEBUG] Entrou no criterio P")

        return self.avaliar_criterios(
            eixo_x_correto,
            landmarks[8].y < landmarks[12].y,
            landmarks[4].y > landmarks[8].y,
            landmarks[4].y < landmarks[12].y,
            rotacao_final in ['lado'],
            rotacao_inicial in ['lado']
        )

class letra_Q(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        if len(trajetoria) > 5:
            return 0.0
        return self.avaliar_criterios(
            estados['indicador_abaixado'],
            not estados['medio_abaixado'],
            not estados['anelar_abaixado'],
            not estados['mindinho_abaixado'],
        )

class letra_R(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        if len(trajetoria) > 5:
            return 0.0
        if info_mao == 'Left':
            diff_correta = landmarks[12].x > landmarks[8].x
        else:
            diff_correta = landmarks[12].x < landmarks[8].x

        return self.avaliar_criterios(
            not estados['anelar'],
            not estados['mindinho'],
            estados['indicador'],
            estados['medio'],
            (estados['polegar_parcial'] or not estados['polegar']),
            diff_correta,
            rotacao_final in ['frente', 'diagonal']
        )

class letra_S(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        if info_mao == 'Left':
            polegar_correto = landmarks[4].x < landmarks[3].x and landmarks[3].x - landmarks[4].x > 0.02
        else:
            polegar_correto = landmarks[4].x > landmarks[3].x and landmarks[4].x - landmarks[3].x > 0.02
        if len(trajetoria) > 5:
            return 0.0
        return self.avaliar_criterios(
            polegar_correto,
            not estados['indicador'],
            not estados['medio'],
            not estados['anelar'],
            not estados['mindinho'],
            not estados['indicador_abaixado'],
            not estados['medio_abaixado'],
            not estados['anelar_abaixado'],
            not estados['mindinho_abaixado'],
            rotacao_final in ['frente', 'diagonal'],
            #trajetoria[-1]['indicador'][1] - trajetoria[0]['indicador'][1] < 50,
            #landmarks[5].z - landmarks[8].z < 0.05
        )
    
class letra_T(LetraBase):
    def detectar_letras(self, estados, trajetoriaSuavizada, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        if len(trajetoria) > 5:
            return 0.0
        if info_mao == "Left":
            if (landmarks[8].x > landmarks[4].x):
                polegar_Fxy = True
        elif info_mao == "Right":
            if (landmarks[4].x > landmarks[8].x):
                polegar_Fxy = True
        else:
            return 0.0  # Retorna score zero para mão desconhecida
        return self.avaliar_criterios(
            polegar_Fxy,
            estados['indicador_parcial'],
            estados['polegar'],
            estados['medio'],
            estados['anelar'],
            estados['mindinho']
        )

class letra_U(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        if len(trajetoria) > 5:
            return 0.0
        dedos_juntos = abs(landmarks[12].x - landmarks[8].x) < 0.06  # dedos juntos
        if info_mao == 'Left':
            diff_correta = landmarks[8].x > landmarks[12].x
        else:
            diff_correta = landmarks[8].x < landmarks[12].x
        return self.avaliar_criterios(
            estados['indicador'],
            estados['medio'],
            not estados['anelar'],
            not estados['mindinho'],
            dedos_juntos,
            diff_correta,
            abs(trajetoria[-1]['indicador'][1] - trajetoria[0]['indicador'][1]) < 60,
            rotacao_final in ['frente', 'tras']
        )

class letra_V(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        if len(trajetoria) > 5:
            return 0.0
        diff_correta = abs(landmarks[12].x - landmarks[8].x) > 0.06  # dedos separados

        return self.avaliar_criterios(
            estados['indicador'],
            estados['medio'],
            not estados['anelar'],
            not estados['mindinho'],
            diff_correta,
            abs(trajetoria[-1]['indicador'][1] - trajetoria[0]['indicador'][1]) < 60,
            rotacao_final in ['frente', 'tras']
        )

class letra_W(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        if len(trajetoria) > 5:
            return 0.0

        if info_mao == 'Left':
            polegar_correto = landmarks[4].x < landmarks[5].x
        else:
            polegar_correto = landmarks[4].x > landmarks[5].x

        return self.avaliar_criterios(
            polegar_correto,
            estados['indicador'],
            estados['medio'],
            estados['anelar'],
            not estados['mindinho'],
            rotacao_final in ['frente', 'diagonal']
        )

class letra_X(LetraBase):
    def detectar_letras(self, estados, trajetoriaSuavizada, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        n = len(trajetoriaSuavizada)
        if n < 5:
            return 0.0

        cruzamento_x = abs(landmarks[6].x - landmarks[5].x) > 0.02
        movimento_x = trajetoriaSuavizada[0]['indicador'][0] - trajetoriaSuavizada[-1]['indicador'][0]
        if abs(movimento_x) < 0.02:
            return 0.0  # sai antes de calcular score

        # Se passou no teste de movimento X, calcula o score normalmente
        score = self.avaliar_criterios(
            cruzamento_x,
            estados['indicador_deitado'],
            not estados["medio"],
            not estados["anelar"],
            not estados['mindinho'],
            rotacao_inicial in ['tras', 'diagonal', 'lado'],
            rotacao_final in ['tras', 'diagonal', 'lado']
        )
        return score

class letra_Y(LetraBase):
    def detectar_letras(self, estados, trajetoria, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):

        if info_mao == 'Left':
            polegar_correto = landmarks[4].x > landmarks[2].x
        else:
            polegar_correto = landmarks[4].x < landmarks[2].x

        return self.avaliar_criterios(
            estados['mindinho'],
            not estados['indicador'],
            not estados['medio'],
            not estados['anelar'],
            polegar_correto,
            abs(landmarks[4].x - landmarks[2].x) > 0.05,
            rotacao_final in ['frente', 'diagonal']
        )
    
class letra_Z(LetraBase):
    def detectar_letras(self, estados, trajetoriaSuavizada, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        n = len(trajetoriaSuavizada)
        if n < 5:
            print('POUCO PARA Z')
            return 0.0
        for i in range(0, n-3, 3):
            self.trajetoria_Z.append(suavizar_frame(trajetoriaSuavizada[i: i + 3]))
        traj = [coord['indicador'][0] for coord in self.trajetoria_Z]
        vetores = []
        for i in range(0, n-3, 3):
            dx = traj[i + 3] - traj[i]
            vetores.append(dx)
        pontos = [traj[0]]
        cont = 1
        for i in range(2, len(vetores)):
            if vetores[2] > 0:
                cond = (cont == 1 and vetores[i] < 0) or (cont == 2 and vetores[i] > 0)
            else:
                cond = (cont == 1 and vetores[i] > 0) or (cont == 2 and vetores[i] < 0)
            if cond:
                pontos.append(traj[i * 4])
                cont += 1
        print(f"[DEBUG] Z: {cont}")
        return self.avaliar_criterios(
            cont == 4,
            trajetoriaSuavizada[-1]['indicador'][1] - trajetoriaSuavizada[0]['indicador'][1] > 50,
            landmarks[5].z > landmarks[8].z,
            estados['indicador'],
            estados['polegar'],
            not estados['indicador_abaixado'],
            not estados['indicador_parcial'],
            not estados['medio'],
            not estados['anelar'],
            not estados['mindinho']
        )


class dedo_meio(LetraBase):
    def detectar_letras(self, estados, trajetoriaSuavizada, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        if len(trajetoria) > 5:
            return 0.0
        return self.avaliar_criterios(
            estados['medio'],
            not estados['medio_parcial'],
            not estados['medio_abaixado'],
            estados['indicador_parcial'],
            estados['anelar_parcial'],
            estados['indicador_parcial'],
            not estados['indicador'],
            not estados['anelar'],
            not estados['mindinho']
        )
    
class amor(LetraBase):
    def detectar_letras(self, estados, trajetoriaSuavizada, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        if len(trajetoria) > 5:
            return 0.0
        if info_mao == 'Left':
            polegar_correto = landmarks[4].x < landmarks[8].x
        else:
            polegar_correto = landmarks[4].x > landmarks[8].x
        return self.avaliar_criterios(
            polegar_correto,
            estados ['indicador'],
            estados ['polegar'],
            not estados ['medio'],
            not estados ['anelar'],
            not estados ['mindinho'],
            rotacao_final in ['tras']
        )
    
class joia(LetraBase):
    def detectar_letras(self, estados, trajetoriaSuavizada, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        if len(trajetoria) > 5:
            return 0.0
        return self.avaliar_criterios(
            estados ['polegar'],
            not estados['polegar_parcial'],
            not estados['polegar_abaixado'],
            estados['indicador_parcial'],
            estados['medio_parcial'],
            estados['anelar_parcial'],
            estados['mindinho_parcial'],
            not estados ['indicador'],
            not estados ['medio'],
            not estados ['anelar'],
            not estados ['mindinho'],
            rotacao_inicial in ['tras', 'frente', 'lado'],
            rotacao_final in ['frente', 'tras', 'lado']
        )
    
class sos(LetraBase):
    def detectar_letras(self, estados, trajetoriaSuavizada, landmarks, info_mao, rotacao_inicial = None, rotacao_final = None):
        if info_mao == 'Left':
            polegar_correto = landmarks[4].x < landmarks[2].x
        else:
            polegar_correto = landmarks[4].x > landmarks[2].x
        if len(trajetoria) < 5:
            return 0.0
        return self.avaliar_criterios(
            polegar_correto,
            #not estados ['indicador'],
            #not estados ['medio'],
            #not estados ['anelar'],
            #not estados ['mindinho'],
            trajetoriaSuavizada[-1]['indicador'][1] - trajetoriaSuavizada[0]['indicador'][1] > 30,
            rotacao_inicial in ['frente'],
            rotacao_final in ['frente']
        )
    
class enviar(LetraBase):
    def detectar_letras(self, estados, trajetoriaSuavizada, landmarks, info_mao, rotacao_inicial=None, rotacao_final=None):
        polegar_correto = polegar_correto = abs(landmarks[4].x - landmarks[2].x) > 0.08
        return self.avaliar_criterios(
            polegar_correto,
            not estados ['polegar'],
            estados ['indicador'],
            estados ['medio'],
            estados ['anelar'],
            estados ['mindinho'],
            rotacao_final in ['frente', 'diagonal']
        )
    
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
    if -0.045 < diff < 0.045: return 'lado'
    if info_mao == 'Left':
        if diff > 0.065: return 'tras'
        elif diff < -0.065: return 'frente'
    else:
        if diff > 0.065: return 'frente'
        elif diff < -0.065: return 'tras'
    return 'diagonal'

# Suaviza todos os pontos contentes em self.trajetoria, para suavizar o tremilique dos pontos
# Retorna um Dicionário
def suavizar_frame(trajetoria):
    nomes = trajetoria[0].keys()
    suavizado = {}

    for nome in nomes:
        xs, ys, zs = [], [], []
        for frame in trajetoria:
            if nome in frame:
                x, y, z = frame[nome]
                xs.append(x)
                ys.append(y)
                zs.append(z)
            
            if xs:
                suavizado[nome] = (
                    sum(xs) // len(xs),
                    sum(ys) // len(ys),
                    sum(zs) // len(zs)
                )

    return suavizado

def process_detector(frame, results, historico_frames, trajetoria, traj_suavizada):
    """
    Recebe um frame do OpenCV e retorna um 'pacote' de informações para detectar letra.
    """
    if results.multi_hand_landmarks:
        for idx, mao in enumerate(results.multi_hand_landmarks):
            info_mao = results.multi_handedness[idx].classification[0].label
            landmarks = mao.landmark
            coord = extrair_coordenadas(landmarks, frame)
            trajetoria.append(coord)

            if len(trajetoria) > 2:
                traj_suavizada.append(suavizar_frame(trajetoria))
                trajetoria.clear()
            
            if "rotacao_inicial" not in locals():
                diff = landmarks[17].x - landmarks[5].x
                rotacao_inicial = calcular_rotacao_horizontal(diff, info_mao)

            estados = LetraBase().estados(landmarks)
            diff = landmarks[17].x - landmarks[5].x
            rotacao_final = calcular_rotacao_horizontal(diff, info_mao)

            pacote = {
                "estados": estados,
                "trajetoria": list(traj_suavizada),
                "landmarks": landmarks,
                "info_mao": info_mao,
                "rot_ini": rotacao_inicial,
                "rot_fim": rotacao_final
            }

            # guarda no histórico (automaticamente descarta os mais antigos)
            historico_frames.append(pacote)
        return historico_frames

# Função para detectar a Letra
def detectar_letras(historico_frames):
    letras_detectadas = []
    for pacote in historico_frames:
        try:
            letras_detectadas.append(detectar(
                pacote["estados"],
                pacote["trajetoria"],
                pacote["landmarks"],
                pacote["info_mao"],
                pacote["rot_ini"],
                pacote["rot_fim"]
            ))
        except Exception as e:
            print("Erro ao detectar letra:", e)
            letras_detectadas.append('?')
    if letras_detectadas:
        print(letras_detectadas)
        # pega o mais comum (só 1 elemento), normalmente retornaria uma tupla, ex: ('C', 4) 
        letra = Counter(letras_detectadas).most_common(1)[0][0] 
        return letra
    
# Função simples pra reconhecer "padrões" de movimento
# valores dos pixels aumentam de: baixo -> cima e esquerda -> direita
def detectar(estados, trajetoriaSuavizada, landmarks, info_mao, rotacao_inicial, rotacao_final):
    print("Deslocamento Y: ", trajetoriaSuavizada[-1]['indicador'][1] - trajetoriaSuavizada[0]['indicador'][1])
    print("Deslocamento Z: ", landmarks[5].z - landmarks[8].z)
    print("Profundidade D: ", abs(landmarks[4].z - landmarks[12].z))
    print("Vertical D: ", landmarks[4].y - landmarks[12].y)
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
    'F': letra_F(),
    'G': letra_G(),
    'H': letra_H(),
    'I': letra_I(),
    'J': letra_J(),
    'K': letra_K(),
    'L': letra_L(),
    'M': letra_M(),
    'N': letra_N(),
    'O': letra_O(),
    'P': letra_P(),
    'Q': letra_Q(),
    'R': letra_R(),
    'S': letra_S(),
    'T': letra_T(),
    'U': letra_U(),
    'V': letra_V(),
    'W': letra_W(),
    'X': letra_X(),
    'Y': letra_Y(),
    'Z': letra_Z(),
    '🖕': dedo_meio(),
    '❤' : amor(),
    '👍' : joia(),
    '🆘': sos(),
    '🤚': enviar()
    }
    
    scores = {}
    for letra, detector in letras.items():
        try:
            score = detector.detectar_letras(estados, trajetoriaSuavizada, landmarks, info_mao, rotacao_inicial, rotacao_final)
            scores[letra] = score
        except Exception:
            scores[letra] = 0.0
    
    melhor_letra = max(scores, key = scores.get)
    
    print("Scores: ", scores)

    return melhor_letra

def movimento_parado(trajetoriaSuavizada):
    if len(trajetoriaSuavizada) < 15:
        return False
    # Cria uma lista por que o deque não suporta fatiamentos
    recentes = list(trajetoriaSuavizada)[-15:]
    tempo_parado = 0
    for i in range(14):
        dx = abs(recentes[i + 1]['centro'][0] - recentes[i]['centro'][0])
        dy = abs(recentes[i + 1]['centro'][1] - recentes[i]['centro'][1])
        dz = abs(recentes[i + 1]['centro'][2] - recentes[i]['centro'][2])
        if dx < 2.2 and dy < 2.2 and dz < 2.2:
            tempo_parado += 1
            print(tempo_parado)
    if tempo_parado > 9:
        return True 
    return False

def movimento_andando(trajetoriaSuavizada):
        if len(trajetoriaSuavizada) < 15:
            return False
        # Cria uma lista por que o deque não suporta fatiamentos
        recentes = list(trajetoriaSuavizada)[-15:]
        tempo_movendo = 0
        for i in range(14):
            dx = abs(recentes[i + 1]['centro'][0] - recentes[i]['centro'][0])
            dy = abs(recentes[i + 1]['centro'][1] - recentes[i]['centro'][1])
            dz = abs(recentes[i + 1]['centro'][2] - recentes[i]['centro'][2])
            if dx > 1.6 or dy > 1.6 or dz > 1.6:
                tempo_movendo += 1
        if tempo_movendo > 7:
            return True 
        return False