from PIL import Image
import numpy as np
from facenet_pytorch import InceptionResnetV1
from dlib import chinese_whispers_clustering, vector
import statistics

import torch
from torch.utils.data import DataLoader
from torchvision import transforms

from .utils import ImageDataset
    
class EmbeddingModel:
    def __init__(self, model: str = "facenet", device: str = 'cpu'):
        self.device = device
        self.model_name = model

        match self.model_name:
            case "facenet":
                self.model = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
            case _:
                raise ValueError("Model not supported")

    def get_embedding(self, batch_size: int, detected_faces: list):
        # Transformation for model compliance
        match self.model_name:
            case "facenet":
                face_transform = transforms.Compose([
                transforms.ToTensor(),          # Convertir en tenseur
                transforms.Resize((160, 160)),  # Taille attendue par FaceNet
                transforms.Normalize([0.5], [0.5])  # Normalisation [-1, 1]
                ])
            case _:
                raise ValueError("Model not supported")

        dataset = ImageDataset(detected_faces, face_transform)
        dataloader = DataLoader(dataset, batch_size=batch_size, num_workers=0)

        embeddings = []

        with torch.no_grad(): 
            for batch in dataloader:
                batch = batch.to(self.device)
                emb = self.model(batch)
                embeddings.append(emb.cpu())

        if len(embeddings) == 0:
            return np.array([])

        embeddings = torch.cat(embeddings)  # Concatenate all embeddings
        embeddings_array = embeddings.numpy() # Convert to numpy array for use in clustering algorithms

        return embeddings_array

class FacesClustering:
    def __init__(self, model = "chinese_whispers", threshold: float = 0.92,  **kwargs):
        self.model = model
        self.threshold = threshold
        self.parameters = kwargs
        self.persons = {}
    
    def cluster_faces(self, embedded_faces_array: np.array):
        match self.model:
            case "chinese_whispers":
                encoded_faces = [vector(encoding) for encoding in embedded_faces_array]
                labels = chinese_whispers_clustering(encoded_faces, threshold=self.threshold)
            case _:
                raise ValueError("Model not supported")
        
        return labels
    
    def apply_clusters(self, persons_list: list, faces_list: list):
        labels = self.cluster_faces(faces_list)
        
        for i in range(len(persons_list)):
            label, person = labels[i], persons_list[i]
            person["person_id"] = i
            if label not in self.persons:
                self.persons[label] = [person]
            else:
                self.persons[label].append(person)
    
    def aggregate_estimations(self, persons_list: list, faces_list: list, method = "majority", min_occurence = 0.03):
        self.apply_clusters(persons_list, faces_list)
        aggregated_persons = []

        final_label = 0
        total_persons = np.sum([len(persons) for persons in self.persons.values()])
        for label, persons in self.persons.items():
            print(f"Character {label} : {len(persons)} occurences, {len(persons) / total_persons * 100:.2f}% of the total")
            if len(persons) / total_persons >= min_occurence:
                match method:
                    case "majority":
                        aggregated_age = statistics.mode([person["age"] for person in persons if person["age"] != "unknown"]) if len([person["age"] for person in persons if person["age"] != "unknown"]) > 0 else "unknown"
                        aggregated_gender = statistics.mode([person["gender"] for person in persons if person["gender"] != "unknown"]) if len([person["gender"] for person in persons if person["gender"] != "unknown"]) > 0 else "unknown"
                        aggregated_ethnicity = statistics.mode([person["ethnicity"] for person in persons if person["ethnicity"] != "unknown"]) if len([person["ethnicity"] for person in persons if person["ethnicity"] != "unknown"]) > 0 else "unknown"
                        occurence = len(persons)
                        area_occupied = sum([np.abs(x1 - x2) * np.abs(y1 - y2) for (x1, y1, x2, y2) in [person["bbox"] for person in persons]])
                        persons_id = [person["person_id"] for person in persons]
                        aggregated_persons.append({"age": aggregated_age, "gender": aggregated_gender, "ethnicity": aggregated_ethnicity, "occurence": occurence, "area occupied": area_occupied, "persons_id": persons_id, "label": final_label})
                    case _:
                        raise ValueError(f"Method  {method} not supported")
                
                final_label += 1
        
        return aggregated_persons