from copy import deepcopy
import json
import numpy as np
import requests
#import tensorflow.keras as keras
#from nsfw_detector import predict as nsfw_predict

from bs4 import BeautifulSoup
from onnxruntime import InferenceSession
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

import torch
from torchvision import models, transforms

# https://github.com/alihassanml/Yolo11-Face-Emotion-Detection
# Face emotion detection ?

class VisionModel() :
    def __init__(self) :
        # add more models here as we see fit, can also swap current models for smaller models
    
        self.yolo_model_person = YOLO("models/yolo11l.pt")
        #https://github.com/ultralytics/ultralytics
    
        self.yolo_model_face = YOLO("models/yolov11l-face.pt")
        #https://github.com/akanametov/yolo-face
    
        ###broken atm, need to figure out how to get rid of the dependency on tensorflow_hub, shouldn't be too hard
        #self.nsfw_model = nsfw_predict.load_model('models/nsfw_mobilenet_v2_140_224/saved_model.h5')
        #self.nsfw_model = model = keras.models.load_model('models/nsfw_mobilenet_v2_140_224/saved_model.h5',
        #                                                   custom_objects={'KerasLayer': hub.KerasLayer})
    
        #https://github.com/GantMan/nsfw_model
    
        self.age_gender_model = InferenceSession('models/best-epoch47-0.9314.onnx') 
        #https://github.com/Nebula4869/PyTorch-gender-age-estimation/tree/master/models-2020-11-20-14-37
    
        ethnicity_state_dict = torch.load('models/ethnicity_detection.ckpt', map_location = torch.device('cpu'))['state_dict']
        self.ethnicity_detection_model = EthnicityModel()
        self.ethnicity_detection_model.load_state_dict(ethnicity_state_dict)
        self.ethnicity_detection_model.eval()
        #https://github.com/anasserhussien/EthnicityRecognition-UTKFaces/tree/main?tab=readme-ov-file
        #model @ https://shorturl.at/3vRuj

    def get_data_from_url(self, url: str, 
                          output_poster: str = "downloaded_poster", 
                          output_trailer: str = "downloaded_trailer") -> None:
        """ Download poster and trailer from a given Allocine URL (only works for allocine) """
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
        """ Load data to class from local file for either a 'poster' or 'trailer' file """
        if filetype == "poster" :
            self.poster_path = file_path
            self.image = Image.open(file_path)
        elif filetype == "trailer" :
            self.trailer_path = file_path
        else :
            raise ValueError("filetype needs to be one of ['poster', 'trailer']")

    def get_persons(self, image: Image, confidence_cutoff:float = 0) -> tuple:
        # Can add a parameter to filter here based on confidence score if required 
        result = self.yolo_model_person(image)[0]
        names = [result.names[cls.item()] for cls in result.boxes.cls.int()]  # class name of each box
        confs = result.boxes.conf  # confidence score of each box
        person_boxes = [result.boxes[i].xyxy.squeeze().tolist() for i in range(len(result.boxes)) \
                        if (names[i] == "person") & (confs[i] > confidence_cutoff)]
        person_confs = [confs[i] for i in range(len(confs)) \
                        if (names[i] == "person") & (confs[i] > confidence_cutoff)]
        person_names = [names[i] for i in range(len(names)) \
                        if (names[i] == "person") & (confs[i] > confidence_cutoff)]
        return (person_boxes, person_confs, person_names)

    def get_faces(self, image: Image, confidence_cutoff:float = 0.5, area_threshold: float = 0.01) -> tuple:
        # Can add a parameter to filter here based on confidence score if required 
        result = self.yolo_model_face(image)[0]
        names = [result.names[cls.item()] for cls in result.boxes.cls.int()]  # class name
        confs = result.boxes.conf  # confidence score
        face_boxes = []
        face_confs = []
        face_names = []
        image_area = image.width * image.height

        for i in range(len(result.boxes)):
            box = result.boxes[i].xyxy.squeeze().tolist()
            box_area = np.abs(box[2] - box[0]) * np.abs(box[3] - box[1])
            if (names[i] == "face") and (confs[i] > confidence_cutoff) and (box_area / image_area > area_threshold):
                face_boxes.append(box)
                face_confs.append(confs[i])
                face_names.append(names[i])

        return (face_boxes, face_confs, face_names)

    def crop_image_to_boundingbox(self, image: Image, bounding_box: list) -> Image:
        """ Create subimage from complete image and a list of bounding box coordinates """
        cropped_image = image.crop(bounding_box)
        return cropped_image

    def crop_persons(self, image: Image) -> None:
        """ Extract all persons and associated bounding box coordinates from one image """ 
        person_boxes, person_confs, person_names = self.get_persons(image)
        cropped_images = [self.crop_image_to_boundingbox(image, box) for box in person_boxes]
        self.cropped_persons = cropped_images
        self.cropped_persons_boxes = person_boxes

    def crop_faces(self, image: Image) -> None:
        """ Extract all faces and associated bounding box coordinates from one image """ 
        face_boxes, face_confs, face_names = self.get_faces(image)
        cropped_images = [self.crop_image_to_boundingbox(image, box) for box in face_boxes]
        self.cropped_faces = cropped_images
        self.cropped_faces_boxes = face_boxes

    def detect_nsfw(self, images: Image) :
        #broken atm, need to figure out how to get rid of the dependency on tensorflow_hub, shouldn't be too hard
        def preprocess_images(images: list, image_size: tuple) -> np.array:
            preprocessed_images = []
            for image in images :
                preprocessed_image = image.resize(image_size, resample = 0)
                preprocessed_image = keras.preprocessing.image.img_to_array(preprocessed_image)
                preprocessed_image /= 255
                preprocessed_images.append(preprocessed_image)
            return np.asarray(preprocessed_images)

        def classify(model, preprocessed_images: np.array) -> list:
            model_preds = model.predict(preprocessed_images)
            categories = ['drawings', 'hentai', 'neutral', 'porn', 'sexy']
            probs = []
            for i, single_preds in enumerate(model_preds):
                single_probs = {}
                for j, pred in enumerate(single_preds):
                    single_probs[categories[j]] = float(pred)
                aggregated_single_probs = {"sfw" : single_probs["drawings"] + single_probs["neutral"],
                                           "nsfw" : single_probs["hentai"] + single_probs["porn"] + single_probs["sexy"],
                                           }
                probs.append(aggregated_single_probs)
            return probs

        preprocessed_images = preprocess_images(images, (224, 224))
        aggregated_result = classify(self.nsfw_model, preprocessed_images)
        return aggregated_result
    
    def draw_bounding_boxes(self, image: Image, boxes: list, confs: list, names: list, fill:tuple = (255, 0, 0, 255)) -> None:
        # not too useful here, but can be used later on to draw boxes and associated predictions
        draw_image = image.copy()
        draw = ImageDraw.Draw(draw_image)
        font = ImageFont.load_default(size = 12)
        for i, box in enumerate(boxes) :
            draw.rectangle(box, outline=fill, width=3)
            txt = f"{names[i]} ({confs[i]:.2f})"
            draw.text((box[0], box[1] - 1), txt, anchor="lb", fill=fill, font=font)
        draw_image.show()

    def predict_age_gender(self, face: Image) -> tuple :
        """ Predict age and gender for a cropped face """
        ### Pour cette tâche, peut-être possible de prendre plusieurs modèles et de faire un vote à la majorité ?
        ### Adapter l'inférence pour prendre en entrée une liste de faces plutôt que les faire une à une
        if face.mode == 'RGBA' :
            face.convert('RGB')
        gender_dict = {0: 'male', 1: 'female'}
        inputs = np.transpose(face.resize((64, 64)), (2, 0, 1))
        inputs = np.expand_dims(inputs, 0).astype(np.float32) / 255.
        predictions = self.age_gender_model.run(['output'], input_feed={'input': inputs})[0][0]    
        gender = gender_dict[int(np.argmax(predictions[:2]))]
        age = np.round(predictions[2])
        return (gender, age)
    
    def predict_ethnicity(self, faces: list) -> list :
        """ Predict ethnicities from a list of cropped faces """
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
        
        transformed_faces = torch.stack([inference_transform(face.convert("RGB")) for face in faces])
        outputs = self.ethnicity_detection_model(transformed_faces)
        _, predicted = torch.max(outputs.data, 1)
        ethnicities = [ethnicity_labels[prediction] for prediction in predicted.tolist()]
        return ethnicities

#class EthnicityModel(pl.LightningModule):
class EthnicityModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.resnet = models.resnet18(pretrained=False)
        num_features = self.resnet.fc.in_features

        self.resnet.fc = torch.nn.Linear(num_features, 4)

    def forward(self, x):
        return self.resnet(x)
