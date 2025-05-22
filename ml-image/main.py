import argparse
import cv2
import os
import pandas as pd
import pickle as pkl
import torch

from datetime import datetime
from loguru import logger
from tqdm import tqdm

from scripts import faces_clustering as faces_clus
from scripts import filter_detections as filter_det
from scripts import utils
from scripts import vision_classifiers
from scripts import vision_detection


def load_data(source):
    # Get data from url or file

    if source[:4] == "http":
        print(f"Looking for data at: {source}")
        data = utils.get_data_from_url(source)
        source_type = "url"
    else:
        print(f"Looking for data in file: {source}")
        data = utils.get_data_from_file(source, filetype="trailer")
        source_type = "path"
    return data, source_type


def compute_constants(frames, mode: str = "trailer", sharpness_factor: float = 42.0, sharpness_factor_cla: float = 7.3, aspect_ratio: float = 2.478) -> tuple:
    # Compute constants for whole pipeline

    match mode:
        case "trailer":
            overall_sharpness = 0
            for frame in frames:
                overall_sharpness += filter_det.compute_sharpness(frame)/len(frames)
            min_sharpness = overall_sharpness / sharpness_factor 
            min_sharpness_cla = overall_sharpness / sharpness_factor_cla

            H_original, W_original = frames[0].shape[:2] 
            effective_height = W_original / aspect_ratio # The aspect ratio of the video is the effective area of the video (i.e., the area where the content is present)
            total_area = effective_height * W_original
        
        case "poster":
            H_original, W_original = frames.shape[:2]
            total_area = H_original * W_original

            min_sharpness, min_sharpness_cla = 0, 0
        
        case _:
            raise ValueError(f"Invalid mode: {mode}. Choose either 'trailer' or 'poster'.")

    return H_original, W_original, total_area, min_sharpness, min_sharpness_cla


def detect_faces(
        frames, H_original, W_original, area_type, batch_size, device, num_cpu_threads):
    # Detect faces in the video

    vision_detector = vision_detection.VisionDetection(
        device=device, num_cpu_threads=num_cpu_threads)
    detections = vision_detector.crop_areas_of_interest(
        frames, H_original, W_original, area_type=area_type, batch_size=batch_size)

    return detections


def filter_detections_poster(detections, total_area, min_area, min_conf):
    # Filter detections for poster

    filters = filter_det.DetectionFilter(
        simple_filters=[filter_det.validates_confidence_filter],
        complex_filters=[],
        area_type='face',
        total_area=total_area,
        min_area=min_area,
        min_conf=min_conf
    )    
    filtered_detections = filters.apply(detections)

    return filtered_detections


def filter_detections_clustering(detections, effective_area, min_area, max_area, min_conf, min_sharpness, max_z, min_mouth_opening):
    # Filter detections

    filters = filter_det.DetectionFilter(
        simple_filters=[filter_det.validates_area_filter,
                        filter_det.validates_confidence_filter],
        complex_filters=[filter_det.validates_sharpness_filter,
                         filter_det.validates_pose_filter],
        area_type='face',
        total_area=effective_area,
        min_area=min_area,
        max_area=max_area,
        min_conf=min_conf,
        min_sharpness=min_sharpness,
        max_z=max_z,
        min_mouth_opening=min_mouth_opening
    )
    filtered_detections = filters.apply(detections)

    return filtered_detections


def filter_detections_classifications(detections, min_conf, min_sharpness, max_z, min_mouth_opening):
    # Filter detections

    filters = filter_det.DetectionFilter(
        simple_filters=[filter_det.validates_confidence_filter],
        complex_filters=[filter_det.validates_sharpness_filter, filter_det.validates_pose_filter],
        area_type='face',
        min_conf=min_conf,
        min_sharpness=min_sharpness,
        max_z=max_z,
        min_mouth_opening=min_mouth_opening
    )    
    filtered_detections = filters.apply(detections, mode = "classification")

    return filtered_detections


def classify_faces(
        filtered_detections, batch_size: int, device: str, mode: str = "trailer", gender_conf_threshold: float = 1.2, age_conf_threshold: float = 1.05, ethnicity_conf_threshold: float = 1.1
        ) -> tuple[dict, list]:
    # Classify all filtered faces

    classifier = vision_classifiers.VisionClassifier(device=device)
    
    flattened_faces = [det["cropped_face"] for det in filtered_detections]
    if len(flattened_faces) > 0:
        ages, genders, ethnicities, age_confs, gender_confs, ethnicity_confs = classifier.predict_age_gender_ethnicity(
            flattened_faces, batch_size = batch_size)

        match mode:
            case "trailer":
                for i, det in enumerate(filtered_detections):
                    det["gender"] = genders[i] if gender_confs[i] >= (gender_conf_threshold / 2) else "unknown"
                    det["age"] = ages[i] if age_confs[i] >= (age_conf_threshold / 9) else "unknown"
                    det["ethnicity"] = ethnicities[i] if ethnicity_confs[i] >= (ethnicity_conf_threshold / 7) else "unknown"
            
            case "poster":
                for i, det in enumerate(filtered_detections):
                    det["gender"] = genders[i]
                    det["age"] = ages[i]
                    det["ethnicity"] = ethnicities[i]

            case _:
                raise ValueError(f"Invalid mode: {mode}. Choose either 'trailer' or 'poster'.")
    
    return filtered_detections, flattened_faces


