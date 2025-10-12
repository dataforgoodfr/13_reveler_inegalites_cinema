import cv2
import json
import numpy as np
import os
import pandas as pd
import pickle as pkl
import requests

from bs4 import BeautifulSoup
from PIL import Image
from torch.utils.data import Dataset
from loguru import logger

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
                      output_trailer: str = 'downloaded_trailer') -> None:
        """
        Download poster and trailer from a given Allocine URL (only works for allocine)
        """
       
        os.makedirs("example", exist_ok=True)  # Ensure the "example" folder exists

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # to download trailer
        figure_tag = soup.find('figure', class_='player')
        if not figure_tag:
            video_path = ""
            quality = ""
        else:
            video_path = os.path.join('example', f'{output_trailer}.mp4')
            data_model = figure_tag['data-model']
            data_model = json.loads(data_model)
            video_sources = data_model['videos'][0]['sources']
            if "high" in video_sources:
                link = video_sources["high"]
                quality = "high"
            elif "medium" in video_sources:
                link = video_sources["medium"]
                quality = "medium"
            else:
                link = video_sources["low"]
                quality = "low"
            #print(f"Downloading trailer in {quality} quality")
            download_video_from_link(link, video_path)
            
        # to download poster
        poster_path = os.path.join('example', f'{output_poster}.jpg')
        poster_tag = soup.find('meta', property='og:image')
        poster_url = poster_tag['content']
        download_poster_from_link(poster_url, poster_path)
        
        poster_image = cv2.imread(poster_path)
        
        data = {"url": url, "poster_path": poster_path, "trailer_path": video_path, "image": poster_image, "quality": quality}

        return data

    
def download_video_from_link(link: str, video_path: str) -> None: 
    r = requests.get(link, stream=True)
    with open(video_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024*1024) :
            if chunk:
                f.write(chunk)

                
def download_poster_from_link(link: str, poster_path: str) -> None: 
    r = requests.get(link, stream=True)
    with open(poster_path, 'wb') as f:
        for chunk in r:
            f.write(chunk)

                
def get_data_from_file(file_path: str, filetype: str = "poster") -> None:
    """
    Load data from local file for either a 'poster' or 'trailer' file
    """
    data = {"url": "unknow", "poster_path": "unknow",
             "trailer_path": "unknow", "image": "unknow"}

    if filetype == "poster":
        data["image"] = Image.open(file_path)
        data["poster_path"] = file_path
    
    elif filetype == "trailer":
        data["trailer_path"] = file_path

    else:
        raise ValueError("filetype needs to be one of ['poster', 'trailer']")
    
    return data

def frame_capture(path: str) -> np.ndarray:
    """
    Extract frames from a video file
    """
    vidObj = cv2.VideoCapture(path)
    frames = []

    # Get the FPS of the video
    fps = vidObj.get(cv2.CAP_PROP_FPS)
    success = 1 # checks whether frames were extracted 
    
    while success:
        # vidObj object calls read
        success, image = vidObj.read() # function extract frames 
        if not success:
            break
        frames.append(image)
        
    return np.array(frames), fps

