import cv2
import easyocr
import serial
import re
import time
import torch
import numpy as np

print("CUDA available:", torch.cuda.is_available())

# База данни с валидни номера
VALID_IDS = {"CA1234BG", "CB5678SO", "TX9876NY", "CA5069MA", "CA5969MA"}

# Свързване към Micro:bit (COM5)
microbit = serial.Serial("COM5", 115200)

# OCR engine с GPU
reader = easyocr.Reader(['en'], gpu=True)


# Корекция на OCR грешки
def correct_plate(text):
    corrections = {'O': '0', 'Q': '0', 'I': '1', 'L': '1', 'S': '5', 'B': '8', 'Z': '2', 'G': '6'}
    return ''.join(corrections.get(c, c) for c in text.upper())


# Проверка на формата: 2 букви + 4 цифри + 2 букви
def is_valid_format(text):
    return re.match(r'^[A-Z]{2}[0-9]{4}[A-Z]{2}$', text) is not None


cap = cv2.VideoCapture(0)

plates_buffer = []
scan_count = 0
found_valid = False

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    results = reader.readtext(frame, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ')

    # комбинираме всички OCR резултати в една линия
    combined_text = "".join([t for (_, t, _) in results])
    combined_text = combined_text.replace(" ", "")
    corrected = correct_plate(combined_text)

    # рисуваме рамки за всеки OCR блок
    for bbox, text, conf in results:
        pts = np.array(bbox, dtype=np.int32).reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], isClosed=True, color=(255, 255, 0), thickness=2)
        cv2.putText(frame, text, tuple(pts[0][0]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    # проверка на комбинирания текст
    if is_valid_format(corrected):
        scan_count += 1
        plates_buffer.append(corrected)
        print(f"[{scan_count}] Засечен номер: {corrected}")

        if corrected in VALID_IDS:
            print("VALID:", corrected)
            microbit.write(b"VALID\n")
            plates_buffer.clear()
            scan_count = 0
            found_valid = True
            time.sleep(2)

    # ако стигнем 10 номера без валиден → INVALID
    if scan_count >= 10 and not found_valid:
        print("INVALID (след 10 номера)")
        microbit.write(b"INVALID\n")
        plates_buffer.clear()
        scan_count = 0
        time.sleep(2)

    # показваме брояча върху видеото
    cv2.putText(frame, f"Сканирани: {scan_count}/10", (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)

    cv2.imshow("Camera OCR", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("INVALID (прекратено от потребителя)")
        microbit.write(b"INVALID\n")
        plates_buffer.clear()
        scan_count = 0
        break

cap.release()
cv2.destroyAllWindows()
