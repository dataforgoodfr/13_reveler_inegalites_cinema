import argparse
import cv2
import os
import pandas as pd
import pickle as pkl
import numpy as np
import torch

from loguru import logger
from tqdm import tqdm

from scripts import faces_clustering as faces_clus
from scripts import filter_detections as filter_det
from scripts import utils
from scripts import vision_classifiers
from scripts import vision_detection
from scripts import evaluation_annotation 


def load_data(source: str, output_poster: str = "downloaded_poster", output_trailer: str = "downloaded_trailer"):
    # Get data from url or file

    if source[:4] == "http":
        #print(f"Looking for data at: {source}")
        data = utils.get_data_from_url(source, output_poster, output_trailer)
        source_type = "url"
    else:
        #print(f"Looking for data in file: {source}")
        data = utils.get_data_from_file(source, filetype="trailer")
        source_type = "path"
    return data, source_type


def load_data_from_links(row) :
    # Get data directly from poster and trailer links
    os.makedirs("downloaded_media", exist_ok=True)
    output_poster, output_trailer = f"downloaded_media/{row.visa_number}.jpg", f"downloaded_media/{row.visa_number}.mp4"
    utils.download_video_from_link(row.trailer_url, output_trailer)
    utils.download_video_from_link(row.poster_url, output_poster)
    
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


def filter_detections_clustering(detections, effective_area, min_area, max_area, min_conf, movie_id):
    # Filter detections

    filters = filter_det.DetectionFilter(
        simple_filters=[filter_det.validates_area_filter,
                        filter_det.validates_confidence_filter],
        complex_filters=[],
        area_type='face',
        total_area=effective_area,
        min_area=min_area,
        max_area=max_area,
        min_conf=min_conf
    )
    filtered_detections = filters.apply(detections)

    return filtered_detections


def filter_detections_classifications(detections, effective_area, min_conf, min_sharpness, max_z, min_mouth_opening, movie_id, mode="infer"):
    # Filter detections

    filters = filter_det.DetectionFilter(
        simple_filters=[filter_det.validates_confidence_filter],
        complex_filters=[filter_det.validates_sharpness_filter, filter_det.validates_pose_filter],
        area_type='face',
        total_area=effective_area,
        min_conf=min_conf,
        min_sharpness=min_sharpness,
        max_z=max_z,
        min_mouth_opening=min_mouth_opening
    )    
    filtered_detections = filters.apply(detections, mode = "classification")

    if mode == "evaluate":
        filters.visualize_detection_parameters(movie_id=movie_id, detections=detections, storage_folder='visualize_parameters')

    return filtered_detections


def classify_faces(
        filtered_detections, batch_size: int, device: str, source_type: str="trailer", gender_conf_threshold: float = 0.965932283883782, age_conf_threshold: float = 0.5956672158338605, ethnicity_conf_threshold: float = 0.810392266540905
        ) -> tuple[dict, list]:
    # Classify all filtered faces

    classifier = vision_classifiers.VisionClassifier(device=device)
    
    flattened_faces = [det["cropped_face"] for det in filtered_detections]
    if len(flattened_faces) > 0:
        ages, genders, ethnicities, age_confs, gender_confs, ethnicity_confs = classifier.predict_age_gender_ethnicity(
            flattened_faces, batch_size = batch_size)

        match source_type:
            case "trailer":
                for i, det in enumerate(filtered_detections):
                    det["gender"] = genders[i] if gender_confs[i] >= gender_conf_threshold else "unknown"
                    det["gender_conf"] = gender_confs[i]
                    det["age"] = ages[i] if age_confs[i] >= age_conf_threshold else "unknown"
                    det["age_conf"] = age_confs[i]
                    det["ethnicity"] = ethnicities[i] if ethnicity_confs[i] >= ethnicity_conf_threshold else "unknown"
                    det["ethnicity_conf"] = ethnicity_confs[i]
            
            case "poster":
                for i, det in enumerate(filtered_detections):
                    det["gender"] = genders[i]
                    det["age"] = ages[i]
                    det["ethnicity"] = ethnicities[i]

            case _:
                raise ValueError(f"Invalid source_type: {source_type}. Choose either 'trailer' or 'poster'.")
    
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


