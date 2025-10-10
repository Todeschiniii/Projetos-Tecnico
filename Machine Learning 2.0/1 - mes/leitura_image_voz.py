# Exemplo simples de leitura de texto em imagem (OCR)
# usando pytesseract e Pillow

import os
import pytesseract
from PIL import Image
import pyttsx3

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Caminho da Imagem
caminho_image = os.path.join(os.path.dirname(__file__), "feira.jpg")

# --- ETAPA 1: Ler texto da imagem ---
image = Image.open(caminho_image)
texto = pytesseract.image_to_string(image, lang = 'eng')

# --- ETAPA 2: Exibir texto reconhecido ---
print("Texto encontrado na imagem: ")
print("=" * 40)
print(texto)
print("=" * 40)

# --- ETAPA 3: Converter texto em fala ---
motor = pyttsx3.init()
motor.setProperty('rate', 170) # Velocidade da Fala
motor.setProperty('volume', 1.0) # Volume da Fala

print("🔊 Lendo o texto em voz alta...")
motor.say(texto)
motor.runAndWait()