import requests
import os
import json
import cv2
import numpy as np

from bs4 import BeautifulSoup
from PIL import Image
from torch.utils.data import Dataset

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

def get_data_from_url(url: str, 
                          output_poster: str = 'downloaded_poster', 
                          output_trailer: str = 'downloaded_trailer') -> None: ### Review: Should be a separate object/function 
        """
        Download poster and trailer from a given Allocine URL (only works for allocine)
        """
       
        os.makedirs("example", exist_ok=True)  # Ensure the "example" folder exists

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # to download trailer
        figure_tag = soup.find('figure', class_='player')
        if not figure_tag :
            video_path = ""
        else :
            video_path = os.path.join('example', f'{output_trailer}.mp4')
            data_model = figure_tag['data-model']
            data_model = json.loads(data_model)
            video_sources = data_model['videos'][0]['sources']
            if "medium" in video_sources :
                link = video_sources["medium"]
                quality = "medium"
            elif "high" in video_sources :
                link = video_sources["high"]
                quality = "high"
            else :
                link = video_sources["low"]
                quality = "low"
            print(f"Downloading trailer in {quality} quality")
            r = requests.get(link, stream = True)
            with open(video_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size = 1024*1024) :
                    if chunk:
                        f.write(chunk)

        # to download poster
        poster_path = os.path.join('example', f'{output_poster}.jpg')
        poster_tag = soup.find('meta', property = 'og:image')
        poster_url = poster_tag['content']
        r = requests.get(poster_url, stream = True)
        with open(poster_path, 'wb') as f :
            for chunk in r :
                f.write(chunk)
        
        data = {"url": url, "poster_path": poster_path, "trailer_path": video_path, "image": Image.open(poster_path), "quality": quality}

        return data
        
def get_data_from_file(file_path:str, filetype:str = "poster") -> None:
    """
    Load data from local file for either a 'poster' or 'trailer' file
    """
    data = {"url": "unknow", "poster_path": "unknow", "trailer_path": "unknow", "image": "unknow"}

    if filetype == "poster" :
        data["image"] = Image.open(file_path)
        data["poster_path"] = file_path
    
    elif filetype == "trailer" :
        data["trailer_path"] = file_path

    else :
        raise ValueError("filetype needs to be one of ['poster', 'trailer']")
    
    return data

def frame_capture(path: str) -> np.ndarray: 
    """
    Extract frames from a video file
    """
    vidObj = cv2.VideoCapture(path) 
    frames = []

    success = 1 # checks whether frames were extracted 
    
    while success: 
        # vidObj object calls read 
        success, image = vidObj.read() # function extract frames 
        if not success:
            break
        frames.append(image)
        
    return np.array(frames)

def draw_predictions_on_video(frames: np.ndarray, video_persons: list, frame_persons: list) -> np.ndarray:
    """
    Draw predictions on video frames (bounding boxes with gender, age, ethnicity...)
    """
    frame_index = 0
    for frame in frames:
        for person in frame_persons:
            if person["frame_id"] == frame_index:
                bbox = [int(coord) for coord in person["bbox"]]  # Ensure bbox coordinates are integers
                for video_person in video_persons:
                    if person["person_id"]  in video_person["persons_id"]:
                        match video_person["gender"]:
                            case "Male":
                                color = (0, 0, 255)
                            case "Female":
                                color = (255, 0, 0)
                            case _:
                                color = (0, 255, 0)
                        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
                        cv2.putText(frame, f"{video_person['label']}, {video_person['age']}, {video_person['ethnicity']}", (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        frame_index += 1
    
    return frames

def find_video_effective_area(frames: np.ndarray) -> tuple:
    """
    Find the effective area of the video frames (i.e., the area where the content is present)
    """
    h, w, _ = frames[0].shape
    mask = np.zeros((h, w), dtype=np.uint8)

    for frame in frames:
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray_frame, 1, 255, cv2.THRESH_BINARY)
        mask = cv2.bitwise_or(mask, thresh)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
        return (x, y), (w, h)
    
    return (0, 0), (w, h)  # Default to full size if no contours found

def store_predictions_on_video(frames: np.ndarray, video_persons: list, frame_persons: list, fps: int = 25, output_name: str = 'predictions_trailer.avi') -> None:
    """
    Draw predictions on video frames and store the result in a new video file
    """
    modified_frames = draw_predictions_on_video(frames, video_persons, frame_persons)

    # Define the codec and create VideoWriter object
    height, width, _= modified_frames[0].shape
    output_path = os.path.join('example', output_name)
    video = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'DIVX'), fps, (width, height))

    # Write each frame to the video file
    for frame in modified_frames:
        video.write(frame)

    # Release the VideoWriter object
    video.release()         