import cv2
import easyocr
import serial
import re
import time
import torch
import numpy as np

# Import the database from a separate file
from valid_db import VALID_DB

print("CUDA available:", torch.cuda.is_available())

# Connecting to Micro:bit (COM5)
microbit = serial.Serial("COM5", 115200)

# OCR engine with GPU
reader = easyocr.Reader(['en'], gpu=True)

def correct_plate(text):
    corrections = {'O':'0','Q':'0','I':'1','L':'1','S':'5','B':'8','Z':'2','G':'6'}
    return ''.join(corrections.get(c,c) for c in text.upper())

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
    combined_text = "".join([t for (_, t, _) in results]).replace(" ", "")
    corrected = correct_plate(combined_text)

    for bbox, text, conf in results:
        pts = np.array(bbox, dtype=np.int32).reshape((-1,1,2))
        cv2.polylines(frame, [pts], isClosed=True, color=(255,255,0), thickness=2)
        cv2.putText(frame, text, tuple(pts[0][0]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)

    if is_valid_format(corrected):
        scan_count += 1
        plates_buffer.append(corrected)
        print(f"[{scan_count}] Засечен номер: {corrected}")

        if corrected in VALID_DB:
            owner = VALID_DB[corrected]
            print(f"VALID: {corrected} ({owner})")
            msg = f"VALID:{corrected}:{owner}\n"
            microbit.write(msg.encode("utf-8"))
            plates_buffer.clear()
            scan_count = 0
            found_valid = True
            time.sleep(2)

    if scan_count >= 10 and not found_valid:
        print("INVALID (след 10 номера)")
        microbit.write(b"INVALID\n")
        plates_buffer.clear()
        scan_count = 0
        time.sleep(2)

    cv2.putText(frame, f"Сканирани: {scan_count}/10", (30,40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,255), 2)

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
#using db from file valid_db.py
