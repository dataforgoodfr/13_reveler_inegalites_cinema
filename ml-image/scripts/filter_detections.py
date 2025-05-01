import cv2
import numpy as np
from typing import List, Dict, Callable
import mediapipe as mp

### Review: je verrais bien une classe pr chaque filtre (qui hériteraient d'une meme classe abstraite) mais peut etre pas la priorité du projet :p

class DetectionFilter:
    def __init__(self, simple_filters: List[Callable[[Dict], bool]], complex_filters: List[Callable[[Dict], bool]], area_type : str = 'face', **kwargs) -> None:
        self.simple_filters = simple_filters
        self.complex_filters = complex_filters
        self.area_type = area_type # not used for now
        self.kwargs = kwargs

    def apply(self, detections: List[Dict], mode: str = "clustering") -> List[Dict]:
        match mode:
            case "clustering":
                filtered_detections = [det for det in detections if all(f(det, **self.kwargs) for f in self.simple_filters)]
                
                return [det for det in filtered_detections if all(f(det, **self.kwargs) for f in self.complex_filters)]
            
            case "classification":
                filtered_detections = []
                for det in detections:
                    passes_classification = all(f(det, **self.kwargs) for f in self.simple_filters + self.complex_filters)

                    if passes_classification:
                        filtered_detections.append(det)  # Keep the detection as is
                    else:
                        # If it fails classification, set predictions to "unknown"
                        det["age"] = "unknown"
                        det["gender"] = "unknown"
                        det["ethnicity"] = "unknown"
                        filtered_detections.append(det)

                return filtered_detections

def compute_area(bbox: List[float], total_area: float) -> float:
    x1, y1, x2, y2 = bbox
    area = np.abs(x2 - x1) * np.abs(y2 - y1) / total_area
    return area

def validates_area_filter(det: Dict, **kwargs) -> bool:
    min_area = kwargs.get("min_area", 0.01)
    max_area = kwargs.get("max_area", 1.0)
    total_area = kwargs.get("total_area", 1.0)
    area = compute_area(det["bbox"], total_area)
    return min_area <= area <= max_area 

def validates_confidence_filter(det: Dict, **kwargs) -> bool:
    min_conf = kwargs.get("min_conf", 0.5)
    return det["conf"] >= min_conf

def compute_sharpness(image: np.ndarray) -> float:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

def validates_sharpness_filter(det: Dict, **kwargs) -> bool:
    min_sharpness = kwargs.get("min_sharpness", 35.0)
    sharpness = compute_sharpness(det["cropped_face"])
    return sharpness >= min_sharpness

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.6)

def get_face_landmarks(image: np.ndarray) -> tuple:
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_image)
    
    if not results.multi_face_landmarks:
        return None

    landmarks = results.multi_face_landmarks[0]
    nose_tip = landmarks.landmark[1]  # Nose tip is the second landmark
    
    return nose_tip.z

def validates_pose_filter(det: Dict, **kwargs) -> bool:
    max_z = kwargs.get("max_z", -0.20)
    #draw_landmarks(det[f"cropped_face"])
    
    pose = get_face_landmarks(det["cropped_face"])
    
    if pose is None:
        return False
    
    nose_z = pose
    
    return nose_z <= max_z

def is_face_not_occluded(det: Dict, **kwargs) -> bool:
    pose = get_face_landmarks(det["cropped_face"])
    if pose is None:
        return False  # Aucun visage détecté = obstruction probable
    

    min_mouth_opening = kwargs.get("min_mouth_opening", 0.01)
    mouth_open = pose[4] - pose[5]  # Lips inf/sup distance
    
    if mouth_open < min_mouth_opening:
        return False

    return True

def draw_landmarks(image):
    h, w, _ = image.shape  # Dimensions de l'image

    # Conversion en RGB
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_image)

    if not results.multi_face_landmarks:
        print("Aucun visage détecté")
        return None
    
    draw_image = image.copy()
    # Dessiner les landmarks sur l'image
    for face_landmarks in results.multi_face_landmarks:
        for landmark in face_landmarks.landmark:
            x, y = int(landmark.x * w), int(landmark.y * h)  # Conversion en pixels
            cv2.circle(draw_image, (x, y), 1, (0, 255, 0), -1)  # Dessiner un point vert

    landmarks = results.multi_face_landmarks[0]
    nose_tip = landmarks.landmark[1]  # Nose tip is the second landmark
    left_eye = landmarks.landmark[33]  # Left eye is the 34th landmark
    right_eye = landmarks.landmark[263]  # Right eye is the 264th landmark
    sup_lips = landmarks.landmark[13]
    inf_lips = landmarks.landmark[14]

    cv2.imwrite(f"example/pose/face_with_landmarks_{nose_tip.z : .2f}_{left_eye.x: .2f}_{right_eye.x: .2f}_{sup_lips.y: .2f}_{inf_lips.y: .2f}.jpg", draw_image)