def gather_and_save_predictions(source:pd.DataFrame) -> None :
    """
    Function to aggregate trailer and poster predictions in one large .csv file for later database insertion.
    """
    path_to_outputs = 'stored_predictions'
    poster_predictions = [os.path.join(path_to_outputs, item) for item in os.listdir(path_to_outputs) if 'poster' in item]
    trailer_predictions = [os.path.join(path_to_outputs, item) for item in os.listdir(path_to_outputs) if 'trailer' in item]
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
        visa_number = int(prediction.split('/')[1].split('_')[0])
        #allocine_url = source[source.visa_number == visa_number].iloc[0]['allocine_url']
        allocine_id = int(source[source.visa_number == visa_number].iloc[0]['allocine_id'])
        for char in data :
            print(char)
            dict_poster_predictions = format_prediction_results('poster', char, allocine_id, visa_number, dict_poster_predictions)
    df_posters = pd.DataFrame(dict_poster_predictions)
    df_posters.to_csv('predictions_on_posters.csv', index=False)

    for prediction in trailer_predictions :
        with open(prediction, 'rb') as infile :
            data = pkl.load(infile)
        infile.close()
        visa_number = int(prediction.split('/')[1].split('_')[0])
        #allocine_url = source[source.visa_number == visa_number].iloc[0]['allocine_url']
        allocine_id = int(source[source.visa_number == visa_number].iloc[0]['allocine_id'])
        for char in data :
            print(char)
            dict_trailer_predictions = format_prediction_results('trailer', char, allocine_id, visa_number, dict_trailer_predictions)
    df_trailers = pd.DataFrame(dict_trailer_predictions)
    df_trailers.to_csv('predictions_on_trailers.csv', index=False)


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