def embed_faces(flattened_faces, batch_size, device):
    # Embed faces

    embedding_model = faces_clus.EmbeddingModel(device=device)
    embedded_faces = embedding_model.get_embedding(
        batch_size=batch_size, detected_faces=flattened_faces)

    return embedded_faces


def cluster_faces(embedded_faces, model, threshold, classified_faces, method, fps, effective_area):
    # Cluster faces and aggregate predictions for each character

    faces_clustering = faces_clus.FacesClustering(
        model=model, threshold=threshold)
    aggregated_estimations = faces_clustering.aggregate_estimations(
        classified_faces, embedded_faces, fps, effective_area, method=method)

    return aggregated_estimations


def main(
        source, movie_id, num_cpu, batch_size, min_area, max_area, min_conf, min_conf_cla, min_sharpness, min_sharpness_cla, max_z, max_z_cla, min_mouth_opening, min_mouth_opening_cla, cluster_model, cluster_threshold, agr_method, store_video, video_path
        ) -> None:
    start_time = datetime.now()

    # Load data
    data, source_type = load_data(source)
    if source_type == "url":
        poster = data["image"]
    print("Data loaded", datetime.now() - start_time)

    trailer_path = data["trailer_path"]

    if trailer_path == "":
        logger.warning(f"No trailer found for {source}.")
        return

    # Extract frames from video
    frames, fps = utils.frame_capture(trailer_path)
    print("Frames extracted", datetime.now() - start_time)

    # Initialize constants
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    if source_type == "url" :
        # Infer on poster
        print("----- Predicting on poster -----")

        # Initialize constants
        H_original, W_original, total_area, _, _= compute_constants(poster, mode = "poster")
        print("Constants initialized", datetime.now() - start_time)

        # Detect faces in the poster
        detections = detect_faces(poster, H_original, W_original, area_type="face",
                                  batch_size=1, device=device, num_cpu_threads=num_cpu)
        print("Faces detected", datetime.now() - start_time)

        # Filter detections
        filtered_detections = filter_detections_poster(detections, total_area, min_area, min_conf)
        print("Faces filtered", datetime.now() - start_time)

        for i, face in enumerate(filtered_detections):
            cv2.imwrite(f"example/detections/face_{i}.jpg", face["cropped_face"])

        # Classify all faces
        classified_faces, _= classify_faces(filtered_detections, batch_size, device, mode = "poster")
        print("Faces classified", datetime.now() - start_time)

        # Detect bodies in the poster
        body_detections = detect_faces(poster, H_original, W_original, area_type="body", batch_size=1, device=device, num_cpu_threads=num_cpu)
        print("Bodies detected", datetime.now() - start_time)

        for i, body in enumerate(body_detections):
            cv2.imwrite(f"example/detections/body_{i}.jpg", body["cropped_body"])

        linked_detections = vision_detection.link_faces_to_bodies(classified_faces, body_detections)

        for id, face in enumerate(linked_detections):
            occupied_area = filter_det.compute_area(face["body_bbox"], total_area)
            face["occupied_area"] = occupied_area
            print(f"Character {id} with predicted gender: {face['gender']}, age: {face['age']}, ethnicity: {face['ethnicity']} representing {occupied_area:.2%} of the image")

        # Store poster predictions in .pkl file
        with open(f'stored_predictions/{movie_id}_poster_predictions.pkl', 'wb') as outfile :
            pkl.dump(linked_detections, outfile)
        outfile.close()

        # Draw predictions on poster
        utils.draw_predictions_on_poster(poster, linked_detections)
        print("Poster with predictions saved", datetime.now() - start_time)

    # Infer on trailer
    print("----- Predicting on trailer -----")

    # Initialize constants
    H_original, W_original, effective_area, min_sharpness, min_sharpness_cla = compute_constants(frames, mode = "trailer")
    print("Constants initialized", datetime.now() - start_time)

    # Detect faces in the video
    detections = detect_faces(frames, H_original, W_original, area_type="face",
                              batch_size=batch_size, device=device, num_cpu_threads=num_cpu)
    print(f"{len(detections)} faces detected in ", datetime.now() - start_time)

    # Filter detections
    filtered_detections = filter_detections_clustering(
        detections, effective_area, min_area, max_area, min_conf, min_sharpness, max_z, min_mouth_opening)
    print("Faces filtered", datetime.now() - start_time)
    print(f"{len(filtered_detections)} remaining faces.")

    # Classify all filtered faces
    classified_faces, flattened_faces = classify_faces(
        filtered_detections, batch_size, device)
    print("Faces classified", datetime.now() - start_time)

    # Filter detections for classification
    filtered_detections = filter_detections_classifications(
        filtered_detections, min_conf_cla, min_sharpness_cla, max_z_cla, min_mouth_opening_cla)
    print("Faces filtered for majority vote", datetime.now() - start_time)
    print(f"{len(filtered_detections)} faces used for majority vote.")

    # Cluster faces and aggregate predictions for each character
    embedded_faces = embed_faces(flattened_faces, batch_size, device)
    aggregated_estimations = cluster_faces(
        embedded_faces, model=cluster_model, threshold=cluster_threshold, classified_faces=classified_faces, method=agr_method, fps=fps, effective_area=effective_area)
    print("Faces clustered", datetime.now() - start_time)

    # Store trailer predictions in .pkl file
    with open(f'stored_predictions/{movie_id}_trailer_predictions.pkl', 'wb') as outfile :
        pkl.dump(aggregated_estimations, outfile)
    outfile.close()

    # Store predictions on video
    if store_video :
        utils.store_predictions_on_video(
            frames, aggregated_estimations, classified_faces, fps=fps, output_name=f'{video_path}.avi')  # TODO add video name
        print("Video with predictions saved", datetime.now() - start_time)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source", type=str, help="Lien vers la fiche film allociné, chemin vers"
        " le fichier vidéo ou vers un fichier csv pour traiter une liste de"
        " films.")
    parser.add_argument("--column_id", type=str, default="visa_number",
                        help="Column to use to get the identifier to save prediction outputs")
    parser.add_argument("--num_cpu", type=int, default=8,
                        help="Number of CPU threads to use")
    parser.add_argument("--batch_size", type=int, default=64,
                        help="Batch size for inference")
    parser.add_argument("--min_area", type=float, default=0.01,
                        help="Minimum area for detection filter")
    parser.add_argument("--max_area", type=float, default=0.5,
                        help="Maximum area for detection filter")
    parser.add_argument("--min_conf", type=float, default=0.5,
                        help="Minimum confidence for detection filter")
    parser.add_argument("--min_conf_cla", type=float, default=0.6,
                        help="Minimum confidence for classification filter")
    parser.add_argument("--min_sharpness", type=float, default=35.0,
                        help="Minimum sharpness for sharpness filter")
    parser.add_argument("--min_sharpness_cla", type=float, default=200.0,
                        help="Minimum sharpness for sharpness filter")
    parser.add_argument("--max_z", type=float, default=0.5,
                        help="Maximum nose z value for pose filter")
    parser.add_argument("--max_z_cla", type=float, default=-0.2,
                        help="Maximum nose z value for pose filter")
    parser.add_argument("--min_mouth_opening", type=float, default=0.00,
                        help="Minimum upper/lower lips distance for obstruction filter")
    parser.add_argument("--min_mouth_opening_cla", type=float, default=0.01,
                        help="Minimum upper/lower lips distance for obstruction filter")
    parser.add_argument("--cluster_model", type=str,
                        default="chinese_whispers", help="Model for clustering faces")
    parser.add_argument("--cluster_threshold", type=float,
                        default=0.92, help="Threshold for clustering faces")
    parser.add_argument("--agr_method", type=str, default="majority",
                        help="Method for aggregating predictions")
    parser.add_argument("--store_video", action=argparse.BooleanOptionalAction,
                        default=False, help="Store trailer with video predictions")
    parser.add_argument("--video_path", type=str, default="stored_videos/",
                        help="Path to store trailers with video predictions")
    

    args = parser.parse_args()
    os.makedirs("stored_videos", exist_ok=True)
    os.makedirs("stored_predictions", exist_ok=True)
    # Check if the source is a url or a file
    if args.source[:4] == "http":
        logger.info("Source is a url.")
        movie_id = input('Enter filename under which to store predictions (without extension) :')
        main(
            args.source, movie_id, args.num_cpu, args.batch_size, args.min_area, args.max_area, args.min_conf, args.min_conf_cla, args.min_sharpness, args.min_sharpness_cla,
            args.max_z, args.max_z_cla, args.min_mouth_opening, args.min_mouth_opening_cla, args.cluster_model, args.cluster_threshold, args.agr_method,
            args.store_video, args.video_path,
        )

    elif args.source[-4:] == ".csv":
        df = pd.read_csv(args.source)
        logger.info(f"Found {len(df)} films to analyze in the source csv.")
        for _, row in tqdm(df.iterrows(), total=len(df)):
            main(
                row.allocine_url, row[args.column_id], args.num_cpu, args.batch_size, args.min_area, args.max_area, args.min_conf, args.min_conf_cla, args.min_sharpness, args.min_sharpness_cla,
                args.max_z, args.max_z_cla, args.min_mouth_opening, args.min_mouth_opening_cla, args.cluster_model, args.cluster_threshold, args.agr_method,
                args.store_video, args.video_path,
            )
        logger.success(f"All films from {args.source} have been analyzed.")
    else:
        raise ValueError("Source must be a url or a file")
