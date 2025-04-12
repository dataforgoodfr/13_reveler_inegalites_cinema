import cv2
import numpy as np
import os
import pickle as pkl
import psutil
import vision_classifiers
import vision_detection

from copy import deepcopy
from PIL import Image, ImageDraw, ImageFont
from utils import frame_capture


def get_frames(trailer_path: str) -> None:
    frames = frame_capture(trailer_path)
    height, width, _ = frames[0].shape
    for i in range(len(frames)):
        frame = frames[i]
        text = f'Frame {i}'
        cv2.putText(frame, text, (int(0.7*width), int(0.7*height)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    output_name = f'{trailer_path[:-4]}_with_frames.avi'
    video = cv2.VideoWriter(
        output_name, cv2.VideoWriter_fourcc(*'DIVX'), 25, (width, height))

    # Write each frame to the video file
    for frame in frames:
        video.write(frame)

    # Release the VideoWriter object
    video.release()


def get_vision_modules() -> tuple[vision_detection.VisionDetection, vision_classifiers.VisionClassifier]:
    visiondetector = vision_detection.VisionDetection()
    visionclassifier = vision_classifiers.VisionClassifier()
    return visiondetector, visionclassifier


def sample_frames(indices: list, trailer_path: str) -> tuple[list, list]:
    frames = frame_capture(trailer_path)
    subframes = frames[indices, :, :, :]
    return subframes


def get_faces(subframes: np.ndarray, vision_detector: vision_detection.VisionDetection) -> list:
    detections = vision_detector.crop_areas_of_interest(
        images=subframes, H_original=subframes.shape[1], W_original=subframes.shape[2])
    return detections


def label_results(detections: list, subframes: list, subframe_indices: list) -> dict:
    d_labeled_results = {}
    for i in range(len(detections)):
        detection = detections[i]
        frame_id = detection['frame_id']

        subframe = subframes[frame_id]
        subframe_index = subframe_indices[frame_id]
        frame_label = f'frame_{subframe_index}'
        if frame_label not in d_labeled_results:
            d_labeled_results[frame_label] = {}
        x1, y1, x2, y2 = detection['bbox']
        img_subframe = Image.fromarray(subframe)
        imgdraw = deepcopy(img_subframe)
        draw = ImageDraw.Draw(imgdraw)
        draw.rectangle((x1, y1, x2, y2), outline='red', width=4)
        face_centroid = ((x2 + x1) / 2, (y2 + y1) / 2)
        imgdraw.show()

        label = input(
            'Do you want to label this face ? Answer with Yes or No.\n')
        match label.lower():
            case 'yes':
                gender = input(
                    'Provide the perceived gender of the detected character (Male or Female).\n')
                age = input('Provide the perceived age range of the detected character (0-2, 3-9, 10-19, 20-29,\n'
                            '30-39, 40-49, 50-59, 60-69, 70+).\n')
                ethnicity = input('Provide the perceived ethnicity of the detected character (White, Black, Latino_Hispanic, East Asian,\n'
                                  'Southeast Asian, Indian, Middle Eastern).\n')
                label_idx = len(d_labeled_results[frame_label])
                d_labeled_results[frame_label][label_idx] = {'face_centroid': face_centroid,
                                                             'bbox': (x1, y1, x2, y2),
                                                             'gender': gender,
                                                             'age': age,
                                                             'ethnicity': ethnicity,
                                                             }
            case _:
                ('Moving on to next detection...')

        # Not the most elegant way to do it, but automatically closes the displayed image
        # Possibly only works on ubuntu, need to check which process automatically runs to open the image on other OS
        for proc in psutil.process_iter():
            if proc.name() == 'eog':
                proc.kill()

    return d_labeled_results


def main(trailer_directory: str) -> None:
    trailer_path = os.path.join('evaluation_trailers', trailer_directory, trailer_directory)
    print(
        f'Outputting frame-numbered trailer to {trailer_path}_with_frames.avi')
    if os.path.isfile(f'{trailer_path}_with_frames.avi'):
        print(f'{trailer_path}_with_frames.avi already exists, moving on')
    else:
        get_frames(f'{trailer_path}.mp4')
    indices = list(
        map(int, input("Enter frame indices to annotate separated by space: ").split()))
    print(f'Annotating frames {indices}...')
    vision_detector, _ = get_vision_modules()
    subframes = sample_frames(indices, f'{trailer_path}.mp4')
    detections = get_faces(subframes, vision_detector)
    d_labeled_results = label_results(detections, subframes, indices)
    with open(f'{trailer_path}_annotated.pkl', 'wb') as outfile:
        pkl.dump(d_labeled_results, outfile)
    outfile.close()


def evaluate_trailer(trailer_directory:str, evaluation_type:str = 'binary') -> float:
    trailer_path = os.path.join('evaluation_trailers', trailer_directory, trailer_directory)
    vision_detector, vision_classifier = get_vision_modules()
    with open(f'{trailer_path}_annotated.pkl', 'rb') as infile :
        annotations = pkl.load(infile)
    infile.close()
    indices = sorted([int(key.split('_')[1]) for key in annotations])
    subframes = sample_frames(indices, f'{trailer_path}.mp4')
    detections = get_faces(subframes, vision_detector)
    frame_scores = []
    for i in range(len(subframes)) :
        frame_annotations = annotations[f'frame_{indices[i]}']
        frame_detections = [det for det in detections if det['frame_id'] == i]
        annotated_centroids = [frame_annotations[k]['face_centroid'] for k in range(len(frame_annotations))]
        mask, matches = [], {}
        for j in range(len(frame_detections)) :
            x1, y1, x2, y2 = frame_detections[j]['bbox']
            det_centroid = ((x2 + x1) / 2, (y2 + y1) / 2)
            dists = [np.abs(det_centroid[0] - annotated_centroids[k][0]) + np.abs(det_centroid[1] - annotated_centroids[k][1]) 
                     for k in range(len(annotated_centroids))]
            mindist, mindist_id = min(dists), np.argmin(dists)
            if mindist < 3 :
                matches[j] = mindist_id
                mask.append(1)
            else :
                mask.append(0)
        frame_detections = [frame_detections[k]['cropped_face'] for k in range(len(frame_detections)) if mask[k] == 1]
        ages, genders, ethnicities, age_confs, gender_confs, ethnicity_confs = vision_classifier.predict_age_gender_ethnicity(frame_detections)
        for j in range(len(matches)):
            frame_annotations[matches[j]]['predicted_age'] = ages[j]
            frame_annotations[matches[j]]['predicted_age_conf'] = age_confs[j]        
            frame_annotations[matches[j]]['predicted_gender'] = genders[j]
            frame_annotations[matches[j]]['predicted_gender_conf'] = gender_confs[j]        
            frame_annotations[matches[j]]['predicted_ethnicity'] = ethnicities[j]
            frame_annotations[matches[j]]['predicted_ethnicity_conf'] = ethnicity_confs[j]        
        
        frame_scores.extend(score_evaluation(frame_annotations, evaluation_type))
    return frame_scores


def score_evaluation(frame_annotations:dict, evaluation_type:str = 'binary') -> list:
    annotation_scores = []
    keys = ['age', 'gender', 'ethnicity']
    for annotation in frame_annotations.values():
        score = 0
        for key in keys :
            if annotation[key] == annotation[f'predicted_{key}'] :
                score += 0
            else :
                match evaluation_type :
                    case 'binary' :
                        score += 1
                    case _ :
                        score += 1 - annotation[f'predicted_{key}_conf']
        annotation_scores.append(score / len(keys))
    return annotation_scores


def save_annotations(trailer_directory:str) -> None:
    trailer_path = os.path.join('evaluation_trailers', trailer_directory, trailer_directory)
    os.makedirs(os.path.join('evaluation_trailers', trailer_directory, 'annotated_frames'), exist_ok=True)
    with open(f'{trailer_path}_annotated.pkl', 'rb') as infile :
        annotations = pkl.load(infile)
    infile.close()
    frames_indices = [int(key.split('_')[1]) for key in annotations]
    frames = frame_capture(f'{trailer_path}.mp4')
    for index in frames_indices :
        frame_annotations = annotations[f'frame_{index}']
        frame = frames[index]
        img_frame = Image.fromarray(frame)
        imgdraw = deepcopy(img_frame)
        draw = ImageDraw.Draw(imgdraw)
        font = ImageFont.load_default(size = 16)

        for i in range(len(frame_annotations)) :
            x1, y1, x2, y2 = frame_annotations[i]['bbox']
            match frame_annotations[i]["gender"]:
                case "Male":
                    color = (0, 0, 255)
                case "Female":
                    color = (255, 0, 0)
            
            draw.rectangle((x1, y1, x2, y2), outline=color, width=2)
#            draw.text((box[0], box[1] - 1), txt, anchor="lb", fill=fill, font=font)
            draw.text((x1, y1 - 1), f"{frame_annotations[i]['age']}, {frame_annotations[i]['ethnicity']}", 
                      anchor='lb', fill=color, font=font)
        #imgdraw.show()
        imgdraw.save(os.path.join('evaluation_trailers', trailer_directory, 'annotated_frames', f'annotated_frame_{index}.png'))