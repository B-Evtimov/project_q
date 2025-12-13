#  Automatic License Plate Recognition and Access Control with Micro:bit

##  Overview
This project demonstrates an integrated system for **automatic license plate recognition** using Python (OCR with EasyOCR + OpenCV) and **hardware control** via a BBC Micro:bit.  
The goal is to simulate an **automated access control system** where recognized license plates trigger physical actions such as LEDs, a servo motor, and sound alarms.

---

##  Components

### Python (OCR + Control)
- Uses **EasyOCR** and **OpenCV** to detect and read license plates from a camera.
- Corrects common OCR mistakes (O→0, I→1, S→5, etc.).
- Validates plate format: `AA9999AA` (2 letters + 4 digits + 2 letters).
- Compares against a **database of valid plates and owners** (`valid_db.py`).
- Sends commands to Micro:bit via **USB serial**:
  - `VALID:<plate>:<owner>\n`
  - `INVALID\n`

### Micro:bit (Hardware Control)
- Receives commands from Python over serial.
- Controls two LEDs:
  - **Green LED** → lights up when a valid plate is detected (while servo is active).
  - **Red LED** → lights up by default, after servo returns, or immediately on invalid plate.
- Controls a **servo motor**:
  - Rotates to 90° on valid plate, returns to 0° after 5 seconds.
- Plays **sound signals**:
  - Short tone for valid plate.
  - Alarm sequence for invalid plate (15 seconds).
- Displays information on the LED matrix:
  - `"VALID"` + plate number + owner name.
  - `"INVALID"` for unrecognized plates.
- Manual override:
  - **Button A** → triggers VALID logic.
  - **Button B** → triggers INVALID logic.

---

##  Workflow
1. Camera captures a license plate.
2. Python OCR script processes the image and validates the plate.
3. If plate is valid:
   - Sends `VALID:<plate>:<owner>` to Micro:bit.
   - Micro:bit shows `"VALID"`, plate, and owner.
   - Green LED lights up, servo rotates, then returns after 5s.
   - Red LED lights up again after reset.
4. If plate is invalid:
   - Sends `INVALID` to Micro:bit.
   - Micro:bit shows `"INVALID"`.
   - Red LED lights up immediately.
   - Alarm sounds for 15s.
5. Buttons A/B allow manual triggering of the same logic.


---

##  Demonstration
- **Valid plate** → Green LED, servo rotates, owner name displayed, then returns to red LED.  
- **Invalid plate** → Red LED + alarm for 15 seconds.  
- **Manual override** → Buttons A/B simulate the same behavior without Python.

---

##  Requirements
- Python 3.9+
- Libraries: `easyocr`, `opencv-python`, `torch`, `numpy`, `pyserial`
- BBC Micro:bit with USB connection
- Servo motor + LEDs connected to Micro:bit pins

---

##  Purpose
This project is designed as a **practical demonstration** of combining:
- Computer vision (OCR)
- Hardware control (Micro:bit)
- Database integration
- Real-time feedback with LEDs, servo, and sound

It can be used for **educational purposes**, **IoT prototypes**, or as a foundation for **access control systems**.

---

##  Author
Developed by **Boris Evtimov**  
Focused on scalable, practical solutions combining **Python, electronics, and cloud-ready architectures**.
