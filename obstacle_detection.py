import cv2
import torch
from ultralytics import YOLO

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = YOLO("yolov8n.pt").to(device)

scale = 40


def detection_object(file_location: str):
    result = []
    capture = cv2.VideoCapture(file_location)

    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) / scale * 100)
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) / scale * 100)

    if not capture.isOpened():
        print("Error establishing connection")

    while capture.isOpened():
        ret, frame = capture.read()
        if not ret:
            break

        frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)
        predict_results = model.track(frame, persist=True, conf=0.3)

        for box in predict_results[0]:
            x1, y1, x2, y2 = box.boxes.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            cls = int(box.boxes.cls[0])
            class_name = model.names[cls]

            result.append([class_name, x1, y1, x2, y2])

    capture.release()
    return result


def generate_object_detection_prompt(objects: list[list[int]]) -> str:
    prompt = "You are given an image with several objects. Identify the objects based on the following coordinates:\n\n"
    for obj in objects:
        name = obj[0]
        x1 = obj[1]
        y1 = obj[2]
        x2 = obj[3]
        y2 = obj[4]
        prompt += f"Object: {name}, Coordinates: ({x1}, {y1}) to ({x2}, {y2})\n"
    prompt += "\nProvide a description of the objects found in the specified coordinates."
    return prompt
