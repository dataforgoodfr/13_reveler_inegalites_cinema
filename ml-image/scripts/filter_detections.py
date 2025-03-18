import cv2
import numpy as np
from typing import List, Dict, Callable

class DetectionFilter:
    def __init__(self, simple_filters: List[Callable[[Dict], bool]], complex_filters: List[Callable[[Dict], bool]], area_type : str = 'face', **kwargs) -> None:
        self.simple_filters = simple_filters
        self.complex_filters = complex_filters
        self.area_type = area_type
        self.kwargs = kwargs

    def apply(self, detections: List[Dict]) -> List[Dict]:
        filtered_detections = [det for det in detections if all(f(det, **self.kwargs) for f in self.simple_filters)]

        for det in filtered_detections:
            det["sharpness"] = compute_sharpness(det[f"cropped_{self.area_type}"])  # On ne calcule que pour celles qui restent

        return [det for det in filtered_detections if all(f(det, **self.kwargs) for f in self.complex_filters)]

def filter_by_area(det: Dict, **kwargs) -> bool:
    min_area = kwargs.get("min_area", 0.01)
    max_area = kwargs.get("max_area", 0.5)
    x1, y1, x2, y2 = det["bbox"]
    total_area = kwargs.get("total_area", 1.0)
    area = (x2 - x1) * (y2 - y1) / total_area
    return min_area <= area <= max_area 

def filter_by_confidence(det: Dict, **kwargs) -> bool:
    min_conf = kwargs.get("min_conf", 0.5)
    return det["conf"] >= min_conf

def compute_sharpness(image: np.ndarray) -> float:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

def filter_by_sharpness(det: Dict, **kwargs) -> bool:
    min_sharpness = kwargs.get("min_sharpness", 35.0)
    return det["sharpness"] >= min_sharpness