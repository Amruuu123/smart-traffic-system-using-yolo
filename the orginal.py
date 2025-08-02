import cv2
import RPi.GPIO as GPIO
from time import sleep
import numpy as np

# GPIO Configuration
LED_RED_1, LED_GREEN_1 = 2, 3
LED_RED_2, LED_GREEN_2 = 4, 27
RS, RW, E = 16, 12, 1
DB4, DB5, DB6, DB7 = 23, 18, 15, 14

GPIO.setmode(GPIO.BCM)
GPIO.setup([LED_RED_1, LED_GREEN_1, LED_RED_2, LED_GREEN_2], GPIO.OUT)
GPIO.setup([RS, RW, E, DB4, DB5, DB6, DB7], GPIO.OUT)

# Initialize LCD
def lcd_command(data, rs=0):
    GPIO.output(RS, rs)
    for pin, val in zip([DB7, DB6, DB5, DB4], [(data >> i) & 1 for i in range(4, 8)]):
        GPIO.output(pin, val)
    GPIO.output(E, GPIO.HIGH)
    sleep(0.001)
    GPIO.output(E, GPIO.LOW)

    for pin, val in zip([DB7, DB6, DB5, DB4], [(data >> i) & 1 for i in range(4)]):
        GPIO.output(pin, val)
    GPIO.output(E, GPIO.HIGH)
    sleep(0.001)
    GPIO.output(E, GPIO.LOW)

def lcd_init():
    lcd_command(0x33)  # Init
    lcd_command(0x32)  # 4-bit mode
    lcd_command(0x28)  # Function set
    lcd_command(0x0C)  # Display on
    lcd_command(0x06)  # Entry mode
    lcd_command(0x01)  # Clear display

def lcd_write(text):
    lcd_command(0x01)  # Clear display
    for char in text:
        lcd_command(ord(char), rs=1)

lcd_init()

# Load YOLO Tiny v4
net = cv2.dnn.readNet("yolov4-tiny.weights", "yolov4-tiny.cfg")
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getUnconnectedOutLayersNames()

# Process Video Streams
def process_camera(camera_source, camera_id):
    cap = cv2.VideoCapture(camera_source)
    if not cap.isOpened():
        print(f"Camera {camera_id} not available.")
        return 0

    ret, frame = cap.read()
    if not ret or frame is None:
        print(f"No frame captured from Camera {camera_id}.")
        cap.release()
        return 0

    # Display the camera preview
    cv2.imshow(f'Camera {camera_id} Preview', cv2.resize(frame, (600, 400)))

    # YOLO detection
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    detections = net.forward(layer_names)

    count = 0
    for output in detections:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            if scores[class_id] > 0.5 and classes[class_id] in ["car", "truck", "bus", "motorbike"]:
                count += 1

    cap.release()
    return count

# Main Program
try:
    while True:
        traffic_count_1 = process_camera(0, "Camera 1")  # Local Camera
        traffic_count_2 = process_camera('http://192.168.198.2:8080/video', "Camera 2")  # Server Camera

        print(f"Camera 1 Traffic: {traffic_count_1}, Camera 2 Traffic: {traffic_count_2}")

        if traffic_count_1 > traffic_count_2:
            GPIO.output([LED_RED_1, LED_GREEN_2], GPIO.HIGH)
            GPIO.output([LED_GREEN_1, LED_RED_2], GPIO.LOW)
            lcd_write("Road 1: High Traffic")
        elif traffic_count_2 > traffic_count_1:
            GPIO.output([LED_RED_2, LED_GREEN_1], GPIO.HIGH)
            GPIO.output([LED_GREEN_2, LED_RED_1], GPIO.LOW)
            lcd_write("Road 2: High Traffic")
        else:
            GPIO.output([LED_GREEN_1, LED_GREEN_2], GPIO.HIGH)
            GPIO.output([LED_RED_1, LED_RED_2], GPIO.LOW)
            lcd_write("Traffic Equal")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
finally:
    cv2.destroyAllWindows()
