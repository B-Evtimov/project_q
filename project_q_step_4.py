import cv2
import easyocr
import serial
import re
import time
import torch

# Проверка дали GPU е достъпен
print("CUDA available:", torch.cuda.is_available())

# База данни с валидни номера
VALID_IDS = {"CA 5969 MA", "CB5678SO", "TX9876NY"}

# Свързване към Micro:bit (COM5)
microbit = serial.Serial("COM5", 115200)

# OCR engine с GPU
reader = easyocr.Reader(['en'], gpu=True)

# Корекция на OCR грешки
def correct_plate(text):
    corrections = {'O':'0','Q':'0','I':'1','L':'1','S':'5','B':'8','Z':'2','G':'6'}
    return ''.join(corrections.get(c,c) for c in text.upper())

# Проверка на формата: 2 букви + 4 цифри + 2 букви
def is_valid_format(text):
    return re.match(r'^[A-Z]{2}[0-9]{4}[A-Z]{2}$', text) is not None

# Камера
cap = cv2.VideoCapture(0)

plates_buffer = []
scan_count = 0
found_valid = False

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    results = reader.readtext(frame, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ')
    for bbox, text, conf in results:
        raw = text.upper().replace(" ", "")
        corrected = correct_plate(raw)

        if is_valid_format(corrected):
            scan_count += 1
            plates_buffer.append(corrected)
            print(f"[{scan_count}] Засечен номер: {corrected}")

            # отбелязване на правоъгълник
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))
            cv2.rectangle(frame, top_left, bottom_right, (0,255,0), 2)
            cv2.putText(frame, corrected, (top_left[0], top_left[1]-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            # ако е валиден → веднага VALID
            if corrected in VALID_IDS:
                print("VALID:", corrected)
                microbit.write(b"VALID\n")
                plates_buffer.clear()
                scan_count = 0
                found_valid = True
                time.sleep(2)
                break

    # ако стигнем 10 номера без валиден → INVALID
    if scan_count >= 10 and not found_valid:
        print("INVALID (след 10 номера)")
        microbit.write(b"INVALID\n")
        plates_buffer.clear()
        scan_count = 0
        time.sleep(2)

    cv2.imshow("Camera OCR", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        # ако човек прекрати с q → INVALID
        print("INVALID (прекратено от потребителя)")
        microbit.write(b"INVALID\n")
        plates_buffer.clear()
        scan_count = 0
        break

cap.release()
cv2.destroyAllWindows()