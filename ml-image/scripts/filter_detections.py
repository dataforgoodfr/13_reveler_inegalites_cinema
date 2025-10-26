import cv2
import mediapipe as mp
import numpy as np
import os
from typing import List, Dict, Callable

### Review: je verrais bien une classe pr chaque filtre (qui hériteraient d'une meme classe abstraite) mais peut etre pas la priorité du projet :p

class DetectionFilter:
    def __init__(self, simple_filters: List[Callable[[Dict], bool]], complex_filters: List[Callable[[Dict], bool]], area_type : str = 'face', **kwargs) -> None:
        self.simple_filters = simple_filters
        self.complex_filters = complex_filters
        self.area_type = area_type # not used for now
        self.kwargs = kwargs

    def apply(self, detections: List[Dict], mode: str = "clustering") -> List[Dict]:
        #print(f"{len(detections)} detections before filtering")
        match mode:
            case "clustering":
                filtered_detections = detections
                for filter in self.simple_filters + self.complex_filters:
                    filtered_detections = [det for det in filtered_detections if filter(det, **self.kwargs)]
                    #print(f"{len(filtered_detections)} detections remaining after filtering {filter.__name__}")
                
                return filtered_detections
            
            case "classification":
                detections_vote_weight = np.zeros_like(detections)
                # Add 1 to count for each passed filters
                for filter in self.simple_filters + self.complex_filters:
                    detections_vote_weight = np.add(detections_vote_weight, np.array([filter(det, **self.kwargs) for det in detections]))

                for det, weight in zip(detections, detections_vote_weight, strict=False) :
                    det["weight"] = weight
                return detections
    
    def visualize_detection_parameters(self, movie_id: str, detections: List[Dict], storage_folder: str='visualize_parameters') -> None:
        movie_path = os.path.join(storage_folder, movie_id)
        os.makedirs(movie_path, exist_ok=True)
        for det in detections:
            image = det[f"cropped_{self.area_type}"]
        
            total_area = self.kwargs.get("total_area", 1.0)
            param_area = compute_area(det["bbox"], total_area)
            param_conf = det['conf']
            param_sharpness = compute_sharpness(image)
            nose_tip = get_face_landmarks(image)
            param_nose_tip = f"_{nose_tip: .2f}.jpg" if nose_tip is not None else "_undetermined.jpg"
            parameters = f"_{param_area: .2f}_{param_conf: .2f}_{param_sharpness: .2f}" + param_nose_tip

            attr_age = det['age']
            attr_age_conf = det['age_conf']
            attr_ethnicity = det['ethnicity']
            attr_ethnicity_conf = det['ethnicity_conf']
            attr_gender = det['gender']
            attr_gender_conf = det['gender_conf']
            attributes = f"_{attr_gender}_{attr_age}_{attr_ethnicity}_{attr_gender_conf:.2f}_{attr_age_conf:.2f}_{attr_ethnicity_conf:.2f}"

            image_name = f"frame_{det['frame_id']}_perso_{det['perso_id']}"
            
            #store image with parameters in folder
            write_image_with_parameters(parameters, attributes, image_name, image, movie_path)

def write_image_with_parameters(parameters:str, attributes:str, image_name: str, image: np.ndarray, movie_path: str) -> None:
    file_name = image_name + attributes + parameters
    file_path = os.path.join(movie_path, file_name)
    cv2.imwrite(file_path, image)
            

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


def filter_detections_poster(detections: list[dict], total_area: float, min_area: float, min_conf: float) -> list[dict]: 
    # Filter detections for poster
    filters = DetectionFilter(
        simple_filters=[validates_confidence_filter],
        complex_filters=[],
        area_type='face',
        total_area=total_area,
        min_area=min_area,
        min_conf=min_conf
    )    
    filtered_detections = filters.apply(detections)

    return filtered_detections


def filter_detections_clustering(detections: list[dict], effective_area: float, min_area: float, max_area: float, min_conf: float) -> list[dict]:
    # Filter detections
    filters = DetectionFilter(
        simple_filters=[validates_area_filter,
                        validates_confidence_filter],
        complex_filters=[],
        area_type='face',
        total_area=effective_area,
        min_area=min_area,
        max_area=max_area,
        min_conf=min_conf
    )
    filtered_detections = filters.apply(detections)

    return filtered_detections


def filter_detections_classifications(detections: list[dict], effective_area: float, min_conf: float, min_sharpness: float, max_z: float, min_mouth_opening: float, movie_id: int | str=None, mode: str="infer") -> list[dict]:
    # Filter detections
    filters = DetectionFilter(
        simple_filters=[validates_confidence_filter],
        complex_filters=[validates_sharpness_filter, validates_pose_filter],
        area_type='face',
        total_area=effective_area,
        min_conf=min_conf,
        min_sharpness=min_sharpness,
        max_z=max_z,
        min_mouth_opening=min_mouth_opening
    )    
    filtered_detections = filters.apply(detections, mode = "classification")

    if mode == "evaluate":
        filters.visualize_detection_parameters(movie_id=movie_id, detections=detections, storage_folder='visualize_parameters')

    return filtered_detections


def draw_landmarks(image):
    h, w, _ = image.shape  # Dimensions de l'image

    # Conversion en RGB
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_image)

    if not results.multi_face_landmarks:
        #print("Aucun visage détecté")
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

    return(draw_image, nose_tip, left_eye,right_eye, sup_lips, inf_lips)
    #cv2.imwrite(f"example/pose/face_with_landmarks_{nose_tip.z : .2f}_{left_eye.x: .2f}_{right_eye.x: .2f}_{sup_lips.y: .2f}_{inf_lips.y: .2f}.jpg", draw_image)


