import numpy as np
from facenet_pytorch import InceptionResnetV1
from dlib import chinese_whispers_clustering, vector

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
                self.model = InceptionResnetV1(
                    pretrained='vggface2').eval().to(self.device)
            case _:
                raise ValueError("Model not supported")

    def get_embedding(self, batch_size: int, detected_faces: list):
        # Transformation for model compliance
        match self.model_name:
            case "facenet":
                face_transform = transforms.Compose([
                    transforms.ToTensor(),          # Convertir en tenseur
                    # Taille attendue par FaceNet
                    transforms.Resize((160, 160)),
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
        # Convert to numpy array for use in clustering algorithms
        embeddings_array = embeddings.numpy()

        return embeddings_array


class FacesClustering:
    def __init__(self, model="chinese_whispers", threshold: float = 0.92,  **kwargs):
        self.model = model
        self.threshold = threshold
        self.parameters = kwargs
        self.persons = {}

    def cluster_faces(self, embedded_faces_array: np.array):
        match self.model:
            case "chinese_whispers":
                encoded_faces = [vector(encoding)
                                 for encoding in embedded_faces_array]
                labels = chinese_whispers_clustering(
                    encoded_faces, threshold=self.threshold)
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

    def compute_weighted_vote(self, attribute: str, label: int):
        voting_dict = {}
        persons = self.persons[label]
        for person in persons:
            if person[attribute] in voting_dict:
                voting_dict[person[attribute]] += person["weight"]
            else:
                voting_dict[person[attribute]] = person["weight"]
        if "unknown" in voting_dict and len(voting_dict) > 1: 
            del voting_dict["unknown"]
        voted_attribute = max(voting_dict, key=lambda k: voting_dict[k])
        return voted_attribute
    
    def aggregate_estimations(self, persons_list: list, faces_list: list, fps, total_area, method="majority", min_occurence=0.03):
        self.apply_clusters(persons_list, faces_list)
        aggregated_persons = []

        final_label = 0
        total_persons = np.sum([len(persons) for persons in self.persons.values()])
        for label, persons in self.persons.items():
            if len(persons) / total_persons >= min_occurence:
                match method:
                    case "majority":
                        aggregated_age = self.compute_weighted_vote("age", label)
                        aggregated_gender = self.compute_weighted_vote("gender", label)
                        aggregated_ethnicity = self.compute_weighted_vote("ethnicity", label)
                        occurence = len(persons)/fps
                        area_occupied = float(sum([np.abs(x1 - x2) * np.abs(y1 - y2)
                                                   for (x1, y1, x2, y2) in [person["bbox"] for person in persons]])/(total_area*len(persons)))
                        frames_id = [person["frame_id"]
                                      for person in persons]
                        persons_bboxes = [person["bbox"]
                                        for person in persons]
                        persons_ids = [person["person_id"]
                                       for person in persons]
                        frames_to_bboxes = dict(zip(frames_id, persons_bboxes))
                        aggregated_persons.append({"age": aggregated_age, "gender": aggregated_gender, "ethnicity": aggregated_ethnicity,
                                                   "occurence": occurence, "area occupied": area_occupied, "label": final_label, "frames_bboxes": frames_to_bboxes, "persons_ids" : persons_ids})
                        #print(f"Character {final_label} : {occurence:.2f} seconds on screen, {len(persons) / total_persons * 100:.2f}% of the total, age: {aggregated_age}, gender: {aggregated_gender}, ethnicity: {aggregated_ethnicity}")
                    case _:
                        raise ValueError(f"Method  {method} not supported")
                
                final_label += 1
        
        return aggregated_persons
