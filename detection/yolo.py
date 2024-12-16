from ultralytics import YOLO


class YOLODetector:
    def __init__(self, model_path: str, conf_threshold: float = 0.8, iou_threshold: float = 0.9):
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold

    def detect_objects(self, frame: str) -> list:
        """
        Detect objects in the frame using YOLO model

        Args:
            frame (str): Path to the frame image
        Returns:
            list: List of bounding boxes for detected objects
        """
        results = self.model.track(
            frame, persist=True, conf=self.conf_threshold, iou=self.iou_threshold
        )
        return results[0].boxes
