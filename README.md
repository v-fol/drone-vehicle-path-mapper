# Drone Video Vehicle Path Traker

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)


The project is designed to detect and map the paths of vehicles using drone footage. It leverages machine learning models for object detection and provides a frontend interface to visualize the detected paths and vehicle information.

## How It Works
- **Preprocessing**: I used FFmpeg to preprocess the video, reducing its high bitrate and converting the SRT file into a JSON file using regex to extract relevant information about each frame.
- **Detection**: The preprocessed data is fed into a YOLO-based object detection model to identify vehicles. I used YOLOv8 nano and small models trained on aerial road drone footage.
- **Tracking**: ByteTrack multi-object tracking computer vision algorithm is used to maintain vehicle identities.
- **Geoprocessing**: To calculate vehicle coordinates, I employed several strategies based on the drone's position and the vehicle's position in the frame. Simplification algorithms were used to remove defective points.
- **Frontend Visualization**: The processed data is visualized on a map using React with the Mapbox Maps library. This includes features such as real-time path prediction displayed alongside the video and the ability to examine individual vehicle paths.


## Preprocessing

I used simple preprosing methods with ffmpeg to reduce file size, bitrate and also used it to cut the video in smaller test chunks. Commands used:

```bash
ffmpeg -i video2.MP4  -b:v 800k -c:v libx264 -preset fast -crf 25 video_low_bit_full.mp4
```

```bash
ffmpeg -i video2.MP4 -ss 00:0:00 -t 00:00:40 -c copy video_cut.mp4
```

The SRT file was transformet with regex python script `parce_srt.py` to json.

## Detection

For the first version I tried general yolov8 models, witch worked preaty good right of the box for general detection but had a lot of problems with detecting vehicles in chalanging situations like shadows or vehicles with sunroofs and where giving a lot of false detections, detecting houses, bus stops, trees as cars.
######
So naturaly came to a conclusion to train those models on a dataset of areal drone vehicles/trafic footage.
######
I used a dataset from https://universe.roboflow.com/irem69/hep7/dataset/7 with 3000 images a 70% training, 20% validation and 10% testing split.

At first I trained the the nano version of yolo8 with 50 epoches (runs).
And after trained small model with 21 and 33 epoches. Sample command:
```bash
yolo task=detect mode=train model=yolov8n.pt data=data.yaml epochs=50 imgsz=640
```
Bouth models showed significant improvment in detection, with the last one (small 33 epoches) showing the best result in terms of not detection outliers. Although the nano version is also great considering it uses 3 times less resources to process a frame. 

I also tried to skip some amount of frames while using the models to make the process fasted but it negativly impacted detection.


## Tracking

To maintain vehicles signature in between frames I used a method called Histogram Comparison from opencv, wich worked preaty well at first glance. It has troubles if there are frames with many objects or when an object comes in or out of the shadow but generally we can track most of the cars on the video.

There is also a problem when an object is showed partialy in the frame but is detecded than this algoritm might generate two object ids. I fixed it by not creating ids when object is realy near to the frame. This might be bad for when you need to detect object that apear only partialy in the frame, but for this footage it worked fine.

After I finished with this implementing this method I have found that ultralitics yolo models have support for ByteTrack and BoT-SORT multi-object tracking =)
I changenged my aproach to work with ByteTrack multi-object tracking computer vision algorithm.
This method did show much better results of persising car ids in chalanging conditions.

## Geoprocessing

At first I used drone's latitude and longitude for vehicle coordinates, and for this scale it works fine. But I wanted to utilize the information we have in the SRT file about drone yaw and camera/shot info to make the path more close to the real world. My algorithm did okay but there still need to be done some improvements for situations when the drone is changing its yaw realy fast.

I also tried diferent path optimization algoritms to remove coordinates that are more likely to be not acurate. The one that performed the best was DBSCAN (density-based spatial clustering of applications with noise). That removed sertain problems with previous algo.

## Frontend Visualization

For map visualization I tried a lot of solutions: kepler.gl, plotly, dash, folium. But did stick with Mapbox for 3 reasons.
1) react library with a lot of customizations and low level support.
2) fast maps api, with a lot of maps styles.
3) good documuntation.

The result you can see at `demo/frontend'
