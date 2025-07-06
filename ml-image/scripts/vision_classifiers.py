import numpy as np
import torch
from torch.utils.data import DataLoader
from torchvision import transforms, models

from .utils import ImageDataset

# https://github.com/alihassanml/Yolo11-Face-Emotion-Detection
# Face emotion detection ?


class VisionClassifier:
    def __init__(self, device: str = None, num_cpu_threads: int = 1) -> None:
        # add more models here as we see fit, can also swap current models for smaller models

        if not device:
            self.device = torch.device(
                'cuda') if torch.cuda.is_available() else torch.device('cpu')
        else:
            self.device = torch.device(device)

        torch.set_num_threads(num_cpu_threads)

        self.model_fair_7 = models.resnet34(weights=models.ResNet34_Weights.IMAGENET1K_V1)
        # self.model_fair_7 = models.resnet34(pretrained=True)
        self.model_fair_7.fc = torch.nn.Linear(
            self.model_fair_7.fc.in_features, 18)
        fair_7_state_dict = torch.load(
            'models/res34_fair_align_multi_7_20190809.pt', map_location=self.device)
        self.model_fair_7.load_state_dict(fair_7_state_dict)
        self.model_fair_7.to(self.device).eval()
        # https://github.com/dchen236/FairFace/tree/master
        # weights available @ https://drive.google.com/file/d/113QMzQzkBDmYMs9LwzvD-jxEZdBQ5J4X/view?usp=drive_link

    def predict_age_gender_ethnicity(
            self, faces: list, batch_size: int = 64, expose_confs: bool = False
    ) -> tuple[list, list, list, list, list, list]:

        ethnicity_labels = {
            0: 'White', 1: 'Black', 2: 'Latino_Hispanic', 3: 'East Asian',
            4: 'Southeast Asian', 5: 'Indian', 6: 'Middle Eastern',
        }

        gender_labels = {
            0: 'Male', 1: 'Female',
        }

        age_labels = {
            0: '0-2', 1: '3-9', 2: '10-19', 3: '20-29', 4: '30-39',
            5: '40-49', 6: '50-59', 7: '60-69', 8: '70+',
        }

        inference_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Resize((224, 224)),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[
                                 0.229, 0.224, 0.225]),
        ])

        transformed_faces = ImageDataset(faces, inference_transform)
        dataloader = DataLoader(
            transformed_faces, batch_size=batch_size, shuffle=False, num_workers=0)

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
                age_results = torch.max(
                    torch.softmax(age_outputs, dim=1), dim=1)
                gender_results = torch.max(
                    torch.softmax(gender_outputs, dim=1), dim=1)
                ethnicity_results = torch.max(
                    torch.softmax(ethnicity_outputs, dim=1), dim=1)

                ages.extend(age_results.indices.tolist())
                genders.extend(gender_results.indices.tolist())
                ethnicities.extend(ethnicity_results.indices.tolist())

                if expose_confs:
                    age_confs = torch.softmax(age_outputs, dim=1).tolist()
                    gender_confs = torch.softmax(
                        gender_outputs, dim=1).tolist()
                    ethnicity_confs = torch.softmax(
                        ethnicity_outputs, dim=1).tolist()
                    age_confidences.extend(age_confs)
                    gender_confidences.extend(gender_confs)
                    ethnicity_confidences.extend(ethnicity_confs)
                else:
                    age_confidences.extend(age_results.values.tolist())
                    gender_confidences.extend(gender_results.values.tolist())
                    ethnicity_confidences.extend(
                        ethnicity_results.values.tolist())

        ages = [age_labels[age] for age in ages]
        genders = [gender_labels[gender] for gender in genders]
        ethnicities = [ethnicity_labels[ethnicity]
                       for ethnicity in ethnicities]

        return ages, genders, ethnicities, age_confidences, gender_confidences, ethnicity_confidences


def classify_faces(
        filtered_detections: list[dict], batch_size: int, device: str, source_type: str="trailer", gender_conf_threshold: float = 0.965932283883782, age_conf_threshold: float = 0.5956672158338605, ethnicity_conf_threshold: float = 0.810392266540905
        ) -> tuple[list[dict], list[np.array]]:
    # Classify all filtered faces
    classifier = VisionClassifier(device=device)
    
    flattened_faces = [det["cropped_face"] for det in filtered_detections]
    if len(flattened_faces) > 0:
        ages, genders, ethnicities, age_confs, gender_confs, ethnicity_confs = classifier.predict_age_gender_ethnicity(
            flattened_faces, batch_size = batch_size)

        match source_type:
            case "trailer":
                for i, det in enumerate(filtered_detections):
                    det["gender"] = genders[i] if gender_confs[i] >= gender_conf_threshold else "unknown"
                    det["gender_conf"] = gender_confs[i]
                    det["age"] = ages[i] if age_confs[i] >= age_conf_threshold else "unknown"
                    det["age_conf"] = age_confs[i]
                    det["ethnicity"] = ethnicities[i] if ethnicity_confs[i] >= ethnicity_conf_threshold else "unknown"
                    det["ethnicity_conf"] = ethnicity_confs[i]
            
            case "poster":
                for i, det in enumerate(filtered_detections):
                    det["gender"] = genders[i]
                    det["age"] = ages[i]
                    det["ethnicity"] = ethnicities[i]

            case _:
                raise ValueError(f"Invalid source_type: {source_type}. Choose either 'trailer' or 'poster'.")
    
    return filtered_detections, flattened_faces
