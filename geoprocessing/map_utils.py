import json
from .simplification import remove_outliers_with_dbscan


def export_for_geo_json(car_paths: list, output_path: str, eps: float = 0.00001, min_samples: int = 3):
    export_geo_format = {"type": "FeatureCollection", "features": []}

    removed_outliers = remove_outliers_with_dbscan(
        car_paths, eps=eps, min_samples=min_samples
    )
    print(
        f"Removed {len(car_paths) - len(removed_outliers)} outliers from {len(car_paths)} paths"
    )

    for feature in removed_outliers:
        export_geo_format["features"].append(feature)

    with open(output_path, "w") as file:
        json.dump(export_geo_format, file)
