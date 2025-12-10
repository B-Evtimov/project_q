import cv2
import easyocr
import re
import time
import torch

# Проверка за GPU
print("Използва ли се GPU:", torch.cuda.is_available())

# База данни с валидни номера (без интервали)
valid_ids = {"CA1234", "BG5678", "SOFIA99", "B123456", "X9Z8Y7"}

# Инициализация на OCR четеца с GPU
reader = easyocr.Reader(['en'], gpu=True)

# Стартиране на камерата
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 90)

print("Натисни 'q' за изход.")
print("Сканиране на максимум 10 номера...")

found_valid = False
recognized_plate = None
scan_count = 0
last_scan_time = time.time()

while scan_count < 10:
    ret, frame = cap.read()
    if not ret:
        break

    current_time = time.time()
    if current_time - last_scan_time >= 1:
        results = reader.readtext(frame)

        for (bbox, text, prob) in results:
            raw_plate = text.upper()  # Оригинален текст с интервали
            clean_plate = raw_plate.replace(" ", "")  # Без интервали за проверка

            if re.match(r'^[A-Z0-9\-]{6,9}$', clean_plate):
                (top_left, top_right, bottom_right, bottom_left) = bbox
                top_left = tuple(map(int, top_left))
                bottom_right = tuple(map(int, bottom_right))

                # Очертаване и надпис
                cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
                cv2.putText(frame, raw_plate, top_left, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

                print(f"📸 Разпознат номер: {raw_plate}")
                scan_count += 1
                last_scan_time = current_time

                if clean_plate in valid_ids:
                    found_valid = True
                    recognized_plate = clean_plate
                    break

    cv2.imshow("Камера", frame)

    if found_valid:
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Резултат
if found_valid:
    print("VALID")
    print(f"номер = {recognized_plate}")
else:
    print("INVALID")