import cv2

from ultralytics import YOLO
import numpy as np

import torch
from torch.utils.data import DataLoader
from torchvision import transforms

from .utils import ImageDataset

class VisionDetection :
    def __init__(self, device:str = None, num_cpu_threads:int = 1, H_resize:int = 640, W_resize:int = 640) -> None:
        # add more models here as we see fit, can also swap current models for smaller models
        
        if not device :
            self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        else :
            self.device = torch.device(device)

        torch.set_num_threads(num_cpu_threads)

        self.H_resized, self.W_resized = H_resize, W_resize

        self.yolo_model_person = YOLO('models/yolo11l.pt').to(self.device).eval()
        #https://github.com/ultralytics/ultralytics
    
        self.yolo_model_face = YOLO('models/yolov11n-face.pt').to(self.device).eval()
        #https://github.com/akanametov/yolo-face

    def get_areas_of_interest(
            self, images: np.ndarray, area_type:str = "face", batch_size:int = 64) -> list:
        """
        Extract areas of interest (faces, silhouettes) from a list of images.
        """
        
        # Transformation for YOLO model
        def bgr_to_rgb(image):
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        if len(images.shape) == 3:  # Single image: [H, W, C]
            images = np.expand_dims(images, axis=0)  # Convert to batch: [1, H, W, C]

        if len(images.shape) != 4:  # Ensure batch format: [N, H, W, C]
            raise ValueError("Input images must have shape [H, W, C] or [N, H, W, C]")

        # Define transformations
        frames_transform = transforms.Compose([
            #transforms.Lambda(lambda img: bgr_to_rgb(img)),
            transforms.ToTensor(),
            transforms.Resize((self.H_resized, self.W_resized)),  # Resize for YOLO model
        ])

        # Load frames in the dataloader
        dataset = ImageDataset(images, frames_transform)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=0)

        # Detect faces in all frames of the trailer
        results = []
        with torch.no_grad():
            if area_type == "face" :
                for batch in dataloader:
                    batch = batch.to(self.device)
                    batch = torch.clamp(batch, 0, 1)  # Ensure values are in [0, 1] range
                    detections = self.yolo_model_face(batch, verbose=False) 
                    results.extend(detections)
            else :
                for batch in dataloader:
                    batch = batch.to(self.device)
                    batch = torch.clamp(batch, 0, 1)  # Ensure values are in [0, 1] range
                    detections = self.yolo_model_person(batch, verbose=False, classes=[0])
                    results.extend(detections)

        return results

    def crop_areas_of_interest(
            self, images: np.ndarray, H_original: int, W_original: int, area_type:str = 'face', batch_size: int = 64) -> None:
        """
        Create individual subimages for all areas of interest in one image
        """ 
        areas_of_interest = self.get_areas_of_interest(images, area_type, batch_size=batch_size)

        # Rescaling factors determination
        scale_x = W_original / self.W_resized
        scale_y = H_original / self.H_resized
        
        detections = []
        for k, area in enumerate(areas_of_interest):
            for i in range(len(area.boxes)):
                x1, y1, x2, y2 = map(int, area.boxes[i].xyxy[0])
                x1, x2, y1, y2 = int(x1 * scale_x), int(x2 * scale_x), int(y1 * scale_y), int(y2 * scale_y) # Bounding boxes need to be rescaled as we previously changed frames size
                conf = area.boxes[i].conf.item()
                match len(images.shape):
                    case 3:
                        cropped_image = images[y1:y2, x1:x2]
                    case 4:
                        cropped_image = images[k][y1:y2, x1:x2]
                    case _:
                        raise ValueError("Input images must have shape [H, W, C] or [N, H, W, C]")
                detections.append({"bbox": [x1, y1, x2, y2], "conf": conf, "frame_id": k, f"cropped_{area_type}": cropped_image})
    
        return detections
    
def link_faces_to_bodies(detections, body_detections):
    """
    Link faces to bodies based on bounding box overlap.
    """
    linked_detections = []

    for face in detections:
        face_bbox = face["bbox"]  # Face bounding box 
        body_faces_candidates = []

        for id, body in enumerate(body_detections):
            body_bbox = body["bbox"]  # Body bounding box 

            # Check if the face is inside the body bounding box
            if (
                face_bbox[0] >= body_bbox[0] and 
                face_bbox[1] >= body_bbox[1] and 
                face_bbox[2] <= body_bbox[2] and  
                face_bbox[3] <= body_bbox[3]    
            ):
                # Compute IoU
                iou = compute_I_o_U(face_bbox, body_bbox)
                body_faces_candidates.append((body, id, iou))
        
        match len(body_faces_candidates):
            case 0:
                # No body found for this face, add the face only
                linked_detections.append({
                    "body_bbox": face["bbox"],
                    "bbox": face["bbox"],
                    "gender": face["gender"],
                    "age": face["age"],
                    "ethnicity": face["ethnicity"]
                })
            
            case _:
                # Sort candidates by IoU and take the one with the highest IoU
                body_faces_candidates.sort(key=lambda x: x[2], reverse=True)
                body, id, _= body_faces_candidates[0]  # Take the body with the highest IoU
                body_detections.pop(id)  # Remove the body from the list to avoid duplicates
                # Add the linked face and body to the list
                linked_detections.append({
                    "body_bbox": body["bbox"],
                    "bbox": face["bbox"],
                    "gender": face["gender"],
                    "age": face["age"],
                    "ethnicity": face["ethnicity"]
                })

    return linked_detections

def compute_I_o_U(face_bbox, body_bbox):
    """
    Compute the Intersection over Union (IoU) between two bounding boxes.
    
    Parameters:
        face_bbox (list): Bounding box of the face [x1, y1, x2, y2].
        body_bbox (list): Bounding box of the body [x1, y1, x2, y2].

    Returns:
        float: IoU value.
    """
    # Calculate the coordinates of the intersection rectangle
    x1_inter = max(face_bbox[0], body_bbox[0])
    y1_inter = max(face_bbox[1], body_bbox[1])
    x2_inter = min(face_bbox[2], body_bbox[2])
    y2_inter = min(face_bbox[3], body_bbox[3])

    # Calculate the area of intersection rectangle
    inter_area = max(0, x2_inter - x1_inter) * max(0, y2_inter - y1_inter)

    # Calculate the area of both bounding boxes
    face_area = (face_bbox[2] - face_bbox[0]) * (face_bbox[3] - face_bbox[1])
    body_area = (body_bbox[2] - body_bbox[0]) * (body_bbox[3] - body_bbox[1])

    # Calculate the area of union
    union_area = face_area + body_area - inter_area

    # Calculate IoU
    iou = inter_area / union_area if union_area > 0 else 0

    return iou