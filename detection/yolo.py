from ultralytics import YOLO

class YOLODetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect_objects(self, frame):
        results = self.model(frame)
        return results[0].boxes