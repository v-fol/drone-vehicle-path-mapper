import numpy as np
import math
import cv2

from preprocessing.drone_data import load_drone_data

from detection.yolo import YOLODetector
from detection.histogram import compute_color_histogram, compare_histograms

from geoprocessing.coordinates import adjust_lat_long_with_direction
from geoprocessing.map_utils import export_for_geo_json

from utils import clear_directory
from config import Config


class CarTracker:
    def __init__(self):
        self.car_counter = 0
        self.car_histograms = {}
        self.car_geo_paths = {}
        self.car_geo_json_paths = []
        self.car_colors = {}
        self.geo_paths = {}
        self.drone_data = load_drone_data(Config.DRONE_DATA_PATH)
        self.confidence_threshold = 0.8
        self.max_similarity = 0.65
        self.interested_class_ids = [2, 3, 4, 5, 8]
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
        }

    def map_to_coordinates(
        self,
        x,
        y,
        frame_idx,
        drone_info,
        resolution_width=1920,
        resolution_height=1080,
        aspect_ratio=16 / 9,
    ) -> tuple:
        """
        Map the pixel coordinates of a car to its corresponding latitude and longitude.

        :param x: The x-coordinate of the car
        :param y: The y-coordinate of the car
        :param frame_idx: The index of the current frame
        :param drone_info: The drone information
        :param resolution_width: The width of the frame in pixels
        :param resolution_height: The height of the frame in pixels
        :param aspect_ratio: The aspect ratio of the frame
        :return: A tuple containing the latitude and longitude of the car
        """

        drone_lat = drone_info["latitude"]
        drone_lon = drone_info["longitude"]
        altitude = drone_info["abs_alt"]  # Absolute altitude in meters
        focal_length = drone_info["focal_len"]  # Focal length in mm
        gb_yaw = drone_info["gb_yaw"]

        sensor_width = 6  # mm
        sensor_height = sensor_width / aspect_ratio  # mm (aspect ratio = 16:9)

        # Calculate the horizontal and vertical FOVs (in radians)
        fov_horizontal = 2 * math.atan(sensor_width / (2 * focal_length))
        fov_vertical = 2 * math.atan(sensor_height / (2 * focal_length))

        # Calculate the ground coverage width and height
        ground_width = 2 * (altitude * math.tan(fov_horizontal / 2))  # in meters
        ground_height = 2 * (altitude * math.tan(fov_vertical / 2))  # in meters

        # Calculate the pixel-to-meter conversion factor
        pixel_to_meter_x = ground_width / resolution_width
        pixel_to_meter_y = ground_height / resolution_height

        # Calculate the center of the image (in pixels)
        center_x = resolution_width / 2
        center_y = resolution_height / 2

        # Calculate the displacement in pixels (relative to center)
        displacement_x_pixels = x - center_x
        displacement_y_pixels = y - center_y

        # Convert the displacement from pixels to meters
        displacement_x_meters = displacement_x_pixels * pixel_to_meter_x
        displacement_y_meters = displacement_y_pixels * pixel_to_meter_y

        # Calculate the straight-line displacement (Euclidean distance)
        displacement = math.sqrt(
            displacement_x_meters ** 2 + displacement_y_meters ** 2
        )

        # if the yaw for the last 10 frames did cahge more than 10 degrees we need to reset the displacement
        frame_range = 10
        if frame_idx > frame_range:
            yaw_changes = []
            for i in range(frame_idx - frame_range, frame_idx):
                yaw_changes.append(
                    abs(self.drone_data[i]["gb_yaw"] - self.drone_data[i - 1]["gb_yaw"])
                )
            if max(yaw_changes) > 3:
                displacement = 0

        new_lat, new_lon = adjust_lat_long_with_direction(
            drone_lat,
            drone_lon,
            displacement,
            gb_yaw + 180,  # 180 is added to convert the drone value to absolute value
        )

        return new_lat, new_lon

    def find_similar_car(self, car_hist, look_for_last=5) -> tuple:
        """
        Find a similar car in the existing car histogram.

        :param car_hist: The color histogram of the car
        :param look_for_last: The number of last found cars to compare with
        :return: A tuple containing a boolean indicating if a similar car was found and the ID of the car
        """
        car_found = False
        car_id = None
        simolarity_dict = {}

        loop = 0
        for existing_car_id, hist in reversed(self.car_histograms.items()):
            if loop > look_for_last:
                break
            similarity = compare_histograms(car_hist, hist)
            simolarity_dict[existing_car_id] = similarity
            loop += 1

        # if the similarity is higher than the threshold, assign the car ID
        if len(simolarity_dict) > 0:
            max_sim = max(simolarity_dict.values())
            if max_sim > self.max_similarity:
                car_id = max(simolarity_dict, key=simolarity_dict.get)
                self.car_histograms[car_id] = car_hist
                car_found = True
        return car_found, car_id

    def create_new_car(
        self, car_id, car_hist, frame, x1, y1, x2, y2, car_image_path, padding=20
    ) -> int:
        """
        Create a new car entry in the tracker.

        :param car_id: The ID of the car
        :param car_hist: The color histogram of the car
        :param frame: The current frame
        :param x1: The x-coordinate of the top-left corner of the car bounding box
        :param y1: The y-coordinate of the top-left corner of the car bounding box
        :param x2: The x-coordinate of the bottom-right corner of the car bounding box
        :param y2: The y-coordinate of the bottom-right corner of the car bounding box
        :param padding: The padding to add to the bounding
        """
        self.car_counter += 1
        car_id = self.car_counter
        # Make the box slightly bigger by adding padding
        y1_pad = max(0, y1 - padding)
        y2_pad = min(frame.shape[0], y2 + padding)
        x1_pad = max(0, x1 - padding)
        x2_pad = min(frame.shape[1], x2 + padding)
        car_img = frame[y1_pad:y2_pad, x1_pad:x2_pad].copy()

        # Save the image
        filename = f"{car_image_path}/vehicle_{car_id}.jpg"
        cv2.imwrite(filename, car_img)

        self.car_histograms[car_id] = car_hist
        self.car_colors[car_id] = (
            np.random.randint(0, 255),
            np.random.randint(0, 255),
            np.random.randint(0, 255),
        )
        return car_id

    def generate_car_geo_json(
        self, car_id, lat, lon, confidence, drone_info, delay
    ) -> None:
        """
        Generate GeoJSON data for a car's current position, wich is used in Mapbox visualization.

        :param car_id: The ID of the car
        :param lat: The latitude of the car
        :param lon: The longitude of the car
        :param confidence: The confidence of the detection
        :param drone_info: The drone information

        """
        # if car_id not in self.car_geo_json_paths:
        #     self.car_geo_json_paths[car_id] = {
        #         "type": "FeatureCollection",
        #         "features": [],
        #     }
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

    def run_recognition(self):
        """
        Run the car recognition pipeline
        In this pipeline, we process the video frames and detect cars using YOLO.
        We then extract the color histogram of each car and compare it with the existing car histograms.
        If a similar car is found, we update the car's position in the GeoJSON data.
        If a similar car is not found, we create a new car entry in the tracker.
        After processing all the frames, we save the GeoJSON data, image data, and other map data.
        """
        
        # Clear old image data
        config = Config()

        clear_directory(config.CAR_IMAGE_PATH)

        cap = cv2.VideoCapture(config.VIDEO_PATH)

        detector = YOLODetector(config.YOLO_MODEL_PATH)

        # Process video frames
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:  # If the frame is not read correctly, break the loop
                break

            frame_idx = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
            if frame_idx >= len(self.drone_data):
                break  # Break the loop if we have processed all the drone data

            drone_info = self.drone_data[frame_idx]
            detections = detector.detect_objects(frame)
            box_index = 0
            for box in detections:
                x1, y1, x2, y2 = box.xyxy[
                    0
                ]  # Extracting the coordinates from the detection box (xyxy format)
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                class_id = box.cls[0]

                if class_id not in self.interested_class_ids:
                    continue  # Skip the class if it is not a vehicle

                confidence = box.conf[0]
                if float(confidence) < self.confidence_threshold:
                    continue  # Skip the detection if the confidence is below the threshold

                car_center = ((x1 + x2) // 2, (y1 + y2) // 2)
                lat, lon = self.map_to_coordinates(
                    car_center[0], car_center[1], frame_idx, drone_info
                )

                # Compute the color histogram of the car
                car_hist = compute_color_histogram(frame, (x1, y1, x2 - x1, y2 - y1))
                car_found, car_id = self.find_similar_car(car_hist, look_for_last=3)

                if not car_found:
                    car_id = self.create_new_car(
                        car_id, car_hist, frame, x1, y1, x2, y2, config.CAR_IMAGE_PATH, padding=20
                    )

                # Add the car's current position to the GeoJSON feature collection
                self.generate_car_geo_json(
                    car_id,
                    lat,
                    lon,
                    confidence,
                    drone_info,
                    delay= True if box_index == 0 else False, # add delay only to one point on the frame
                )
                box_index += 1

                # For other maps (e.g., kepler.gl or folium)
                if car_id not in self.car_geo_paths:
                    self.car_geo_paths[car_id] = []
                self.car_geo_paths[car_id].append((lat, lon))


        # Save the GeoJSON data
        export_for_geo_json(self.car_geo_json_paths, config.GEOJSON_OUTPUTPATH)

        cap.release()  # Release the video capture object


if __name__ == "__main__":
    main = CarTracker()
    main.run_recognition()
