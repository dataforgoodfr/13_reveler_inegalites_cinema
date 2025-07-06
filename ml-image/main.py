import argparse
import cv2
import os
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


def infer_on_trailer(trailer_path: str, cluster_model: str, cluster_threshold: float, agr_method: str, min_area: float, max_area: float, min_conf: float, min_conf_cla: float, min_sharpness_cla: float, max_z_cla: float, min_mouth_opening_cla : float, movie_id: str | int, mode: str, batch_size: int, device: str, num_cpu: int, store_visuals: bool) -> tuple[list[dict], np.ndarray]:
    # Extract frames from video
    frames, fps = utils.frame_capture(trailer_path)

    # Initialize constants
    H_original, W_original, effective_area, _, _= utils.compute_constants(frames, movie_id=movie_id, source_type="trailer", mode=mode)

    # Detect faces in the video
    detections = vision_detection.detect_faces(frames, H_original, W_original, area_type="face",
                              batch_size=batch_size, device=device, num_cpu_threads=num_cpu)

    # Filter detections
    filtered_detections = filter_detections.filter_detections_clustering(
        detections, effective_area, min_area, max_area, min_conf, movie_id)

    # Classify all filtered faces
    classified_faces, flattened_faces = vision_classifiers.classify_faces(
        filtered_detections, batch_size, device)

    # Filter detections for classification
    filtered_detections = filter_detections.filter_detections_classifications(
        classified_faces, effective_area, min_conf_cla, min_sharpness_cla, max_z_cla, min_mouth_opening_cla, movie_id, mode=mode)

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
        embedded_faces = [embedding for i, embedding in enumerate(embedded_faces) if i in all_indexes]

    return embedded_faces_poster, embedded_faces, filtered_detections, total_area


def assign_poster(embedded_faces_poster: list[dict], embedded_faces: list[np.ndarray], aggregated_estimations: list[dict], filtered_detections: list[dict], total_area: float) -> list:
    indexes_to_del = []
    for index, face in enumerate(embedded_faces_poster):
        closest_index = None
        closest_distance = float("inf")  # Distance initiale très grande

        #closest_index = int(np.argmin(np.linalg.norm(face - np.array(embedded_faces), axis = 1)))

        # Comparer avec chaque embedding dans embedded_faces
        for i, cluster_embedding in enumerate(embedded_faces):
        # Calculer la distance Euclidienne entre les embeddings
            distance = np.linalg.norm(face - np.array(cluster_embedding))

            # Mettre à jour si une distance plus petite est trouvée
            if distance < closest_distance:
                closest_distance = distance
                closest_index = i

        # Assigner le label correspondant à l'index le plus proche
        if closest_index is not None:
            for video_person in aggregated_estimations:
                if closest_index in video_person["persons_ids"]:
                    filtered_detections[index]["gender"] = video_person["gender"]
                    filtered_detections[index]["age"] = video_person["age"]
                    filtered_detections[index]["ethnicity"] = video_person["ethnicity"]

            occupied_area = filter_detections.compute_area(filtered_detections[index]["bbox"], total_area)
            filtered_detections[index]["occupied_area"] = occupied_area
        else:
            indexes_to_del.append(index)
    # Delete the detection from filtered_detections
    filtered_detections = [det for i, det in enumerate(filtered_detections) if i not in indexes_to_del]
    return filtered_detections


