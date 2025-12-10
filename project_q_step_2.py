import cv2
import easyocr
import re

# Инициализация на OCR четеца
reader = easyocr.Reader(['en'])

# Стартиране на камерата
cap = cv2.VideoCapture(0)

print("Натисни 'q' за изход.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # OCR върху текущия кадър
    results = reader.readtext(frame)

    for (bbox, text, prob) in results:
        # Филтър за регистрационни номера (букви и цифри, 6–9 символа)
        if re.match(r'^[A-Z0-9\-]{6,9}$', text.replace(" ", "")):
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))

            cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(frame, text, top_left, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

            print(f"📸 Разпознат номер: {text}")

    cv2.imshow("Камера", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()