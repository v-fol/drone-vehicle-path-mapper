import json
import re

from datetime import datetime
from typing import List, Dict


def parse_srt(filename: str) -> List[Dict]:
    """
    Parse an SRT file and extract frame data into a list of dictionaries.

    Args:
        filename (str): Path to the SRT file
    
    Returns:
        List[Dict]: List of dictionaries containing frame data
    
    """
    data_list = []
    with open(filename, "r", encoding="utf-8") as file:
        content = file.read()

    # Split the content into blocks for each frame
    blocks = content.strip().split("\n\n")

    # [iso: 100] [shutter: 1/798.21] [fnum: 2.8] [ev: 0] [color_md : default] [ae_meter_md: 1] [focal_len: 24.00] [dzoom_ratio: 1.00], [latitude: 48.267013] [longitude: 25.914562] [rel_alt: 102.229 abs_alt: 426.185] [gb_yaw: -65.8 gb_pitch: -89.9 gb_roll: 0.0]

    frame_re = re.compile(r"FrameCnt: (\d+), DiffTime: (\d+ms)")
    timestamp_re = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})")
    gps_re = re.compile(r"latitude: ([\d.-]+).*?longitude: ([\d.-]+)")
    alt_re = re.compile(r"rel_alt: ([\d.-]+).*?abs_alt: ([\d.-]+)")
    gb_re = re.compile(r"gb_yaw: ([\d.-]+).*?gb_pitch: ([\d.-]+).*?gb_roll: ([\d.-]+)")
    focal_len = re.compile(r"focal_len: ([\d.-]+)")

    for block in blocks:
        frame_data = {}

        # Extract frame count and diff time
        frame_match = frame_re.search(block)
        if frame_match:
            frame_data["frame_cnt"] = int(frame_match.group(1))
            frame_data["diff_time"] = frame_match.group(2)

        # Extract timestamp
        timestamp_match = timestamp_re.search(block)
        if timestamp_match:
            frame_data["timestamp"] = datetime.strptime(
                timestamp_match.group(1), "%Y-%m-%d %H:%M:%S.%f"
            ).strftime("%H:%M:%S:%f")[:-3]

        # Extract GPS data
        gps_match = gps_re.search(block)
        if gps_match:
            frame_data["latitude"] = float(gps_match.group(1))
            frame_data["longitude"] = float(gps_match.group(2))

        # Extract altitude data
        alt_match = alt_re.search(block)
        if alt_match:
            frame_data["rel_alt"] = float(alt_match.group(1))
            frame_data["abs_alt"] = float(alt_match.group(2))

        # Extract gimbal data
        gb_match = gb_re.search(block)
        if gb_match:
            frame_data["gb_yaw"] = float(gb_match.group(1))
            frame_data["gb_pitch"] = float(gb_match.group(2))
            frame_data["gb_roll"] = float(gb_match.group(3))

        # Extract focal length
        focal_len_match = focal_len.search(block)
        if focal_len_match:
            frame_data["focal_len"] = float(focal_len_match.group(1))

        data_list.append(frame_data)

    return data_list


if __name__ == "__main__":
    filename = "video2.SRT"
    parsed_data = parse_srt(filename)
    with open("parsedSRT.json", "w") as f:
        f.write(json.dumps(parsed_data))
