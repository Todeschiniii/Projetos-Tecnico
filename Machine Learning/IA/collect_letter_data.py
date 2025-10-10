import cv2
import csv
import mediapipe as mp
import argparse
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

parser = argparse.ArgumentParser()
parser.add_argument('--class-name', type=str, required=True)
parser.add_argument('--collect-for', type=int, default=20)
parser.add_argument('--start-delay', type=int, default=5)
parser.add_argument('--file-name', type=str, default='letters_data.csv')
args = parser.parse_args()

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Erro: Não foi possível acessar a webcam.")
    exit()

print(f"Aguardando {args.start_delay}s antes de começar coleta para letra {args.class_name}...")
time.sleep(args.start_delay)
start = time.time()

with open(args.file_name, 'a', newline='') as f:
    writer = csv.writer(f)
    while time.time() - start < args.collect_for:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao capturar o frame.")
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = hands.process(frame_rgb)
        if res.multi_hand_landmarks:
            lm = res.multi_hand_landmarks[0].landmark
            row = [args.class_name] + [coord for lm_i in lm for coord in (lm_i.x, lm_i.y, lm_i.z)]
            writer.writerow(row)
            cv2.putText(frame, f"Coletando: {args.class_name}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Coleta Libras", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Coleta interrompida pelo usuário.")
            break

cap.release()
cv2.destroyAllWindows()
print("Coleta finalizada.")