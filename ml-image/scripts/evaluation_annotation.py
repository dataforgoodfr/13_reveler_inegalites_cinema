from PIL import Image, ImageDraw
import cv2
import vision_detection
import numpy as np
from utils import frame_capture
from copy import deepcopy 
import psutil
import pickle as pkl
import os

def get_frames(trailer_path:str) -> None:
    frames = frame_capture(trailer_path)
    height, width, _= frames[0].shape
    for i in range(len(frames)) :
        frame = frames[i]
        text = f'Frame {i}'
        cv2.putText(frame, text, (int(0.8*width), int(0.8*height)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    output_name = f'{trailer_path[:-4]}_with_frames.avi'
    video = cv2.VideoWriter(output_name, cv2.VideoWriter_fourcc(*'DIVX'), 25, (width, height))

    # Write each frame to the video file
    for frame in frames:
        video.write(frame)

    # Release the VideoWriter object
    video.release()

def get_vision_module() -> vision_detection.VisionDetection:
    visiondetector = vision_detection.VisionDetection()
    return visiondetector

def sample_frames(indices: list, trailer_path:str) -> tuple[list, list]:
    frames = frame_capture(trailer_path)
    subframes = frames[indices, :, :, :]
    return subframes

def get_faces(subframes: np.ndarray, visiondetector: vision_detection.VisionDetection) -> list:
    detections = visiondetector.crop_areas_of_interest(images=subframes, H_original=subframes.shape[1], W_original=subframes.shape[2])
    return detections

def label_results(detections: list, subframes: list, subframe_indices: list) -> dict:
    d_labeled_results = {}
    for i in range(len(detections)):
        detection = detections[i]
        frame_id = detection['frame_id']

        subframe = subframes[frame_id]
        subframe_index = subframe_indices[frame_id]
        frame_label = f'frame_{subframe_index}'
        if frame_label not in d_labeled_results :
            d_labeled_results[frame_label] = {}
        x1, y1, x2, y2 = detection['bbox']
        img_subframe = Image.fromarray(subframe)
        imgdraw = deepcopy(img_subframe)
        draw = ImageDraw.Draw(imgdraw)
        draw.rectangle((x1, y1, x2, y2), outline='red', width=4)
        face_centroid = ((x2 + x1) / 2, (y2 + y1) / 2)
        imgdraw.show()
        
        #print(f'{ages[i]} ({np.round(age_confs[i], 2)}), {genders[i]} ({np.round(gender_confs[i], 2)}), {ethnicities[i]} ({np.round(ethn_confs[i], 2)})')
        label = input('Do you want to label this face ? Answer with Yes or No.\n')
        match label.lower() :
            case 'yes' :
                gender = input('Provide the perceived gender of the detected character (Male or Female).\n')
                age = input('Provide the perceived age range of the detected character (0-2, 3-9, 10-19, 20-29,\n'
                '30-39, 40-49, 50-59, 60-69, 70+).\n')
                ethnicity = input('Provide the perceived ethnicity of the detected character (White, Black, Latino_Hispanic, East Asian,\n'
                'Southeast Asian, Indian, Middle Eastern).\n')
                label_idx = len(d_labeled_results[frame_label])
                d_labeled_results[frame_label][label_idx] = {'face_centroid' : face_centroid,
                                                                    'bbox' : (x1, y1, x2, y2),
                                                                    'gender' : gender,
                                                                    'age' : age,
                                                                    'ethnicity' : ethnicity,
                                                                    }
            case _ :
                ('Moving on to next detection...')

        # Not the most elegant way to do it, but automatically closes the displayed image
        # Possibly only works on ubuntu, need to check which process automatically runs to open the image on other OS
        for proc in psutil.process_iter() :
            if proc.name() == 'eog' :
                proc.kill()

    return d_labeled_results

def main(trailer_path:str) :
    print(f'Outputting numbered trailer video to {trailer_path[:-4]}_with_frames.avi')
    if os.path.isfile(f'{trailer_path[:-4]}_with_frames.avi') :
        print(f'{trailer_path[:-4]}_with_frames.avi already exists, moving on')
    else :
        get_frames(trailer_path)
    indices = list(map(int, input("Enter frame indices to annotate separated by space: ").split()))
    print(f'Annotating frames {indices}...')
    visiondetector = get_vision_module()
    subframes = sample_frames(indices, trailer_path)
    detections = get_faces(subframes, visiondetector)
    d_labeled_results = label_results(detections, subframes, indices)
    with open(f'annotated_{trailer_path[:-4]}.pkl', 'wb') as outfile :
        pkl.dump(d_labeled_results, outfile)
    outfile.close()