import math


def adjust_lat_long_with_direction(lat, lon, displacement, direction_deg):
    """
    Adjusts latitude and longitude by a displacement (in meters) in a specific direction.
    Lat and Lon are in decimal degrees. Direction is in degrees relative to the compass.
    
    displacement: The total displacement (in meters).
    direction_deg: Direction in degrees relative to the compass (0° = North, 90° = East).
    """
    
    # Convert the direction angle from degrees to radians
    direction_rad = math.radians(direction_deg)
    
    # Break the displacement into x (East-West) and y (North-South) components
    displacement_x = displacement * math.sin(direction_rad)  # East-West (positive is East)
    displacement_y = displacement * math.cos(direction_rad)  # North-South (positive is North)
    
    # Convert latitude and longitude from degrees to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    
    # Calculate the change in latitude
    delta_lat = displacement_y / 111320  # 1 degree of latitude is approx 111,320 meters
    
    # Calculate the change in longitude
    delta_lon = displacement_x / (111320 * math.cos(lat_rad))  # Adjust based on current latitude
    
    # New latitude and longitude in radians
    new_lat_rad = lat_rad + math.radians(delta_lat)
    new_lon_rad = lon_rad + math.radians(delta_lon)
    
    # Convert back to degrees
    new_lat = math.degrees(new_lat_rad)
    new_lon = math.degrees(new_lon_rad)
    
    return new_lat, new_lon

