class Config:
    YOLO_MODEL_PATH = './runs/detect/train_small_v11_35epochs/weights/best.pt'
    DRONE_DATA_PATH = 'parsedSRT.json'
    VIDEO_PATH = 'video_low_bit.mp4'
    GEOJSON_OUTPUT_PATH = './demo/frontend/src/pathGEO.json'
    CAR_IMAGE_PATH = './demo/frontend/src/assets/images/vehicles'

    CAMERA_RESOLUTION_WIDTH = 1920 # pixels
    CAMERA_RESOLUTION_HEIGHT = 1080 # pixels
    SENSOR_WIDTH = 8 # mm
    
    CONFIDENCE_THRESHOLD = 0.8
    IOU_THRESHOLD = 0.9
    CLOSE_TO_FRAME_PIXELS = 20
    IMAGE_PADDING = 20
    INTERESTED_CLASS_IDS = [1, 2, 3, 4, 7]
    DISPLACEMENT_FRAME_COUNT_THRESHOLD = 10
    DISPLACEMENT_YAW_THRESHOLD = 4