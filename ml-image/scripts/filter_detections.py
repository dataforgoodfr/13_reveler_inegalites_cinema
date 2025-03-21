import cv2
import numpy as np
from typing import List, Dict, Callable
import mediapipe as mp

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
    area = np.abs(x2 - x1) * np.abs(y2 - y1) / total_area
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

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, refine_landmarks=True)

def get_face_landmarks(image: np.ndarray) -> tuple:
    h, w, _ = image.shape
    size = max(h, w)
    square_image = np.zeros((size, size, 3), dtype=np.uint8)
    square_image[:h, :w] = image
    rgb_image = cv2.cvtColor(square_image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_image)
    
    if not results.multi_face_landmarks:
        return None

    landmarks = results.multi_face_landmarks[0]
    nose_tip = landmarks.landmark[1]  # Nose tip is the second landmark
    left_eye = landmarks.landmark[33]  # Left eye is the 34th landmark
    right_eye = landmarks.landmark[263]  # Right eye is the 264th landmark
    sup_lips = landmarks.landmark[13]
    inf_lips = landmarks.landmark[14]
    return nose_tip.z, left_eye.x * w, right_eye.x * w, sup_lips.y * h, inf_lips.y * h

def filter_by_pose(det: Dict, **kwargs) -> bool:
    min_z = kwargs.get("min_z", -0.3)
    max_z = kwargs.get("max_z", 0.3)
    min_eye_diff = kwargs.get("min_eye_diff", 0.4)
    pose = get_face_landmarks(det[f"cropped_face"])
    if pose is None:
        return False
    nose_z = pose[0]
    left_eye_x = pose[1]
    right_eye_x = pose[2]
    eye_diff = abs(left_eye_x - right_eye_x)
    return min_z <= nose_z <= max_z and eye_diff >= min_eye_diff

def is_face_not_occluded(det: Dict, **kwargs) -> bool:
    pose = get_face_landmarks(det[f"cropped_face"])
    if pose is None:
        return False  # Aucun visage détecté = obstruction probable
    

    min_mouth_opening = kwargs.get("min_mouth_opening", 0.01)
    mouth_open = pose[4] - pose[5]  # Lips inf/sup distance
    
    if mouth_open < min_mouth_opening:
        return False

    return True
