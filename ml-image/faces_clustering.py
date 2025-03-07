from PIL import Image
import numpy as np
from facenet_pytorch import InceptionResnetV1
from dlib import chinese_whispers_clustering, vector
import statistics
import torch
from torch.utils.data import Dataset, DataLoader

class Person():
    def __init__(self, age: float, gender: str, ethnicity: str):
        self.age = age
        self.gender = gender
        self. ethnicity = ethnicity

class Frame_person(Person):
    def __init__(self, age: float, gender: str, ethnicity: str, face: Image, bbox: list, frame_id: int, face_id: int):
        super().__init__(age, gender, ethnicity)
        self.face = face
        self.bbox = bbox
        self.frame_id = frame_id
        self.face_id = face_id

class Video_person(Person):
    def __init__(self, age: float, gender: str, ethnicity: str, occurence: int, area: float, faces_id: list, person_id: int):
        super().__init__(age, gender, ethnicity)
        self.area_occupied = area
        self.occurence = occurence
        self.faces_id = faces_id
        self.person_id = person_id
    
    def __repr__(self):
        return f"Character w/ estimated age: {self.age}, gender: {self.gender}, ethnicity: {self.ethnicity}. This character appears {self.occurence} time(s) on screen and covers {self.area_occupied:.2f} total area."
    
    def show_faces(self, persons_list: list, max_faces: int = 25):
        faces = [person.face for person in persons_list if person.face_id in self.faces_id]
        
        # Limit the number of faces to display
        if len(faces) > max_faces:
            step = len(faces) // max_faces
            faces = faces[::step][:max_faces]
        
        # Determine the grid size
        grid_size = int(np.ceil(np.sqrt(len(faces))))
        
        # Get the size of each face image
        face_width, face_height = faces[0].size
        
        # Create a blank image for the grid
        grid_image = Image.new('RGB', (grid_size * face_width, grid_size * face_height))
        
        # Paste faces into the grid image
        for i, face in enumerate(faces):
            row = i // grid_size
            col = i % grid_size
            grid_image.paste(face, (col * face_width, row * face_height))
        
        # Display the grid image
        grid_image.show()
    
class Embedding_model():
    def __init__(self, model = "facenet", transform = None, device = 'cpu'):
        self.device = device
        match model:
            case "facenet":
                self.model = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
            case _:
                raise ValueError("Model not supported")
        self.transform = transform

    def get_embedding(self, batch_size: int, detected_faces: list):
        dataset = ImageDataset(detected_faces, self.transform)
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

class Faces_clustering():
    def __init__(self, model = "chinese_whispers", **kwargs):
        self.model = model
        self.parameters = kwargs
        self.persons = {}
    
    def cluster_faces(self, embedded_faces_array: np.array):
        match self.model:
            case "chinese_whispers":
                encoded_faces = [vector(encoding) for encoding in embedded_faces_array]
                threshold = self.parameters.get('threshold', 0.5)
                labels = chinese_whispers_clustering(encoded_faces, threshold=threshold)
            case _:
                raise ValueError("Model not supported")
        
        return labels
    
    def cluster_persons(self, persons_list: list, faces_list: list):
        labels = self.cluster_faces(faces_list)
        
        for label, person in zip(labels, persons_list):
            if label not in self.persons:
                self.persons[label] = [person]
            else:
                self.persons[label].append(person)
        
    
    def aggregate_estimations(self, persons_list: list, faces_list: list, method = "majority"):
        self.cluster_persons(persons_list, faces_list)
        aggregated_persons = []

        for label, persons in self.persons.items():
            match method:
                case "majority":
                    new_age = statistics.mode([person.age for person in persons])
                    new_gender = statistics.mode([person.gender for person in persons])
                    new_ethnicity = statistics.mode([person.ethnicity for person in persons])
                    occurence = len(persons)
                    area_occupied = sum([np.abs(x1 - x2) * np.abs(y1 - y2) for (x1, y1, x2, y2) in [person.bbox for person in persons]])
                    persons_id = [person.face_id for person in persons]
                    aggregated_persons.append(Video_person(new_age, new_gender, new_ethnicity, occurence, area_occupied, persons_id, label))
                case _:
                    raise ValueError("Method not supported")
        
        return aggregated_persons

class ImageDataset(Dataset):
    # Dataset builder for array images for specific PyTorch model compliance
    def __init__(self, image_array, transform):
        self.image = image_array
        self.transform = transform # Please change the transformation (resize, normalize...) to comply w/ the used model
        
    def __len__(self):
        return len(self.image)

    def __getitem__(self, idx):
        image = self.image[idx]
        if self.transform:
            return self.transform(image)
        raise ValueError("No transformation provided")