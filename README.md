# Drone Video Vehicle Path Traker

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)


The project is designed to detect and map the paths of vehicles using drone footage. It leverages machine learning models for object detection and provides a frontend interface to visualize the detected paths and vehicle information.

![](docs/media/demo.gif)

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

For the first version, I used general YOLOv8 models, which worked pretty well right out of the box for general detection. However, they struggled in challenging situations, such as detecting vehicles in shadows, vehicles with sunroofs, or in scenarios with a lot of false positives—misidentifying houses, bus stops, and trees as cars.

Naturally, I concluded that training these models on a specialized dataset of aerial drone footage featuring vehicles and traffic would improve performance.

I used a dataset from [Roboflow](https://universe.roboflow.com/irem69/hep7/dataset/7), consisting of 3,000 images with a 70% training, 20% validation, and 10% testing split.

Initially, I trained the nano version of YOLOv8 with 50 epochs (runs). After that, I trained the small model with 21 and 33 epochs. Sample command:
```bash
yolo task=detect mode=train model=yolov8n.pt data=data.yaml epochs=50 imgsz=640
```
Both models showed significant improvement in detection, with the last one (small, 33 epochs) delivering the best results in terms of minimizing detection outliers. However, the nano version is also impressive, considering it uses three times fewer resources to process a frame.

I also experimented with skipping some frames while using the models to speed up the process, but this negatively impacted detection accuracy.


## Tracking

To maintain vehicle signatures between frames, I used the Histogram Comparison method from OpenCV, which worked well initially. However, it encountered difficulties when frames contained many objects or when objects moved in and out of shadows. Despite these challenges, we could track most cars in the video.

Another issue arose when objects appeared partially in the frame but were still detected - this algorithm would sometimes generate duplicate object IDs. I addressed this by preventing ID creation for objects very close to the frame edge. While this solution might not be ideal for cases where detecting partially visible objects is necessary, it worked well for this footage.

After implementing this method, I discovered that Ultralytics YOLO models support ByteTrack and BoT-SORT multi-object tracking =).
I then modified my approach to use ByteTrack, which demonstrated significantly better results in maintaining car IDs under challenging conditions.

## Geoprocessing

At first I used drones latitude and longitude for vehicle coordinates, and for this scale it works fine. But I wanted to utilize the information we have in the SRT file about drone yaw and camera/shot info to make the path more close to the real world. My algorithm did okay but there still need to be done some improvements for situations when the drone is changing its yaw really fast.

I also tried diferent path optimization algoritms to remove coordinates that are more likely to be not acurate. The one that performed the best was DBSCAN (density-based spatial clustering of applications with noise). That removed sertain problems with previous algo.

## Frontend Visualization

For map visualization I tried a lot of solutions: kepler.gl, plotly, dash, folium. But did stick with Mapbox for 3 reasons.
1) react library with a lot of customizations and low level support.
2) fast maps api, with a lot of maps styles.
3) good documuntation.

The app is build with react + vite + typescript + jotai + tailwindcss + shadcn.

The result you can see at `demo/frontend`

## Usage

To run this project you need to install dependencies using [uv](https://docs.astral.sh/uv/getting-started/installation/):
```bash
uv sync
```
Transform the SRT file with parse_srt.py, witch will generate a json file.
```bash
python3 parse_srt.py
```

Than go to `config.py` and change necessary variables, like video source:
```python
class Config:
    YOLO_MODEL_PATH = './runs/detect/train_small_33epochs/weights/best.pt'
    DRONE_DATA_PATH = 'parsedSRT.json'
    VIDEO_PATH = 'video.mp4' # your video
    GEOJSON_OUTPUTPATH = './demo/frontend/src/pathGEO.json'
    CAR_IMAGE_PATH = './demo/frontend/src/assets/car'
```
Important here is the video path/name of the file, you can leave everything else.

After this you can run:
```bash
python3 main.py 
```
wich will generate images and GEOJSON files in frontend folder.

To launch the react app you need to install dependansies, I recomend [bun](https://bun.sh/docs/installation) for this:
```bash
cd demo/frontend
bun i
```
And than you can run:
```bash
bun run dev
```
and open the react app with the map at `http://localhost:5173/`

##  Technologies, links

- https://github.com/ultralytics/ultralytics 
- https://github.com/ifzhang/ByteTrack
- https://github.com/visgl/react-map-gl
- https://www.mapbox.com/
- https://scikit-learn.org/stable/


