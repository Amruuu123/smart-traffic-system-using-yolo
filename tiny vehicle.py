import cv2
import RPi.GPIO as GPIO
from time import sleep
import numpy as np

# GPIO Configuration
LED_RED_1, LED_GREEN_1 = 2, 3
LED_RED_2, LED_GREEN_2 = 4, 17
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

# Load YOLO Tiny
net = cv2.dnn.readNet("yolov3-tiny.weights", "yolov3-tiny.cfg")
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getUnconnectedOutLayersNames()

# Process Video Streams
def process_camera(cam_id):
    cap = cv2.VideoCapture(cam_id)
    if not cap.isOpened():
        print(f"Camera {cam_id} not available.")
        return 0
    _, frame = cap.read()
    height, width = frame.shape[:2]
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
        count1 = process_camera(0)
        count2 = process_camera(1)
        print(f"Road 1: {count1}, Road 2: {count2}")
        if count1 > count2:
            GPIO.output([LED_RED_1, LED_GREEN_2], GPIO.HIGH)
            GPIO.output([LED_GREEN_1, LED_RED_2], GPIO.LOW)
            lcd_write("Road 1: High Traffic")
        elif count2 > count1:
            GPIO.output([LED_RED_2, LED_GREEN_1], GPIO.HIGH)
            GPIO.output([LED_GREEN_2, LED_RED_1], GPIO.LOW)
            lcd_write("Road 2: High Traffic")
        else:
            GPIO.output([LED_GREEN_1, LED_GREEN_2], GPIO.HIGH)
            GPIO.output([LED_RED_1, LED_RED_2], GPIO.LOW)
            lcd_write("Traffic Equal")
        sleep(5)

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
