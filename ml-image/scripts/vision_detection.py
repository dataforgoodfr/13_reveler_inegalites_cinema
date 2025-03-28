import cv2

from ultralytics import YOLO
import numpy as np

import torch
from torch.utils.data import DataLoader
from torchvision import transforms

from utils import ImageDataset

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

        frames_transform = transforms.Compose([
            transforms.Lambda(lambda img: bgr_to_rgb(img)),
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
                    detections = self.yolo_model_face(batch, verbose=False) 
                    results.extend(detections)
            else :
                for batch in dataloader:
                    batch = batch.to(self.device)
                    detections = self.yolo_model_person(batch, verbose=False, classes=[0]) ### Review: Add class condition here
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
                cropped_image = images[k][y1:y2, x1:x2]
                detections.append({"bbox": [x1, y1, x2, y2], "conf": conf, "frame_id": k, f"cropped_{area_type}": cropped_image})
    
        return detections