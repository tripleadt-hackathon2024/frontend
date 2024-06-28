from ultralytics import YOLO

yolo = YOLO("yolov8x.pt")

yolo.track(source=0, show=True, persist=True)