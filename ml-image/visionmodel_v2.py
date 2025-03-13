from copy import deepcopy
import json
import numpy as np
import requests

from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

import torch
from torchvision import transforms

import model_architectures

# https://github.com/alihassanml/Yolo11-Face-Emotion-Detection
# Face emotion detection ?

class VisionModel :
    def __init__(self, device:str = None, num_cpu_threads:int = 1) -> None:
        # add more models here as we see fit, can also swap current models for smaller models
        
        if not device :
            self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        else :
            self.device = torch.device(device)

        torch.set_num_threads(num_cpu_threads)

        self.yolo_model_person = YOLO('models/yolo11l.pt').to(self.device)
        #https://github.com/ultralytics/ultralytics
    
        self.yolo_model_face = YOLO('models/yolov11l-face.pt').to(self.device)
        #https://github.com/akanametov/yolo-face
    
        self.age_gender_model = model_architectures.AgeGenderModel().to(self.device)
        weights = torch.load('models/age_gender_weights.pt', map_location=self.device)
        self.age_gender_model.load_state_dict(weights)
        self.age_gender_model.eval()
        #https://github.com/manhcuong02/Pytorch-Age-Estimation/tree/main
        # rename weights file to 'age_gender_weights.pt'
        # weights available @ https://drive.google.com/file/d/1_JNOsSl9kY082VVs5TcU1aoRcCGN1cBh/view?usp=sharing

        self.ethnicity_detection_model = model_architectures.EthnicityModel().to(self.device)
        ethnicity_state_dict = torch.load('models/ethnicity_detection.ckpt', map_location = self.device)['state_dict']
        self.ethnicity_detection_model.load_state_dict(ethnicity_state_dict)
        self.ethnicity_detection_model.eval()
        #https://github.com/anasserhussien/EthnicityRecognition-UTKFaces/tree/main?tab=readme-ov-file


    def get_data_from_url(self, url: str, 
                          output_poster: str = 'downloaded_poster', 
                          output_trailer: str = 'downloaded_trailer') -> None:
        """
        Download poster and trailer from a given Allocine URL (only works for allocine)
        """
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # to download trailer
        figure_tag = soup.find('figure', class_='player')
        if not figure_tag :
            video_path = ""
        else :
            video_path = f'{output_trailer}.mp4'
            data_model = figure_tag['data-model']
            data_model = json.loads(data_model)
            video_sources = data_model['videos'][0]['sources']
            if "high" in video_sources :
                link = video_sources["high"]
            if "medium" in video_sources :
                link = video_sources["medium"]
            else :
                link = video_sources["low"]
            r = requests.get(link, stream = True)
            with open(video_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size = 1024*1024) :
                    if chunk:
                        f.write(chunk)

        # to download poster
        poster_path = f'{output_poster}.jpg'
        poster_tag = soup.find('meta', property = 'og:image')
        poster_url = poster_tag['content']
        r = requests.get(poster_url, stream = True)
        with open(poster_path, 'wb') as f :
            for chunk in r :
                f.write(chunk)
        
        self.url = url
        self.poster_path = poster_path
        self.trailer_path = video_path
        self.image = Image.open(poster_path)

    def get_data_from_file(self, file_path:str, filetype:str = "poster") -> None:
        """
        Load data to class from local file for either a 'poster' or 'trailer' file
        """
        if filetype == "poster" :
            self.poster_path = file_path
            self.image = Image.open(file_path)
        elif filetype == "trailer" :
            self.trailer_path = file_path
        else :
            raise ValueError("filetype needs to be one of ['poster', 'trailer']")

    def get_areas_of_interest(
            self, images:list[Image], area_type:str = "face", confidence_cutoff:float = 0.5, area_threshold:float = 0.01
            ) -> tuple[list, list, list]:
        """
        Extract areas of interest (faces, silhouettes) from a list of images.
        """
        if area_type == "face" :
            results = self.yolo_model_face(images, device=self.device)
        else :
            results = self.yolo_model_person(images, device=self.device)

        all_boxes = []
        all_confs = []
        all_names = []
        for image, result in zip(images, results) :
            area_names = [result.names[cls.item()] for cls in result.boxes.cls.int()]  # class name
            area_confs = result.boxes.conf  # confidence score
            boxes = []
            confs = []
            names = []
            image_area = image.width * image.height

            for i in range(len(result.boxes)):
                box = result.boxes[i].xyxy.squeeze().tolist()
                box_area = np.abs(box[2] - box[0]) * np.abs(box[3] - box[1])
                if (area_names[i] == area_type) and (area_confs[i] > confidence_cutoff) and (box_area / image_area > area_threshold) :
                    boxes.append(box)
                    confs.append(area_confs[i])
                    names.append(area_names[i])
            all_boxes.append(boxes)
            all_confs.append(confs)
            all_names.append(names)
        
        return (all_boxes, all_confs, all_names)

    def crop_image_to_boundingbox(self, image: Image, bounding_box: list) -> Image:
        """
        Create a subimage from a complete image given a list containing the coordinates of a single bounding box
        """
        cropped_image = image.crop(bounding_box)
        return cropped_image

    def crop_areas_of_interest(
            self, images: list[Image], area_type:str = 'face', confidence_cutoff:float = 0.5, area_threshold:float = 0.01
            ) -> None:
        """
        Create individual subimages for all areas of interest in one image
        """ 
        all_boxes, all_confs, all_names = self.get_areas_of_interest(images, area_type=area_type, confidence_cutoff=confidence_cutoff,area_threshold=area_threshold)
        cropped_images = []
        for i in range(len(all_boxes)) :
            cropped_images.append([self.crop_image_to_boundingbox(images[i], box) for box in all_boxes[i]])
        
        #add attributes to the class, the name follows kwarg 'area_type'
        setattr(self, f'cropped_{area_type}s', cropped_images)
        setattr(self, f'cropped_{area_type}s_boxes', all_boxes)

    def flatten_list_areas_of_interest(
            self, images: list[Image], area_type:str = 'face'
    ) -> tuple[list, list]:
        """
        Function to unravel a nested list of extracted areas of interest (e.g. faces, persons) while retaining the id of the image they were extracted from. 
        Returns the images as a flat list and their corresponding image ids 
        """
        areas_of_interest = getattr(self, f'cropped_{area_type}s')
        flattened_areas_of_interest, image_ids = [], []
        for i in range(len(areas_of_interest)) :
            for j in range(len(areas_of_interest[i])) :
                flattened_areas_of_interest.append(areas_of_interest[i][j])
                image_ids.append(i)
        return (flattened_areas_of_interest, image_ids)

    def draw_bounding_boxes(self, image: Image, boxes: list, confs: list, names: list, fill:tuple = (255, 0, 0, 255)) -> None:
        draw_image = image.copy()
        draw = ImageDraw.Draw(draw_image)
        font = ImageFont.load_default(size = 12)
        for i, box in enumerate(boxes) :
            draw.rectangle(box, outline=fill, width=3)
            txt = f"{names[i]} ({confs[i]:.2f})"
            draw.text((box[0], box[1] - 1), txt, anchor="lb", fill=fill, font=font)
        draw_image.show()

    def predict_age_gender(self, faces: list) -> tuple[list, list]:
        """ 
        Predict age, gender and ethnicity for a list of cropped faces
        """
        dict_gender = {
            0 : 'male',
            1 : 'female',
            }
        
        inference_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Resize(size=(64,64)),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
            ])
        
        transformed_faces = torch.stack([inference_transform(face) for face in faces])
        with torch.no_grad() :
            genders, ages = self.age_gender_model(transformed_faces)
        genders, ages = np.round(genders), np.round(ages)
        genders = [dict_gender[int(pred)] for pred in genders]
        ages = ages.flatten().tolist()
        return (genders, ages)
    
    def predict_ethnicity(self, faces: list) -> list:
        """
        Predict ethnicities from a list of cropped faces
        """
        ethnicity_labels = {
            0 : "white", 
            1 : "black", 
            2 : "asian", 
            3 : "indian",
            }
        
        inference_transform = transforms.Compose([
            transforms.Resize(size=128),
            transforms.CenterCrop(size=104),
            transforms.ToTensor(),
            transforms.Normalize( [0.5, 0.5, 0.5],[0.5, 0.5, 0.5])
            ])
        
        transformed_faces = torch.stack([inference_transform(face) for face in faces])
        with torch.no_grad() :
            outputs = self.ethnicity_detection_model(transformed_faces)
        _, predicted = torch.max(outputs.data, 1)
        ethnicities = [ethnicity_labels[prediction] for prediction in predicted.tolist()]
        return ethnicities