def draw_predictions_on_video(frames: np.ndarray, video_persons: list, frame_persons: list) -> np.ndarray:
    """
    Draw predictions on video frames (bounding boxes with gender, age, ethnicity...)
    """
    frame_index = 0
    for frame in frames:
        for person in video_persons:
            if frame_index in person["frames_bboxes"]:
                # Ensure bbox coordinates are integers
                bbox = [int(coord) for coord in person["frames_bboxes"][frame_index]]
                match person["gender"]:
                    case "Male":
                        color = (0, 0, 255)
                    case "Female":
                        color = (255, 0, 0)
                    case _:
                        color = (0, 255, 0)
                cv2.rectangle(
                    frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
                cv2.putText(frame, f"{person['label']}, {person['age']}, {person['ethnicity']}", (
                    bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        frame_index += 1
    
    return frames

def draw_predictions_on_poster(poster: np.ndarray, predictions: list, output_name: str = 'predictions_poster.jpg') -> None :
    """
    Draw predictions on poster (bounding boxes with gender, age, ethnicity...)
    """
    for person in predictions:
        bbox = [int(coord) for coord in person["bbox"]]  # Ensure bbox coordinates are integers
        match person["gender"]:
            case "Male":
                color = (0, 0, 255)
            case "Female":
                color = (255, 0, 0)
            case _:
                color = (0, 255, 0)
        cv2.rectangle(
            poster, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
        cv2.putText(poster, f"{person['age']}, {person['ethnicity']}", (
            bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    output_path = os.path.join('example', output_name)
    cv2.imwrite(output_path, poster)

def store_predictions_on_video(frames: np.ndarray, video_persons: list, frame_persons: list, fps: int = 25, output_name: str = 'predictions_trailer') -> None:
    """
    Draw predictions on video frames and store the result in a new video file
    """
    modified_frames = draw_predictions_on_video(
        frames, video_persons, frame_persons)

    # Define the codec and create VideoWriter object
    height, width, _ = modified_frames[0].shape
    output_name = f"{output_name}.avi"
    output_path = os.path.join('example', output_name)
    video = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(
        *'DIVX'), fps, (width, height))

    # Write each frame to the video file
    for frame in modified_frames:
        video.write(frame)

    # Release the VideoWriter object
    video.release()         

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


def gather_and_save_predictions(source:pd.DataFrame, path_to_outputs: str, final_predictions_path: str) -> None :
    """
    Function to aggregate trailer and poster predictions in one large .csv file for later database insertion.
    """
    poster_predictions = [os.path.join(path_to_outputs, item) for item in os.listdir(path_to_outputs) if 'poster' in item]
    trailer_predictions = [os.path.join(path_to_outputs, item) for item in os.listdir(path_to_outputs) if 'trailer' in item]
    logger.info(f'Gathering {len(poster_predictions)} poster predictions and {len(trailer_predictions)} trailer predictions')
    dict_poster_predictions = {
        'visa_number' : [], 
        'allocine_id' : [],
        'gender' : [], 
        'age_min' : [], 
        'age_max' : [], 
        'ethnicity' : [], 
        'poster_percentage' : []
        }
    dict_trailer_predictions = {
        'visa_number' : [], 
        'allocine_id' : [],
        'gender' : [], 
        'age_min' : [], 
        'age_max' : [], 
        'ethnicity' : [], 
        'time_on_screen' : [], 
        'average_size_on_screen' : []
        }
    for prediction in poster_predictions :
        with open(prediction, 'rb') as infile :
            data = pkl.load(infile)
        infile.close()
        logger.debug(f'la tête du path des prédictions: {prediction}')
        visa_number = int(prediction.split('\\')[-1].split('_')[0]) #To make more robust to the OS used -> using the Path library
        logger.debug(f'Le numéro de visa récupéré dans le path: {visa_number}')
        allocine_id = int(source[source.visa_number == visa_number].iloc[0]['allocine_id'])
        for char in data :
            dict_poster_predictions = format_prediction_results('poster', char, allocine_id, visa_number, dict_poster_predictions)
    df_posters = pd.DataFrame(dict_poster_predictions)
    df_posters.to_csv(f'{final_predictions_path}/predictions_on_posters.csv', index=False)

    for prediction in trailer_predictions :
        with open(prediction, 'rb') as infile :
            logger.debug(f'Gathering predictions from {prediction}')
            data = pkl.load(infile)
        infile.close()
        visa_number = int(prediction.split('\\')[-1].split('_')[0])
        allocine_id = int(source[source.visa_number == visa_number].iloc[0]['allocine_id'])
        for char in data :
            dict_trailer_predictions = format_prediction_results('trailer', char, allocine_id, visa_number, dict_trailer_predictions)
    df_trailers = pd.DataFrame(dict_trailer_predictions)
    df_trailers.to_csv(f'{final_predictions_path}/predictions_on_trailers.csv', index=False)


def format_prediction_results(
        mode: str, character_data: dict, allocine_id: str, visa_number: int, dict_predictions: dict
        ) -> dict:
    if character_data['age'] == 'unknown':
        dict_predictions['age_min'].append(0)
        dict_predictions['age_max'].append(0)
    else :
        dict_predictions['age_min'].append(character_data['age'].split('-')[0])
        dict_predictions['age_max'].append(character_data['age'].split('-')[1])
        
    dict_predictions['visa_number'].append(visa_number)
    dict_predictions['allocine_id'].append(allocine_id)
    dict_predictions['gender'].append(character_data['gender'])
    dict_predictions['ethnicity'].append(character_data['ethnicity'])
    match mode :
        case 'poster' :
            dict_predictions['poster_percentage'].append(character_data['occupied_area'])
        case 'trailer' :
            dict_predictions['time_on_screen'].append(character_data['occurence'])
            dict_predictions['average_size_on_screen'].append(character_data['area occupied'])
    return dict_predictions


def load_data(source: str, output_poster: str = "downloaded_poster", output_trailer: str = "downloaded_trailer"):
    # Get data from url or file

    if source[:4] == "http":
        #print(f"Looking for data at: {source}")
        data = get_data_from_url(source, output_poster, output_trailer)
        source_type = "url"
    else:
        #print(f"Looking for data in file: {source}")
        data = get_data_from_file(source, filetype="trailer")
        source_type = "path"
    return data, source_type


def load_data_from_links(row, downloaded_media_path) :
    # Get data directly from poster and trailer links
    output_poster, output_trailer = f"{downloaded_media_path}/{row.visa_number}.jpg", f"{downloaded_media_path}/{row.visa_number}.mp4"
    if f"{row.visa_number}.mp4" not in os.listdir(downloaded_media_path):
        download_video_from_link(row.trailer_url, output_trailer)
    if f"{row.visa_number}.jpg" not in os.listdir(downloaded_media_path):
        download_poster_from_link(row.poster_url, output_poster)
    
    poster_image = cv2.imread(output_poster)
    quality = "unknown"
    source_type = "url"
    
    data = {"url": row.allocine_url, "poster_path": output_poster, "trailer_path": output_trailer, "image": poster_image, "quality": quality}
    
    return data, source_type


def compute_constants(frames, movie_id: str, source_type: str = "trailer", sharpness_factor: float = 1.0, sharpness_factor_cla: float = 1.0, aspect_ratio: float = 2.478, mode: str = "evaluate") -> tuple:
    # Compute constants for whole pipeline

    match source_type:
        case "trailer":
            '''
            overall_sharpness = 0
            for frame in frames:
                overall_sharpness += filter_det.compute_sharpness(frame)/len(frames)

            min_sharpness = overall_sharpness / sharpness_factor
            min_sharpness_cla = overall_sharpness / sharpness_factor_cla
            '''
            min_sharpness, min_sharpness_cla = 0, 0

            H_original, W_original = frames[0].shape[:2] 
            effective_height = W_original / aspect_ratio # The aspect ratio of the video is the effective area of the video (i.e., the area where the content is present)
            total_area = effective_height * W_original

            if mode == "evaluate":
                movie_folder = os.path.join("visualize_parameters", movie_id)
                constants_path = os.path.join(movie_folder, "constants.txt")
                os.makedirs("visualize_parameters", exist_ok=True)
                os.makedirs(movie_folder, exist_ok=True)

                with open(constants_path, mode='w') as constants_file:
                    #constants_file.write(f"overall sharpness : {overall_sharpness}\n")
                    constants_file.write(f"minimal sharpness : {min_sharpness}")
                    constants_file.write(f"total area : {total_area}")
                    constants_file.close()
        
        case "poster":
            H_original, W_original = frames.shape[:2]
            total_area = H_original * W_original

            min_sharpness, min_sharpness_cla = 0, 0
        
        case _:
            raise ValueError(f"Invalid source_type: {source_type}. Choose either 'trailer' or 'poster'.")

    return H_original, W_original, total_area, min_sharpness, min_sharpness_cla
