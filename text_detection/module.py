import os

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

from paddleocr import PaddleOCR
import cv2

ocr = PaddleOCR(lang="en")

cap = cv2.VideoCapture(0)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

output_path = "outputs.mp4"
fourcc = cv2.VideoWriter.fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

if not cap.isOpened():
    print("Error establishing connection")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    height, width, _ = frame.shape

    results = ocr.ocr(frame)[0]

    if results:
        for line in results:
            box = line[0]

            text, score = line[1]
            if score < 0.7:
                continue

        top_left, top_right, bottom_right, bottom_left = box
        top_left = (int(top_left[0]), int(top_left[1]))
        bottom_right = (int(bottom_right[0]), int(bottom_right[1]))

        cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

    cv2.imshow("Text detection", frame)
    cv2.waitKey(0)

cap.release()
