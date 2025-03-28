import numpy as np

import torch
from torch.utils.data import DataLoader
from torchvision import transforms, models

from . import model_architectures
from .utils import ImageDataset

# https://github.com/alihassanml/Yolo11-Face-Emotion-Detection
# Face emotion detection ?

class VisionClassifier :
    def __init__(self, device:str = None, num_cpu_threads:int = 1) -> None:
        # add more models here as we see fit, can also swap current models for smaller models
        
        if not device :
            self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        else :
            self.device = torch.device(device)

        torch.set_num_threads(num_cpu_threads)
        
        self.H_resized, self.W_resized = 640, 640
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

        self.model_fair_7 = models.resnet34(pretrained=True)
        self.model_fair_7.fc = torch.nn.Linear(self.model_fair_7.fc.in_features, 18)
        fair_7_state_dict = torch.load('models/res34_fair_align_multi_7_20190809.pt', map_location = self.device)
        self.model_fair_7.load_state_dict(fair_7_state_dict)
        self.model_fair_7.to(self.device).eval()
        #https://github.com/dchen236/FairFace/tree/master
        # weights available @ https://drive.google.com/file/d/113QMzQzkBDmYMs9LwzvD-jxEZdBQ5J4X/view?usp=drive_link

    def predict_age_gender(self, faces: list, batch_size: int = 64) -> tuple[list, list]:
        """ Predict age, gender and ethnicity for a cropped face """
        dict_gender = {
            0 : 'male',
            1 : 'female',
            }
        
        inference_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Resize(size=(64,64)),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
            ])
        
        transformed_faces = ImageDataset(faces, inference_transform)
        dataloader = DataLoader(transformed_faces, batch_size=batch_size, shuffle=False, num_workers=0)

        genders, ages = [], []
        with torch.no_grad():
            for batch in dataloader:
                batch = batch.to(self.device)
                results = self.age_gender_model(batch)
                genders.extend(results[0].cpu().numpy().flatten())
                ages.extend(results[1].cpu().numpy().flatten())

        genders = [dict_gender[int(np.round(pred))] for pred in genders]
        return genders, ages
    
    def predict_ethnicity(self, faces: list, batch_size: int = 64) -> list:
        """ Predict ethnicities from a list of cropped faces """
        ethnicity_labels = {
            0 : "white", 
            1 : "black", 
            2 : "asian", 
            3 : "indian",
            }
        
        inference_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Resize(size=128),
            transforms.CenterCrop(size=104),
            transforms.Normalize( [0.5, 0.5, 0.5],[0.5, 0.5, 0.5])
            ])
        
        transformed_faces = ImageDataset(faces, inference_transform)
        dataloader = DataLoader(transformed_faces, batch_size=batch_size, shuffle=False, num_workers=0)

        ethnicities = []
        with torch.no_grad():
            for batch in dataloader:
                batch = batch.to(self.device)
                results = self.ethnicity_detection_model(batch)
                _, predicted = torch.max(results.data, 1)
                ethnicities.extend(predicted.cpu().numpy().flatten())
        ethnicities = [ethnicity_labels[prediction] for prediction in ethnicities]
              
        return ethnicities

    def predict_age_gender_ethnicity(self, faces: list, batch_size: int = 64) -> tuple[list, list, list, list, list, list]:
        ethnicity_labels = {
            0 : 'White', 1 : 'Black', 2 : 'Latino_Hispanic', 3 : 'East Asian',
            4 : 'Southeast Asian', 5 : 'Indian', 6 : 'Middle Eastern',
            }

        gender_labels = {
            0 : 'Male', 1 : 'Female',
            }

        age_labels = {
            0 : '0-2', 1 : '3-9', 2 : '10-19', 3 : '20-29', 4 : '30-39',
            5 : '40-49', 6 : '50-59', 7 : '60-69', 8 : '70+',
            }

        inference_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Resize((224, 224)),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
        
        transformed_faces = ImageDataset(faces, inference_transform)
        dataloader = DataLoader(transformed_faces, batch_size=batch_size, shuffle=False, num_workers=0)

        ages, genders, ethnicities = [], [], []
        age_confidences, gender_confidences, ethnicity_confidences = [], [], []
        with torch.no_grad():
            for batch in dataloader:
                batch = batch.to(self.device)
                outputs = self.model_fair_7(batch)
                outputs_cpu = outputs.detach().cpu()

                age_outputs = outputs_cpu[:, 9:18]
                gender_outputs = outputs_cpu[:, 7:9]
                ethnicity_outputs = outputs_cpu[:, :7]

                # get confidence scores and argmax of predictions
                age_results = torch.max(torch.softmax(age_outputs, dim = 1), dim = 1)
                gender_results = torch.max(torch.softmax(gender_outputs, dim = 1), dim = 1)
                ethnicity_results = torch.max(torch.softmax(ethnicity_outputs, dim = 1), dim = 1)

                ages.extend(age_results.indices.tolist())
                genders.extend(gender_results.indices.tolist())
                ethnicities.extend(ethnicity_results.indices.tolist())

                age_confidences.extend(age_results.values.tolist())
                gender_confidences.extend(gender_results.values.tolist())
                ethnicity_confidences.extend(ethnicity_results.values.tolist())

        ages = [age_labels[age] for age in ages]
        genders = [gender_labels[gender] for gender in genders]
        ethnicities = [ethnicity_labels[ethnicity] for ethnicity in ethnicities]
        
        return ages, genders, ethnicities, age_confidences, gender_confidences, ethnicity_confidences