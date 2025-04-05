from datetime import datetime
import scripts
import torch
import argparse
import cv2

def load_data(source):
    ### Get data from url or file

    if source[:4] == "http":
        print(f"Looking for data at: {source}")
        data = scripts.get_data_from_url(source)
    else:
        print(f"Looking for data in file: {source}")
        data = scripts.get_data_from_file(source, filetype="trailer")
    return data

def detect_faces(frames, H_original, W_original, area_type, batch_size, device, num_cpu_threads):
    ### Detect faces in the video

    vision_detector = scripts.VisionDetection(device = device, num_cpu_threads = num_cpu_threads)
    detections = vision_detector.crop_areas_of_interest(frames, H_original, W_original, area_type = area_type, batch_size = batch_size)

    return detections

def filter_detections_clustering(detections, effective_area, min_area, max_area, min_conf, min_sharpness, max_z, min_mouth_opening):
    ### Filter detections

    filters = scripts.DetectionFilter(
        simple_filters=[scripts.validates_area_filter, scripts.validates_confidence_filter],
        complex_filters=[scripts.validates_sharpness_filter, scripts.validates_pose_filter],
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
    ### Filter detections

    filters = scripts.DetectionFilter(
        simple_filters=[scripts.validates_confidence_filter],
        complex_filters=[scripts.validates_sharpness_filter, scripts.validates_pose_filter],
        area_type='face',
        min_conf=min_conf,
        min_sharpness=min_sharpness,
        max_z=max_z,
        min_mouth_opening=min_mouth_opening
    )    
    filtered_detections = filters.apply(detections, mode = "classification")

    return filtered_detections

def classify_faces(filtered_detections, batch_size, device, conf_threshold=1.1):
    ### Classify all filtered faces

    classifier = scripts.VisionClassifier(device = device)
    
    flattened_faces = [det["cropped_face"] for det in filtered_detections]
    if len(flattened_faces) > 0:
        ages, genders, ethnicities, age_confs, gender_confs, ethnicity_confs = classifier.predict_age_gender_ethnicity(flattened_faces, batch_size = batch_size)

        for i, det in enumerate(filtered_detections):
            #print(gender_confs[i], age_confs[i], ethnicity_confs[i])
            det["gender"] = genders[i] if gender_confs[i] >= (1.2 / 2) else "unknown"
            det["age"] = ages[i] if age_confs[i] >= (1.05 / 9) else "unknown"
            det["ethnicity"] = ethnicities[i] if ethnicity_confs[i] >= (1.1 / 7) else "unknown"
    
    return filtered_detections, flattened_faces

def embed_faces(flattened_faces, batch_size, device):
    ### Embed faces

    embedding_model = scripts.EmbeddingModel(device = device)
    embedded_faces = embedding_model.get_embedding(batch_size = batch_size, detected_faces = flattened_faces)

    return embedded_faces

def cluster_faces(embedded_faces, model, threshold, classified_faces, method):
    ### Cluster faces and aggregate predictions for each character

    faces_clustering = scripts.FacesClustering(model=model, threshold=threshold)
    aggregated_estimations = faces_clustering.aggregate_estimations(classified_faces, embedded_faces, method=method)

    return aggregated_estimations

def main(source, num_cpu, batch_size, min_area, max_area, min_conf, min_conf_cla, min_sharpness, min_sharpness_cla, max_z, max_z_cla, min_mouth_opening, min_mouth_opening_cla, cluster_model, cluster_threshold, agr_method):
    start_time = datetime.now()

    ### Load data
    data = load_data(source)
    print("Data loaded", datetime.now() - start_time)

    ### Extract frames from video
    frames = scripts.frame_capture(data["trailer_path"])
    print("Frames extracted", datetime.now() - start_time)

    ### Initialize constants
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    overall_sharpness = 0
    for frame in frames:
        overall_sharpness += scripts.compute_sharpness(frame)/len(frames)
    min_sharpness = overall_sharpness/42
    min_sharpness_cla = overall_sharpness/7.3

    H_original, W_original = frames[0].shape[:2]
    effective_height = W_original / 2.478 # 2.4 is the aspect ratio of the video
    effective_area = effective_height * W_original
    
    '''effective_top_left, effective_bot_right = scripts.find_video_effective_area(frames)
    effective_height = effective_bot_right[1] - effective_top_left[1]
    effective_width = effective_bot_right[0] - effective_top_left[0]
    effective_area = effective_height * effective_width
    print("Effective dimensions:", effective_height, effective_width, datetime.now() - start_time)

    frames = frames[:,effective_top_left[1]:effective_bot_right[1], effective_top_left[0]:effective_bot_right[0]]'''

    ### Detect faces in the video
    detections = detect_faces(frames, H_original, W_original, area_type="face", batch_size=batch_size, device=device, num_cpu_threads=num_cpu)
    print("Faces detected", datetime.now() - start_time)

    ### Filter detections
    filtered_detections = filter_detections_clustering(detections, effective_area, min_area, max_area, min_conf, min_sharpness, max_z, min_mouth_opening)
    print("Faces filtered", datetime.now() - start_time)

    ### Classify all filtered faces
    classified_faces, flattened_faces = classify_faces(filtered_detections, batch_size, device)
    print("Faces classified", datetime.now() - start_time)

    ### Filter detections for classification
    filtered_detections = filter_detections_classifications(filtered_detections, min_conf_cla, min_sharpness_cla, max_z_cla, min_mouth_opening_cla)
    print("Faces filtered 2", datetime.now() - start_time)

    ### Cluster faces and aggregate predictions for each character
    embedded_faces = embed_faces(flattened_faces, batch_size, device)
    aggregated_estimations = cluster_faces(embedded_faces, model=cluster_model, threshold=cluster_threshold, classified_faces=classified_faces, method=agr_method)
    print("Faces clustered", datetime.now() - start_time)

    ### Store predictions on video
    scripts.store_predictions_on_video(frames, aggregated_estimations, classified_faces, fps=25, output_name='predictions_trailer.avi')
    print("Video with predictions saved", datetime.now() - start_time)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=str, help="Lien vers la fiche film allociné ou chemin vers le fichier vidéo")
    parser.add_argument("--num_cpu", type=int, default=8, help="Number of CPU threads to use")
    parser.add_argument("--batch_size", type=int, default=64, help="Batch size for inference")
    parser.add_argument("--min_area", type=float, default=0.01, help="Minimum area for detection filter")
    parser.add_argument("--max_area", type=float, default=0.5, help="Maximum area for detection filter")
    parser.add_argument("--min_conf", type=float, default=0.5, help="Minimum confidence for detection filter")
    parser.add_argument("--min_conf_cla", type=float, default=0.6, help="Minimum confidence for detection filter")
    parser.add_argument("--min_sharpness", type=float, default=35.0, help="Minimum sharpness for detection filter")
    parser.add_argument("--min_sharpness_cla", type=float, default=200.0, help="Minimum sharpness for detection filter")
    parser.add_argument("--max_z", type=float, default=0.5, help="Maximum nose z value for pose filter")
    parser.add_argument("--max_z_cla", type=float, default=-0.2, help="Maximum nose z value for pose filter")
    parser.add_argument("--min_mouth_opening", type=float, default=0.00, help="Minimum upper/lower lips distance for obstruction filter")
    parser.add_argument("--min_mouth_opening_cla", type=float, default=0.01, help="Minimum upper/lower lips distance for obstruction filter")
    parser.add_argument("--cluster_model", type=str, default="chinese_whispers", help="Model for clustering faces")
    parser.add_argument("--cluster_threshold", type=float, default=0.92, help="Threshold for clustering faces")
    parser.add_argument("--agr_method", type=str, default="majority", help="Method for aggregating predictions")
    
    args = parser.parse_args()
    main(args.source, args.num_cpu, args.batch_size, args.min_area, args.max_area, args.min_conf, args.min_conf_cla, args.min_sharpness, args.min_sharpness_cla, args.max_z, args.max_z_cla, args.min_mouth_opening, args.min_mouth_opening_cla, args.cluster_model, args.cluster_threshold, args.agr_method)