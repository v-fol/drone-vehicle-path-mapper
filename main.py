import numpy as np
import math
import cv2

from preprocessing.drone_data import load_drone_data

from detection.yolo import YOLODetector

from geoprocessing.coordinates import adjust_lat_long_with_direction
from geoprocessing.map_utils import export_for_geo_json

from utils import clear_directory
from config import Config


class CarTracker:
    def __init__(self):
        self.cap = cv2.VideoCapture(Config.VIDEO_PATH)
        self.car_geo_paths = {}
        self.car_geo_json_paths = []
        self.car_colors = {}
        self.car_ids = []
        self.drone_data = load_drone_data(Config.DRONE_DATA_PATH)
        self.classes = {
            0: "boat",
            1: "bus",
            2: "car",
            3: "construction vehicle",
            4: "motorcycle",
            5: "person",
            6: "train",
            7: "truck",
            8: "uai",
            9: "uap",
        }  # class ids from the yolo model (detector.model.names)

    def __enter__(self):
        clear_directory(Config.CAR_IMAGE_PATH)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.car_geo_json_paths:
            export_for_geo_json(self.car_geo_json_paths, Config.GEOJSON_OUTPUT_PATH)
        self.cap.release()

    def map_to_coordinates(
        self,
        x: int,
        y: int,
        frame_idx: int,
        drone_info: dict,
    ) -> tuple:
        """
        Map the pixel coordinates of a car to its corresponding latitude and longitude.

        Args:
            x: The x-coordinate of the car
            y: The y-coordinate of the car
            frame_idx: The index of the current frame
            drone_info: The drone information
        Returns:
            tuple: The latitude and longitude of the car
        """

        drone_lat = drone_info["latitude"]
        drone_lon = drone_info["longitude"]
        altitude = drone_info["abs_alt"]  # Absolute altitude in meters
        focal_length = drone_info["focal_len"]  # Focal length in mm
        gb_yaw = (
            drone_info["gb_yaw"] + 180
        )  # Gimbal yaw in degrees (0 - 360), we add 180 to convert it to absolute value

        if gb_yaw not in range(0, 360):
            raise ValueError("Gimbal yaw should be in the range of 0-360 degrees")

        sensor_width = Config.SENSOR_WIDTH
        sensor_height = sensor_width / (
            Config.CAMERA_RESOLUTION_WIDTH / Config.CAMERA_RESOLUTION_HEIGHT
        )

        # Calculate the horizontal and vertical FOVs (in radians)
        fov_horizontal = 2 * math.atan(sensor_width / (2 * focal_length))
        fov_vertical = 2 * math.atan(sensor_height / (2 * focal_length))

        # Calculate the ground coverage width and height
        ground_width = 2 * (altitude * math.tan(fov_horizontal / 2))  # in meters
        ground_height = 2 * (altitude * math.tan(fov_vertical / 2))  # in meters

        # Calculate the pixel-to-meter conversion factor
        pixel_to_meter_x = ground_width / Config.CAMERA_RESOLUTION_WIDTH
        pixel_to_meter_y = ground_height / Config.CAMERA_RESOLUTION_HEIGHT

        # Calculate the center of the image (in pixels)
        center_x = Config.CAMERA_RESOLUTION_WIDTH / 2
        center_y = Config.CAMERA_RESOLUTION_HEIGHT / 2

        # Calculate the displacement in pixels (relative to center)
        displacement_x_pixels = x - center_x
        displacement_y_pixels = y - center_y

        # Convert the displacement from pixels to meters
        displacement_x_meters = displacement_x_pixels * pixel_to_meter_x
        displacement_y_meters = displacement_y_pixels * pixel_to_meter_y

        # Calculate the straight-line displacement (Euclidean distance)
        displacement = math.sqrt(displacement_x_meters**2 + displacement_y_meters**2)

        # If the yaw for the last M frames did cahge more than N degrees we reset the displacement
        # to avoid dispacement when the drone is rotating fast
        if frame_idx > Config.DISPLACEMENT_FRAME_COUNT_THRESHOLD:
            yaw_changes = []
            for i in range(
                frame_idx - Config.DISPLACEMENT_FRAME_COUNT_THRESHOLD, frame_idx
            ):
                yaw_changes.append(
                    abs(self.drone_data[i]["gb_yaw"] - self.drone_data[i - 1]["gb_yaw"])
                )
            if max(yaw_changes) > Config.DISPLACEMENT_YAW_THRESHOLD:
                displacement = 0

        new_lat, new_lon = adjust_lat_long_with_direction(
            drone_lat, drone_lon, displacement, gb_yaw
        )

        return new_lat, new_lon

    def generate_car_geo_json(
        self,
        car_id: int,
        lat: float,
        lon: float,
        confidence: float,
        drone_info: dict,
        delay: bool,
    ) -> None:
        """
        Generate GeoJSON data for a car's current position, wich is used in Mapbox visualization.

        Args:
            car_id: The ID of the car
            lat: The latitude of the car
            lon: The longitude of the car
            confidence: The confidence score of the detection
            drone_info: The drone information
            delay: Whether to add a delay to the car's position dot
        """
        self.car_geo_json_paths.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "vehicle_id": f"vehicle_{car_id}",
                    "timestamp": f"2024-12-09T{str(drone_info['timestamp'][:-3])}Z",
                    "color": f"#{self.car_colors[car_id][0]:02X}{self.car_colors[car_id][1]:02X}{self.car_colors[car_id][2]:02X}",
                    "frame_time": drone_info["timestamp"],
                    "confidence": f"{confidence:.4f}",
                    "delay": delay,
                },
            }
        )

    def save_vehicle_image(self, car_id: int, car_img: np.ndarray) -> None:
        """
        Save the image of a found vehicle to the disk.

        Args:
            car_id: The ID of the vehicle
            car_img: The image of the vehicle
        """
        filename = f"{Config.CAR_IMAGE_PATH}/vehicle_{car_id}.jpg"
        cv2.imwrite(filename, car_img)

    def create_vehicle_entry(
        self,
        car_id: int,
        frame: np.ndarray,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
    ) -> None:
        """
        Create and add to the tracker a new entry for a vehicle that has been detected.

        Args:
            car_id: The ID of the vehicle
            frame: The current frame
            x1: The x-coordinate of the top-left corner of the vehicle bounding box
            y1: The y-coordinate of the top-left corner of the vehicle bounding box
            x2: The x-coordinate of the bottom-right corner of the vehicle bounding box
            y2: The y-coordinate of the bottom-right corner of the vehicle bounding
        """
        y1_pad = max(0, y1 - Config.IMAGE_PADDING)
        y2_pad = min(frame.shape[0], y2 + Config.IMAGE_PADDING)
        x1_pad = max(0, x1 - Config.IMAGE_PADDING)
        x2_pad = min(frame.shape[1], x2 + Config.IMAGE_PADDING)
        car_img = frame[y1_pad:y2_pad, x1_pad:x2_pad].copy()

        self.save_vehicle_image(car_id, car_img)

        self.car_colors[car_id] = (
            np.random.randint(0, 255),
            np.random.randint(0, 255),
            np.random.randint(0, 255),
        )
        self.car_ids.append(car_id)

    def run_recognition(self, detector: YOLODetector) -> None:
        """
        Run the car recognition pipeline
        In this pipeline, we process the video frames and detect cars using YOLO.
        We then extract the color histogram of each car and compare it with the existing car histograms.
        If a similar car is found, we update the car's position in the GeoJSON data.
        If a similar car is not found, we create a new car entry in the tracker.
        After processing all the frames, we save the GeoJSON data, image data, and other map data.
        """
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:  # If the frame is not read correctly, break the loop
                break

            frame_idx = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
            if frame_idx >= len(self.drone_data):
                break  # Break the loop if we have processed all the drone data

            drone_info = self.drone_data[frame_idx]
            detections = detector.detect_objects(frame)

            box_index = 0
            for box in detections:
                if not box.id:
                    continue

                class_id = box.cls[0]
                if class_id not in Config.INTERESTED_CLASS_IDS:
                    continue  # Skip the class if it is not a vehicle

                x1, y1, x2, y2 = box.xyxy[
                    0
                ]  # Extracting the coordinates from the detection box (xyxy format)
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                # Skip the detection if it is too close to the frame
                if (
                    x1 < Config.CLOSE_TO_FRAME_PIXELS
                    or y1 < Config.CLOSE_TO_FRAME_PIXELS
                    or x2 > frame.shape[1] - Config.CLOSE_TO_FRAME_PIXELS
                    or y2 > frame.shape[0] - Config.CLOSE_TO_FRAME_PIXELS
                ):
                    continue

                car_id = int(box.id[0])

                if car_id and car_id not in self.car_ids:
                    self.create_vehicle_entry(car_id, frame, x1, y1, x2, y2)

                lat, lon = self.map_to_coordinates(
                    (x1 + x2) // 2, (y1 + y2) // 2, frame_idx, drone_info
                )

                # Add the car's current position to the GeoJSON feature collection
                self.generate_car_geo_json(
                    car_id,
                    lat,
                    lon,
                    box.conf[0],
                    drone_info,
                    delay=True
                    if box_index == 0
                    else False,  # add delay only to one point on the frame
                )
                box_index += 1

                # For other maps (e.g., kepler.gl or folium)
                if car_id not in self.car_geo_paths:
                    self.car_geo_paths[car_id] = []
                self.car_geo_paths[car_id].append((lat, lon))


if __name__ == "__main__":
    with CarTracker() as tracker:
        detector = YOLODetector(
            Config.YOLO_MODEL_PATH,
            conf_threshold=Config.CONFIDENCE_THRESHOLD,
            iou_threshold=Config.IOU_THRESHOLD,
        )
        tracker.run_recognition(detector)
