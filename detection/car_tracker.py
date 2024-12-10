import cv2
from detection.histogram import compute_color_histogram, compare_histograms
from geoprocessing.coordinates import map_to_coordinates
import numpy as np


class CarTracker:
    def __init__(self):
        self.car_counter = 0
        self.car_histograms = {}
        self.car_geo_paths = {}
        self.car_geo_json_paths = {}
        self.car_colors = {}
        self.geo_paths = {}

    def track_cars(self, detections, frame, drone_info, frame_idx):
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
            lat, lon = map_to_coordinates(car_center[0], car_center[1], frame_idx, drone_info)

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
                    "color": f"#{self.car_colors[car_id][0]:02X}{self.car_colors[car_id][1]:02X}{self.car_colors[car_id][2]:02X}"
                }
            })

            if car_id not in self.car_geo_paths:
                self.car_geo_paths[car_id] = []
            self.car_geo_paths[car_id].append((lat, lon))
