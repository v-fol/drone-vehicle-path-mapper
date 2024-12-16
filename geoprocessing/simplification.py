import numpy as np
from sklearn.cluster import DBSCAN


def douglas_peucker(features: list, tolerance: float) -> list:
    """
    Simplifies a list of GeoJSON features representing a path using the Douglas-Peucker algorithm.

    Args:
        features (list of dict): List of GeoJSON feature dictionaries
        tolerance (float): Maximum distance threshold for simplification
    Returns:
        list of dict: Simplified list of GeoJSON feature dictionaries
    """
    if len(features) < 3:
        return features  # Cannot simplify further

    start, end = (
        features["geometry"]["coordinates"][0],
        features["geometry"]["coordinates"][-1],
    )

    # Find the point furthest from the line segment
    line = np.array([end[0] - start[0], end[1] - start[1]])
    line_length = np.linalg.norm(line)
    if line_length == 0:
        return [start, end]

    line_unit = line / line_length
    max_distance = 0
    furthest_index = 0

    for i in range(1, len(features) - 1):
        point = np.array(features[i]["geometry"]["coordinates"]) - np.array(start)
        distance = np.linalg.norm(np.cross(point, line_unit))
        start_to_point = np.array(point) - np.array(start)
        projection = np.dot(start_to_point, line_unit)
        closest_point = np.array(start) + projection * line_unit
        distance = np.linalg.norm(point - closest_point)

        if distance > max_distance:
            max_distance = distance
            furthest_index = i

    # If the furthest point is greater than the tolerance, split the path
    if max_distance > tolerance:
        left = douglas_peucker(features[: furthest_index + 1], tolerance)
        right = douglas_peucker(features[furthest_index:], tolerance)
        return left[:-1] + right  # Remove duplicate point
    else:
        return [start, end]  # No points to remove


def douglas_peucker_path_simlification(features: list, simplification_threshold: float) -> list:
    """
    Simplifies a list of GeoJSON features representing paths using the Douglas-Peucker algorithm.

    Args:
        features (list of dict): List of GeoJSON feature dictionaries
        simplification_threshold (float): Maximum distance threshold for simplification
    Returns:
        list of dict: Simplified list of GeoJSON feature dictionaries

    """
    simplified_features = []
    features_by_car_id = {}
    for feature in features:
        car_id = feature["properties"]["car_id"]
        if car_id not in features_by_car_id:
            features_by_car_id[car_id] = []
        features_by_car_id[car_id].append(feature)

    for car_id, features in features_by_car_id.items():
        simplified_path = douglas_peucker(features, simplification_threshold)
        simplified_features.append(simplified_path)

    return simplified_features


def remove_outliers_with_dbscan(features: list, eps: float, min_samples: int) -> list:
    """
    Removes outliers from a list of feature dictionaries using DBSCAN.

    Args:
        features (list of dict): List of GeoJSON feature dictionaries
        eps (float): Maximum distance between two points to be considered in the same neighborhood
        min_samples (int): Minimum number of points to form a cluster

    Returns:
        list of dict: Filtered list of features with outliers removed
    """
    # Extract coordinates from features
    coords = [feature["geometry"]["coordinates"] for feature in features]

    # Convert coordinates to numpy array
    data = np.array(coords)

    # Apply DBSCAN
    db = DBSCAN(eps=eps, min_samples=min_samples, metric="euclidean").fit(data)

    # Filter out outliers (-1 label means outlier)
    filtered_features = [
        feature for feature, label in zip(features, db.labels_) if label != -1
    ]

    return filtered_features
