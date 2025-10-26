import numpy as np
import torch

from torch.utils.data import DataLoader
from torchvision import transforms
from facenet_pytorch import InceptionResnetV1
from dlib import chinese_whispers_clustering, vector
from loguru import logger

from scripts import filter_detections
from scripts import utils

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

        dataset = utils.ImageDataset(detected_faces, face_transform)
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


class FacesClusterer:
    def __init__(self, model: str ="chinese_whispers", threshold: float = 0.92,  **kwargs):
        self.model = model
        self.threshold = threshold
        self.parameters = kwargs
        self.persons = {}

    def get_clustering_labels(self, embedded_faces_array: np.ndarray):
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
        '''
        Determine a cluster for each detected faces and register them.
        '''
        labels = self.get_clustering_labels(faces_list)

        for i in range(len(persons_list)):
            if i==14:
                logger.debug(f'le label du person_id {i}: {labels[i]}')
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
    
    def aggregate_estimations(self, persons_list: list, faces_list: list, fps, total_area, method="majority", min_occurence=0.03) -> list[dict]:
        self.apply_clusters(persons_list, faces_list)
        aggregated_persons = []

        final_label = 0
        total_persons = np.sum([len(persons) for persons in self.persons.values()])
        for label, persons in self.persons.items():
            logger.debug(f'Aggregation des résultats sur le label: {label}')
            if len(persons) / total_persons >= min_occurence:
                logger.debug(f'Le label: {label} valide les conditions minimales pour être conservé')
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
                        frames_to_bboxes = dict(zip(frames_id, persons_bboxes, strict=False))
                        aggregated_persons.append({"age": aggregated_age, "gender": aggregated_gender, "ethnicity": aggregated_ethnicity,
                                                   "occurence": occurence, "area occupied": area_occupied, "label": final_label, "frames_bboxes": frames_to_bboxes, "persons_ids" : persons_ids})
                        #print(f"Character {final_label} : {occurence:.2f} seconds on screen, {len(persons) / total_persons * 100:.2f}% of the total, age: {aggregated_age}, gender: {aggregated_gender}, ethnicity: {aggregated_ethnicity}")
                    case _:
                        raise ValueError(f"Method {method} not supported")
                
                final_label += 1
            else:
                logger.debug(f'/!\ Le label: {label} ne valide pas les conditions minimales pour être conservé')
        
        return aggregated_persons


def embed_faces(flattened_faces: list[np.ndarray], batch_size: int, device: str) -> np.ndarray:
    # Embed faces
    embedding_model = EmbeddingModel(device=device)
    embedded_faces = embedding_model.get_embedding(
        batch_size=batch_size, detected_faces=flattened_faces)

    return embedded_faces


def cluster_faces(embedded_faces: np.ndarray, model: str, threshold: float, classified_faces: list[dict], method: str, fps: int, effective_area: float) -> list[dict]:
    # Cluster faces and aggregate predictions for each character
    faces_clusterer = FacesClusterer(
        model=model, threshold=threshold)
    aggregated_estimations = faces_clusterer.aggregate_estimations(
        classified_faces, embedded_faces, fps, effective_area, method=method)

    return aggregated_estimations

def assign_poster(embedded_faces_poster: list[dict], embedded_faces: list[np.ndarray], aggregated_estimations: list[dict], filtered_detections: list[dict], total_area: float, poster: np.ndarray, store_visuals: bool) -> list:
    """
    Given a list of embedded faces detected on a poster and a list of embedded_faces from predicted characters of a trailer,
    returns the character id w/ its characteristics predicted from trailer.
    Args:
        - embedded_faces_poster: Embedded faces from the poster
        - embedded_faces: Embedded faces from the trailer
        - aggregated_estimations: Global predictions on the trailer
        - filtered_detections: ...
        - total_area: ...
        - poster: The image of the poster
        - store_visuals: True or False. If True, will store predictions drawn on the poster.

    """
    #FIXME: filtered_detections & aggregated_estimations have some common info
    indexes_to_del = []
    for index, face in enumerate(embedded_faces_poster):
        closest_index = None
        closest_distance = float("inf")  # Distance initiale très grande

        #closest_index = int(np.argmin(np.linalg.norm(face - np.array(embedded_faces), axis = 1)))

        # Comparer avec chaque embedding dans embedded_faces
        for embedded_face in embedded_faces:
            i, cluster_embedding = embedded_face
        # Calculer la distance Euclidienne entre les embeddings
            distance = np.linalg.norm(face - np.array(cluster_embedding))

            # Mettre à jour si une distance plus petite est trouvée
            if distance < closest_distance:
                closest_distance = distance
                closest_index = i

        # Assigner le label correspondant à l'index le plus proche
        if closest_index is not None:
            logger.debug(f"Assignation du label {closest_index} à l'index {index}")
            for video_person in aggregated_estimations:
                logger.debug(f'La liste des persons_ids : {video_person["persons_ids"]}')
                if closest_index in video_person["persons_ids"]:
                    filtered_detections[index]["gender"] = video_person["gender"]
                    filtered_detections[index]["age"] = video_person["age"]
                    logger.debug(f"l'age du cluster qui lui est assigné: {video_person['age']}")
                    filtered_detections[index]["ethnicity"] = video_person["ethnicity"]

            occupied_area = filter_detections.compute_area(filtered_detections[index]["bbox"], total_area)
            filtered_detections[index]["occupied_area"] = occupied_area
        else:
            indexes_to_del.append(index)
    # Delete the detection from filtered_detections
    filtered_detections = [det for i, det in enumerate(filtered_detections) if i not in indexes_to_del]

    if store_visuals :
        # Draw predictions on poster
        utils.draw_predictions_on_poster(poster, filtered_detections)

    return filtered_detections