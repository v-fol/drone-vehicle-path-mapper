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
        self.car_geo_json_paths = {}
        self.car_colors = {}
        self.geo_paths = {}
        self.drone_data = load_drone_data(Config.DRONE_DATA_PATH)

    def map_to_coordinates(self, x, y, frame_idx, drone_info, resolution_width=1920, resolution_height=1080, aspect_ratio=16/9):
        drone_lat = drone_info['latitude']
        drone_lon = drone_info['longitude']
        altitude = drone_info['abs_alt']  # Absolute altitude in meters
        focal_length = drone_info['focal_len']  # Focal length in mm
        gb_yaw = drone_info['gb_yaw']
                                    
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
        displacement = math.sqrt(displacement_x_meters**2 + displacement_y_meters**2)

        # if the yaw for the last 10 frames did cahge more than 10 degrees we need to reset the displacement
        frame_range = 10
        if frame_idx > frame_range:
            yaw_changes = []
            for i in range(frame_idx - frame_range, frame_idx):
                yaw_changes.append(abs(self.drone_data[i]['gb_yaw'] - self.drone_data[i - 1]['gb_yaw']))
            if max(yaw_changes) > 3:
                displacement = 0


        new_lat, new_lon = adjust_lat_long_with_direction(drone_lat, drone_lon, displacement, gb_yaw + 180)

        return new_lat, new_lon

    def run(self):
        # Clear old data
        clear_directory('car')


        # Load configuration and data
        config = Config()
        cap = cv2.VideoCapture(config.VIDEO_PATH)

        # Initialize components
        detector = YOLODetector(config.YOLO_MODEL_PATH)

        # Process video frames
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_idx = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
            if frame_idx >= len(self.drone_data):
                break

            drone_info = self.drone_data[frame_idx]
            detections = detector.detect_objects(frame)
            for box in detections:
                # x1, y1, x2, y2 = map(int, box[:4])
                x1, y1, x2, y2 = box.xyxy[0]  # Extracting the coordinates from the box (xyxy format)
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                class_id = box.cls[0]
                if class_id not in [2, 3, 4, 5, 8]:
                    continue
                conf = box.conf[0]
                if float(conf) < 0.8:
                    continue
                car_center = ((x1 + x2) // 2, (y1 + y2) // 2)
                lat, lon = self.map_to_coordinates(car_center[0], car_center[1], frame_idx, drone_info)

                # Check or assign car ID (unchanged logic)

                # new aproach wirh color heistogram

                # Compute the color histogram of the car
                car_hist = compute_color_histogram(frame, (x1, y1, x2 - x1, y2 - y1))


                #---------------

                # Compare the histogram with existing cars
                car_found = False
                car_id = None
                simolarity_dict = {}
                # look up the last 5 found cars
                loop = 0
                for existing_car_id, hist in reversed(self.car_histograms.items()):
                    if loop > 3:
                        break
                    similarity = compare_histograms(car_hist, hist)
                    simolarity_dict[existing_car_id] = similarity
                    loop += 1

                # I need to find maximum number in that dict but kiping its key
                if len(simolarity_dict) > 0:
                    max_sim = max(simolarity_dict.values())
                    if max_sim > 0.65:
                        car_id = max(simolarity_dict, key=simolarity_dict.get)
                        self.car_histograms[car_id] = car_hist
                        car_found = True
                
                
                
                if not car_found:
                    # If no match, create a new car ID and track it
                    self.car_counter += 1
                    car_id = self.car_counter
                    # take a snapshot of the car and save as a image with the car_id and the frame number as the name and box as the crop
                    # Make the box slightly bigger by adding padding
                    padding = 20
                    y1_pad = max(0, y1 - padding)
                    y2_pad = min(frame.shape[0], y2 + padding)
                    x1_pad = max(0, x1 - padding)
                    x2_pad = min(frame.shape[1], x2 + padding)
                    
                    # Get the cropped image with padding
                    car_img = frame[y1_pad:y2_pad, x1_pad:x2_pad].copy()

                    
                    # Save the image
                    filename = f'car/vehicle_{car_id}.jpg'
                    cv2.imwrite(filename, car_img)
                    self.car_histograms[car_id] = car_hist
                    self.car_colors[car_id] = (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))  # Random color


            
                # Add the car's current position to the GeoJSON feature collection
                if car_id not in self.car_geo_json_paths:
                    self.car_geo_json_paths[car_id] = {
                        "type": "FeatureCollection",
                        "features": []
                    }

                self.car_geo_json_paths[car_id]["features"].append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    "properties": {
                        "vehicle_id": f"vehicle_{car_id}",
                        "timestamp": f"2024-12-09T{str(drone_info['timestamp'])}Z",
                        "color": f"#{self.car_colors[car_id][0]:02X}{self.car_colors[car_id][1]:02X}{self.car_colors[car_id][2]:02X}",
                        "confidence": f"{conf:.4f}"
                    }
                })

                if car_id not in self.car_geo_paths:
                    self.car_geo_paths[car_id] = []
                self.car_geo_paths[car_id].append((lat, lon))


        # Save the GeoJSON data
        export_for_geo_json(self.car_geo_json_paths)

        
        cap.release()

if __name__ == "__main__":
    main = CarTracker()
    main.run()
