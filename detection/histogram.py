import cv2
import numpy as np

def compute_color_histogram(image: np.ndarray, bbox: tuple) -> np.ndarray:
    """
    Compute the color histogram of the region of interest (ROI) in the image
    defined by the bounding box (bbox).

    Args:
        image (numpy.ndarray): The input image.
        bbox (tuple): The bounding box (x, y, w, h) of the ROI.
    Returns:
        numpy.ndarray: The color histogram of the ROI.
    """
    x, y, w, h = bbox
    roi = image[y:y+h, x:x+w]
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv_roi], [0], None, [180], [0, 180])
    cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
    return hist

def compare_histograms(hist1: np.ndarray, hist2: np.ndarray, method: int) -> float:
    """
    Compare two color histograms using the specified method.
    
    Args:
        hist1 (numpy.ndarray): The first color histogram.
        hist2 (numpy.ndarray): The second color histogram.
        method (int): The comparison method to use.
    Returns:
        float: The similarity score between the two histograms
    """
    return cv2.compareHist(hist1, hist2, method)
