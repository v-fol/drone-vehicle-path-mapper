# Drone Video Vehicle Path Traker

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)


The project is designed to detect and map the paths of vehicles using drone footage. It leverages machine learning models for object detection and provides a frontend interface to visualize the detected paths and vehicle information.

## How It Works
- **Preprocessing**: I used FFmpeg to preprocess the video, reducing its high bitrate and converting the SRT file into a JSON file using regex to extract relevant information about each frame.
- **Detection**: The preprocessed data is fed into a YOLO-based object detection model to identify vehicles. I used YOLOv8 nano and small models trained on aerial road drone footage.
- **Tracking**: Frame histograms are used to maintain vehicle identities.
- **Geoprocessing**: To calculate vehicle coordinates, I employed several strategies based on the drone's position and the vehicle's position in the frame. Simplification algorithms were used to remove defective points.
- **Frontend Visualization**: The processed data is visualized on a map using React with the Mapbox Maps library. This includes features such as real-time path prediction displayed alongside the video and the ability to examine individual vehicle paths.
