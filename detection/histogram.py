import cv2

def compute_color_histogram(image, bbox):
    x, y, w, h = bbox
    roi = image[y:y+h, x:x+w]
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv_roi], [0], None, [180], [0, 180])
    cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
    return hist

def compare_histograms(hist1, hist2, method=cv2.HISTCMP_CORREL):
    return cv2.compareHist(hist1, hist2, method)