def main(
        source, movie_id, num_cpu, batch_size, min_area, max_area, min_conf, min_conf_cla, min_sharpness, min_sharpness_cla,
        max_z, max_z_cla, min_mouth_opening, min_mouth_opening_cla, cluster_model, cluster_threshold, agr_method, store_visuals, visuals_path, mode='inference', poster_source='None', row=None,
        ) -> None:

    # Load data
    data, source_type = utils.load_data_from_links(row)
    if source_type == "url":
        poster = data["image"]
    elif poster_source != "None":
        poster = cv2.imread(poster_source)

    trailer_path = data["trailer_path"]

    if trailer_path == "":
        logger.warning(f"No trailer found for {source}.")
        return

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Infer on trailer
    aggregated_estimations = infer_on_trailer(trailer_path,
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
                                              movie_id,
                                              mode,
                                              batch_size,
                                              device,
                                              num_cpu,
                                              store_visuals)

    if poster_source != "None":
        # Infer on poster
        embedded_faces_poster, embedded_faces, filtered_detections, total_area = infer_on_poster(poster,
                                                                                                 movie_id,
                                                                                                 aggregated_estimations,
                                                                                                 min_area,
                                                                                                 min_conf,
                                                                                                 mode,
                                                                                                 batch_size,
                                                                                                 device,
                                                                                                 num_cpu)
        filtered_detections = assign_poster(embedded_faces_poster, embedded_faces, aggregated_estimations, filtered_detections, total_area)
        
        # Store poster predictions in .pkl file
        with open(f'stored_predictions/{movie_id}_poster_predictions.pkl', 'wb') as outfile:
            pkl.dump(filtered_detections, outfile)
        outfile.close()

        if store_visuals :
            # Draw predictions on poster
            utils.draw_predictions_on_poster(poster, filtered_detections)

    match mode:
        case 'evaluate':
            score_tot, score_kept_frames = evaluation_annotation.evaluate_trailer_whole_pipeline(trailer_path, aggregated_estimations)
            #print(f"Score for {trailer_path}: {score_tot:.2f} if including non kept frames, {score_kept_frames:.2f} if only kept frames")
            return score_tot, score_kept_frames
        case _:
            # Store trailer predictions in .pkl file
            with open(f'stored_predictions/{movie_id}_trailer_predictions.pkl', 'wb') as outfile:
                pkl.dump(aggregated_estimations, outfile)
            outfile.close()
            
            return aggregated_estimations

        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source", type=str, help="Lien vers la fiche film allociné, chemin vers"
        " le fichier vidéo ou vers un fichier csv pour traiter une liste de"
        " films.")
    parser.add_argument(
        "--source_image", type=str, default="None", help="Lien vers la fiche film allociné, chemin vers"
        " le fichier vidéo ou vers un fichier csv pour traiter une liste de"
        " films.")
    parser.add_argument("--mode", type=str, default="infer", help="Mode to use the main, will infer if not 'evaluate'")
    parser.add_argument("--column_identifier", type=str, default="visa_number",
                        help="Column to use to get the identifier to save prediction outputs")
    parser.add_argument("--num_cpu", type=int, default=8,
                        help="Number of CPU threads to use")
    parser.add_argument("--batch_size", type=int, default=64,
                        help="Batch size for inference")
    parser.add_argument("--min_area", type=float, default=0.07622856572436439,
                        help="Minimum area for detection filter")
    parser.add_argument("--max_area", type=float, default=1.0,
                        help="Maximum area for detection filter")
    parser.add_argument("--min_conf", type=float, default=0.0,
                        help="Minimum confidence for detection filter")
    parser.add_argument("--min_conf_cla", type=float, default=0.8059752338758108,
                        help="Minimum confidence for classification filter")
    parser.add_argument("--min_sharpness", type=float, default=0.0,
                        help="Minimum sharpness for sharpness filter")
    parser.add_argument("--min_sharpness_cla", type=float, default=144.39764905212095,
                        help="Minimum sharpness for sharpness filter")
    parser.add_argument("--max_z", type=float, default=0.5,
                        help="Maximum nose z value for pose filter")
    parser.add_argument("--max_z_cla", type=float, default=-0.18154759434262552,
                        help="Maximum nose z value for pose filter")
    parser.add_argument("--min_mouth_opening", type=float, default=0.00,
                        help="Minimum upper/lower lips distance for obstruction filter")
    parser.add_argument("--min_mouth_opening_cla", type=float, default=0.00,
                        help="Minimum upper/lower lips distance for obstruction filter")
    parser.add_argument("--cluster_model", type=str,
                        default="chinese_whispers", help="Model for clustering faces")
    parser.add_argument("--cluster_threshold", type=float,
                        default=0.92, help="Threshold for clustering faces")
    parser.add_argument("--agr_method", type=str, default="majority",
                        help="Method for aggregating predictions")
    parser.add_argument("--store_visuals", action=argparse.BooleanOptionalAction,
                        default=False, help="Store trailer and poster with visual predictions")
    parser.add_argument("--visuals_path", type=str, default="stored_visuals/",
                        help="Path to store trailers and posters with visual predictions")
    parser.add_argument("--istart", type=int, default=0,
                        help="Row index from which to start dataframe analysis")
    parser.add_argument("--istop", type=int, default=1e9,
                        help="Row index on which to stop dataframe analysis")

    args = parser.parse_args()
    
    os.makedirs("stored_visuals", exist_ok=True)
    os.makedirs("stored_predictions", exist_ok=True)
        
    if args.source[-4:] == ".csv":
        df = pd.read_csv(args.source)
        istart = args.istart
        istop = min(len(df), args.istop)
        df = df.iloc[istart:istop]
        logger.info(f"Found {len(df)} films to analyze in the source csv.")
        for i, row in tqdm(df.iterrows(), total=len(df)):
            try : 
                predictions = main(
                    row.allocine_url, row[args.column_identifier], args.num_cpu, args.batch_size, args.min_area, args.max_area, args.min_conf, args.min_conf_cla, args.min_sharpness, args.min_sharpness_cla, args.max_z, args.max_z_cla, args.min_mouth_opening, args.min_mouth_opening_cla, args.cluster_model, args.cluster_threshold, args.agr_method, args.store_visuals, args.visuals_path, row=row,
                )
                os.remove(f"downloaded_media/{row.visa_number}.jpg")
                os.remove(f"downloaded_media/{row.visa_number}.mp4")
            except Exception as e:
                logger.info(f"Row {i}, id {row[args.column_identifier]} : {repr(e)}")
                continue
        logger.success(f"All films from {args.source} have been analyzed.")
        df = pd.read_csv(args.source)
        utils.gather_and_save_predictions(df)
    else:
        raise ValueError("Source must be a .csv file")
