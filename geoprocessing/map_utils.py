import json

def export_for_geo_json(car_paths):
    export_geo_format = {
    "type": "FeatureCollection",
    "features": []
    }

    for key, value in car_paths.items():
        export_geo_format['features'].extend(value['features'])

    with open('pathsGEO.json', 'w') as file:
        json.dump(export_geo_format, file)