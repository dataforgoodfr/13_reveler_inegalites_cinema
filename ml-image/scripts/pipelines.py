import cv2
import os
import sys
import pandas as pd
import pickle as pkl
import numpy as np
import torch

from loguru import logger
from tqdm import tqdm

from scripts import faces_clustering
from scripts import filter_detections
from scripts import utils
from scripts import vision_classifiers
from scripts import vision_detection
from scripts import evaluation_annotation 

logger.remove(0)
logger.add(sys.stderr, level="INFO")

def infer_on_trailer(trailer_path: str, cluster_model: str, cluster_threshold: float, agr_method: str, min_area: float, max_area: float, min_conf: float, min_conf_cla: float, min_sharpness_cla: float, max_z_cla: float, min_mouth_opening_cla : float, batch_size: int, device: str, num_cpu: int, store_visuals: bool, movie_id: str | int=None, mode: str='infer') -> tuple[list[dict], np.ndarray]:
    """
    Description of the function
    """
    # Extract frames from video
    frames, fps = utils.frame_capture(trailer_path)

    # Initialize constants
    H_original, W_original, effective_area, _, _= utils.compute_constants(frames, movie_id=movie_id, source_type="trailer", mode=mode)

    # Detect faces in the video
    detections = vision_detection.detect_faces(frames, H_original, W_original, area_type="face",
                              batch_size=batch_size, device=device, num_cpu_threads=num_cpu)

    # Filter detections for classification
    filtered_detections = filter_detections.filter_detections_clustering(
        detections, effective_area, min_area, max_area, min_conf)

    # Classify all filtered faces
    classified_faces, flattened_faces = vision_classifiers.classify_faces(
        filtered_detections, batch_size, device)

    # Filter detections for clustering
    filtered_detections = filter_detections.filter_detections_classifications(
        classified_faces, effective_area, min_conf_cla, min_sharpness_cla, max_z_cla, min_mouth_opening_cla, movie_id=movie_id, mode=mode)

    # Cluster faces and aggregate predictions for each character
    embedded_faces = faces_clustering.embed_faces(flattened_faces, batch_size, device)
    aggregated_estimations = faces_clustering.cluster_faces(
        embedded_faces, model=cluster_model, threshold=cluster_threshold, classified_faces=filtered_detections,
        method=agr_method, fps=fps, effective_area=effective_area)

    # Store predictions on video
    if store_visuals :
        utils.store_predictions_on_video(
            frames, aggregated_estimations, classified_faces, fps=fps, output_name=movie_id)

    return aggregated_estimations, embedded_faces


def infer_on_poster(poster: np.ndarray, embedded_faces: np.ndarray, aggregated_estimations: list[dict], min_area: float, min_conf: float, movie_id: str | int, mode: str, batch_size: int, device: str, num_cpu: int) -> tuple[list[dict], list[np.ndarray], list[dict], float]:
    """
    Description of the function
    """
    # Initialize constants
    H_original, W_original, total_area, _, _ = utils.compute_constants(poster, movie_id, mode=mode, source_type="poster")

    # Detect faces in the poster
    detections = vision_detection.detect_faces(poster, H_original, W_original, area_type="face",
                              batch_size=1, device=device, num_cpu_threads=num_cpu)

    # Filter detections
    filtered_detections = filter_detections.filter_detections_poster(detections, total_area, min_area, min_conf)

    flattened_faces_poster = [face["cropped_face"] for face in filtered_detections]
    embedded_faces_poster = faces_clustering.embed_faces(flattened_faces_poster, batch_size, device)
    all_indexes = set()  # Use a set to avoid duplicates
    for video_person in aggregated_estimations:
        all_indexes.update(video_person["persons_ids"])  # Add all indexes from persons_ids

    # Step 2: Filter embedded_faces to keep only the embeddings corresponding to the collected indexes
    embedded_faces = [(i, embedding) for i, embedding in enumerate(embedded_faces) if i in all_indexes]

    return embedded_faces_poster, embedded_faces, filtered_detections, total_area


def assign_poster(embedded_faces_poster: list[dict], embedded_faces: list[np.ndarray], aggregated_estimations: list[dict], filtered_detections: list[dict], total_area: float, poster: np.ndarray, store_visuals: bool) -> list:
    """
    Description of the function
    """
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

