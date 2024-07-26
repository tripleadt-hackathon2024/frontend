import cv2
import torch
from paddleocr import PaddleOCR
from ultralytics import YOLO

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = YOLO("yolov8n.pt", verbose=False).to(device)
ocr = PaddleOCR(lang="en", use_gpu=False, show_log=False)
scale = 40


def detection_object(file_location: str):
    object_result = []
    text_result = []
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
        obstacle_predict_results = model.track(frame, persist=True, conf=0.3)
        text_predict_results = ocr.ocr(frame)[0]

        for obstacle_box in obstacle_predict_results[0]:
            x1, y1, x2, y2 = obstacle_box.boxes.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            cls = int(obstacle_box.boxes.cls[0])
            class_name = model.names[cls]
            object_result.append([class_name, x1, y1, x2, y2])

        if text_predict_results:
            for line in text_predict_results:
                print(line)
                text_box = line[0]

                text, score = line[1]

                if score < 0.7:
                    continue

                top_left, top_right, bottom_right, bottom_left = text_box
                x1, y1 = int(top_left[0]), int(top_left[1])
                x2, y2 = int(bottom_right[0]), int(bottom_right[1])
                text_result.append([text, x1, y1, x2, y2])
    capture.release()
    return object_result, text_result


def generate_object_detection_prompt(objects: list[list[str, int, int, int]],
                                     texts: list[list[str, int, int, int]]) -> str:
    prompt = (
        "You are given an image with several objects and text. Identify the objects moving path and text based on the "
        "following coordinates:\n\n")
    for obj in objects:
        name, x1, y1, x2, y2 = obj
        prompt += f"Object: {name}, Coordinates: ({x1}, {y1}) to ({x2}, {y2})\n"
    for text in texts:
        text, x1, y1, x2, y2 = text
        prompt += f"Text: {text}, Coordinates: ({x1}, {y1}) to ({x2}, {y2})\n"
        prompt += "\nProvide a description of the objects found in the specified coordinates."
    return prompt
