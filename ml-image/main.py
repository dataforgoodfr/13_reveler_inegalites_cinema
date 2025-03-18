from scripts import VisionDetection, VisionClassifier, Embedding_model, Faces_clustering, DetectionFilter, filter_by_area, filter_by_confidence, filter_by_sharpness, get_data_from_file, get_data_from_url, store_predictions_on_video, frame_capture

from datetime import datetime
import torch

import sys

def main() :
    start_time = datetime.now()

    ### Get data from url
    if len(sys.argv) < 2:
        print("Erreur : Aucun lien fourni !")
        sys.exit(1)

    link = sys.argv[1]
    print(f"Looking for data at: {link}")
    data = get_data_from_url(link)

    ### Extract frames from video
    frames = frame_capture(data["trailer_path"])
    H_original, W_original = frames[0].shape[:2]

    ### Initialize models
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    vision_dectector = VisionDetection(device = device)
    classifier = VisionClassifier(device = device)
    embedding_model = Embedding_model(model = "facenet", device = device)
    
    ### Detect faces in the video
    detections = vision_dectector.crop_areas_of_interest(frames, H_original, W_original, area_type = 'face')
    
    ### Filter detections
    total_area = H_original * W_original
    filters = DetectionFilter(simple_filters = [filter_by_area, filter_by_confidence], complex_filters = [filter_by_sharpness], area_type = 'face', total_area = total_area, min_area = 0.03, min_sharpness = 30.0, min_conf = 0.6)
    filtered_detections = filters.apply(detections)

    ### Classify all filtered faces
    flattened_faces = [det["cropped_face"] for det in filtered_detections]
    if len(flattened_faces) > 0:
        genders, ages = classifier.predict_age_gender(flattened_faces)
        ethnicities = classifier.predict_ethnicity(flattened_faces)

        for i, det in enumerate(filtered_detections):
            det["gender"] = genders[i]
            det["age"] = ages[i]
            det["ethnicity"] = ethnicities[i]

    ### Cluster faces and aggregate predictions for each character
    embedded_faces = embedding_model.get_embedding(batch_size = 64, detected_faces = flattened_faces)
    
    faces_clustering = Faces_clustering(model="chinese_whispers", threshold=0.92)

    aggregated_estimations = faces_clustering.aggregate_estimations(filtered_detections, embedded_faces, method="majority")

    ### Store predictions on video
    store_predictions_on_video(frames, aggregated_estimations, filtered_detections, fps=25, output_name='predictions_trailer.avi')
    print("Video with predictions saved", datetime.now() - start_time)

if __name__ == '__main__':
    main()