def predict_one_item(
        column_identifier, num_cpu, batch_size, min_area, max_area, min_conf, min_conf_cla, min_sharpness_cla, max_z_cla,
        min_mouth_opening_cla, cluster_model, cluster_threshold, agr_method, store_visuals, downloaded_media_path,
        poster_path, trailer_path, mode='inference', poster_source='None', row=None
        ) -> None:
    """
    Predict all handled metrics over a selected movie (trailer + poster)
    """ 
    movie_id = row[column_identifier]

    # Load data
    data, source_type = utils.load_data_from_links(row, downloaded_media_path, poster_path, trailer_path)
    if source_type == "url":
        poster = data["image"]
        poster_source = "url"
    elif poster_source != "None":
        poster = cv2.imread(poster_source) #TODO: use this part when handler will cover sources other than csv 

    trailer_path = data["trailer_path"]

    if trailer_path == "":
        logger.error(f"No trailer found for movie id: {movie_id}. Skipping this row")
        raise

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Infer on trailer
    aggregated_estimations, embedded_faces = infer_on_trailer(trailer_path,
                                              cluster_model,
                                              cluster_threshold,
                                              agr_method,
                                              min_area,
                                              max_area,
                                              min_conf,
                                              min_conf_cla,
                                              min_sharpness_cla,
                                              max_z_cla,
                                              min_mouth_opening_cla,
                                              batch_size,
                                              device,
                                              num_cpu,
                                              store_visuals,
                                              movie_id=movie_id,
                                              mode=mode)
    
    # Infer on poster
    if poster_source != "None":
        embedded_faces_poster, embedded_faces, filtered_detections, total_area = infer_on_poster(poster,
                                                                                                 embedded_faces,
                                                                                                 aggregated_estimations,
                                                                                                 min_area,
                                                                                                 min_conf,
                                                                                                 movie_id,
                                                                                                 mode,
                                                                                                 batch_size,
                                                                                                 device,
                                                                                                 num_cpu)
        filtered_detections = assign_poster(embedded_faces_poster,
                                            embedded_faces,
                                            aggregated_estimations,
                                            filtered_detections,
                                            total_area,
                                            poster,
                                            store_visuals)
    else :
        filtered_detections = []
            
    return aggregated_estimations, filtered_detections

def evaluate_pipeline(args, to_predict_df):
    score_tot, score_kept_frames = "WIP", "WIP" #evaluation_annotation.evaluate_trailer_whole_pipeline(trailer_path, aggregated_estimations)
            #print(f"Score for {trailer_path}: {score_tot:.2f} if including non kept frames, {score_kept_frames:.2f} if only kept frames")
    return score_tot, score_kept_frames
    
def infer_pipeline(args, to_predict_df, paths):
    try:
        # take selected subset of items to infer on        
        istart = args.istart
        istop = min(len(to_predict_df), args.istop)
        to_predict_df = to_predict_df.iloc[istart:istop]
        logger.info(f"Found {len(to_predict_df)} films to analyze in the source csv.")
        
        # Infer per item
        for i, row in tqdm(to_predict_df.iterrows(), total=len(to_predict_df)):
            try : 
                poster_path, trailer_path = f"{paths['dl_media']}/{row.visa_number}.jpg", f"{paths['dl_media']}/{row.visa_number}.mp4"
                aggregated_estimations, filtered_detections = predict_one_item(
                    args.column_identifier, args.num_cpu, args.batch_size, args.min_area, args.max_area, args.min_conf, 
                    args.min_conf_cla, args.min_sharpness_cla, args.max_z_cla, args.min_mouth_opening_cla, args.cluster_model,
                    args.cluster_threshold, args.agr_method, args.store_visuals, paths['dl_media'], poster_path, trailer_path, row=row
                )

                # Store poster predictions in .pkl file
                with open(f"{paths['temp_preds']}/{row[args.column_identifier]}_poster_predictions.pkl", 'wb') as outfile:
                    pkl.dump(filtered_detections, outfile)
                outfile.close()

                # Store trailer predictions in .pkl file
                with open(f"{paths['temp_preds']}/{row[args.column_identifier]}_trailer_predictions.pkl", 'wb') as outfile:
                    pkl.dump(aggregated_estimations, outfile)
                outfile.close()
            
                os.remove(poster_path)
                os.remove(trailer_path)

            except Exception as e:
                logger.info(f"Row {i}, id {row[args.column_identifier]} : {repr(e)}")
                continue
        logger.success(f"All films from {args.source} have been analyzed.")

        # Aggregate predictions
        utils.gather_and_save_predictions(to_predict_df, paths['temp_preds'], paths['final_preds'])
        
    except Exception as e:
        raise ValueError(f'Could not infer on given csv: {e}')
        
def handler(args, paths):
    if args.source[-4:] == ".csv":
        to_predict_df = pd.read_csv(args.source)
        if args.mode == 'infer':
            infer_pipeline(args, to_predict_df, paths)
        elif args.mode == 'evaluate':
            evaluate_pipeline(args, to_predict_df)
        else:
            raise ValueError(f'{args.mode} mode is not supported')
    else: 
        raise ValueError("Source must be a .csv file")