def main(
        source, movie_id, num_cpu, batch_size, min_area, max_area, min_conf, min_conf_cla, min_sharpness, min_sharpness_cla,
        max_z, max_z_cla, min_mouth_opening, min_mouth_opening_cla, cluster_model, cluster_threshold, agr_method, store_visuals, visuals_path, mode='inference', poster_source='None', row=None,
        ) -> None:
    #start_time = datetime.now()

    # Load data

    #data, source_type = load_data(source)
    data, source_type = load_data_from_links(row)
    if source_type == "url":
        poster = data["image"]
    elif poster_source != "None":
        poster = cv2.imread(poster_source)
    #print("Data loaded", datetime.now() - start_time)

    trailer_path = data["trailer_path"]

    if trailer_path == "":
        logger.warning(f"No trailer found for {source}.")
        return

    # Extract frames from video
    frames, fps = utils.frame_capture(trailer_path)
    #print("Frames extracted", datetime.now() - start_time)

    # Initialize constants
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Infer on trailer
    #print("----- Predicting on trailer -----")

    # Initialize constants
    H_original, W_original, effective_area, _, _= compute_constants(frames, movie_id=movie_id, source_type="trailer", mode=mode)
    #print("Constants initialized", datetime.now() - start_time)

    # Detect faces in the video
    detections = detect_faces(frames, H_original, W_original, area_type="face",
                              batch_size=batch_size, device=device, num_cpu_threads=num_cpu)
    #print(f"{len(detections)} faces detected in ", datetime.now() - start_time)

    # Filter detections
    filtered_detections = filter_detections_clustering(
        detections, effective_area, min_area, max_area, min_conf, movie_id)
    #print("Faces filtered", datetime.now() - start_time)
    #print(f"{len(filtered_detections)} remaining faces.")

    # Classify all filtered faces
    classified_faces, flattened_faces = classify_faces(
        filtered_detections, batch_size, device)
    #print("Faces classified", datetime.now() - start_time)

    # Filter detections for classification
    filtered_detections = filter_detections_classifications(
        classified_faces, effective_area, min_conf_cla, min_sharpness_cla, max_z_cla, min_mouth_opening_cla, movie_id, mode=mode)
    #print("Faces filtered for majority vote", datetime.now() - start_time)
    #print(f"{len(filtered_detections)} faces used for majority vote.")

    # Cluster faces and aggregate predictions for each character
    embedded_faces = embed_faces(flattened_faces, batch_size, device)
    aggregated_estimations = cluster_faces(
        embedded_faces, model=cluster_model, threshold=cluster_threshold, classified_faces=filtered_detections,
        method=agr_method, fps=fps, effective_area=effective_area)
    #print("Faces clustered", datetime.now() - start_time)

    # Store predictions on video
    if store_visuals :
        utils.store_predictions_on_video(
            frames, aggregated_estimations, classified_faces, fps=fps, output_name=movie_id)
       # print("Video with predictions saved", datetime.now() - start_time)
    
    if source_type == "url" or poster_source != "None" :
        # Infer on poster
        #print("----- Predicting on poster -----")

        # Initialize constants
        H_original, W_original, total_area, _, _ = compute_constants(poster, movie_id, mode=mode, source_type="poster")
        #print("Constants initialized", datetime.now() - start_time)

        # Detect faces in the poster
        detections = detect_faces(poster, H_original, W_original, area_type="face",
                                  batch_size=1, device=device, num_cpu_threads=num_cpu)
        #print("Faces detected", datetime.now() - start_time)

        # Filter detections
        filtered_detections = filter_detections_poster(detections, total_area, min_area, min_conf)
        #print("Faces filtered", datetime.now() - start_time)
        
        flattened_faces_poster = [face["cropped_face"] for face in filtered_detections]
        embedded_faces_poster = embed_faces(flattened_faces_poster, batch_size, device)
        all_indexes = set()  # Use a set to avoid duplicates
        for video_person in aggregated_estimations:
            all_indexes.update(video_person["persons_ids"])  # Add all indexes from persons_ids

            # Step 2: Filter embedded_faces to keep only the embeddings corresponding to the collected indexes
            embedded_faces = [embedding for i, embedding in enumerate(embedded_faces) if i in all_indexes]

        for index, face in enumerate(embedded_faces_poster):
            cv2.imwrite(f"example/detections/face_{index}.jpg", flattened_faces_poster[index])

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
            
                occupied_area = filter_det.compute_area(filtered_detections[index]["bbox"], total_area)
                filtered_detections[index]["occupied_area"] = occupied_area
                #print(f"Character {closest_index} with predicted gender: {filtered_detections[index]['gender']}, age: {filtered_detections[index]['age']}, ethnicity: {filtered_detections[index]['ethnicity']} representing {occupied_area:.2%} of the image")
            else:
                # Delete the detection from filtered_detections
                del filtered_detections[index]

        '''
        # Classify all faces
        classified_faces, _ = classify_faces(filtered_detections, batch_size, device, mode = "poster")
        print("Faces classified", datetime.now() - start_time)
        '''
            
        # Store poster predictions in .pkl file
        with open(f'stored_predictions/{movie_id}_poster_predictions.pkl', 'wb') as outfile :
            pkl.dump(filtered_detections, outfile)
        outfile.close()

        if store_visuals :
            # Draw predictions on poster
            utils.draw_predictions_on_poster(poster, filtered_detections)
            #print("Poster with predictions saved", datetime.now() - start_time)

    match mode:
        case 'evaluate':
            score_tot, score_kept_frames = evaluation_annotation.evaluate_trailer_whole_pipeline(trailer_path, aggregated_estimations)
            #print(f"Score for {trailer_path}: {score_tot:.2f} if including non kept frames, {score_kept_frames:.2f} if only kept frames")
            return score_tot, score_kept_frames
        case _:
            # Store trailer predictions in .pkl file
            with open(f'stored_predictions/{movie_id}_trailer_predictions.pkl', 'wb') as outfile :
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
    # Check if the source is a url or a file
    if args.source[:4] == "http" or args.source[-4:] == ".mp4":
        if args.source[:4] == "http":
            logger.info("Source is a URL.")
            movie_id = input('Enter filename under which to store predictions (without extension) :')
        else:
            logger.info("Source is an mp4 file.")
            movie_id = os.path.splitext(os.path.basename(args.source))[0]  # Extract file name without extension
        predictions = main(
            args.source, movie_id, args.num_cpu, args.batch_size, args.min_area, args.max_area, args.min_conf, args.min_conf_cla, args.min_sharpness, args.min_sharpness_cla,
            args.max_z, args.max_z_cla, args.min_mouth_opening, args.min_mouth_opening_cla, args.cluster_model, args.cluster_threshold, args.agr_method,
            args.store_visuals, args.visuals_path, mode=args.mode, poster_source=args.source_image, row=None,
        )

    elif args.source[-4:] == ".csv":
        df = pd.read_csv(args.source)
        istart = args.istart
        istop = min(len(df), args.istop)
        df = df.iloc[istart:istop]
        logger.info(f"Found {len(df)} films to analyze in the source csv.")
        for _, row in tqdm(df.iterrows(), total=len(df)):
            predictions = main(
                row.allocine_url, row[args.column_identifier], args.num_cpu, args.batch_size, args.min_area, args.max_area, args.min_conf, args.min_conf_cla, args.min_sharpness, args.min_sharpness_cla,
                args.max_z, args.max_z_cla, args.min_mouth_opening, args.min_mouth_opening_cla, args.cluster_model, args.cluster_threshold, args.agr_method,
                args.store_visuals, args.visuals_path, row=row,
            )
            os.remove(f"downloaded_media/{row.visa_number}.jpg")
            os.remove(f"downloaded_media/{row.visa_number}.mp4")
        logger.success(f"All films from {args.source} have been analyzed.")
        gather_and_save_predictions(df)
    else:
        raise ValueError("Source must be a url or a file")
