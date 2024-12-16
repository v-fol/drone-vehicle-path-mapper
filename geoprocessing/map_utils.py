import json
from .simplification import remove_outliers_with_dbscan


def export_for_geo_json(
    car_paths: list, output_path: str, eps: float = 0.00001, min_samples: int = 3
) -> None:
    """
    Export car paths to a GeoJSON file after removing outliers using DBSCAN.

    Args:
        car_paths (list): List of GeoJSON feature dictionaries representing car paths
        output_path (str): Path to the output GeoJSON file
        eps (float): Maximum distance between two points to be considered in the same neighborhood
        min_samples (int): Minimum number of points to form a cluster
    """
    export_geo_format = {"type": "FeatureCollection", "features": []}

    removed_outliers = remove_outliers_with_dbscan(
        car_paths, eps=eps, min_samples=min_samples
    )
    print(
        f"Removed {len(car_paths) - len(removed_outliers)} outliers from {len(car_paths)} paths"
    )

    car_counts = {}
    for feature in removed_outliers:
        car_id = feature["properties"]["vehicle_id"]
        car_counts[car_id] = car_counts.get(car_id, 0) + 1

    removed_outliers = [
        feature
        for feature in removed_outliers
        if car_counts[feature["properties"]["vehicle_id"]] >= 5
    ]

    for feature in removed_outliers:
        export_geo_format["features"].append(feature)

    with open(output_path, "w") as file:
        json.dump(export_geo_format, file)
