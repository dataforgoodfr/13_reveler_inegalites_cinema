from visionmodel import VisionModel
from datetime import datetime
from faces_clustering import Faces_clustering, Embedding_model, Frame_person
from torchvision import transforms
import torch
import cv2
from PIL import Image
import numpy as np
import sys

def FrameCapture(path): 
	# Function to extract frames
    vidObj = cv2.VideoCapture(path) 
    frames = []

	# Used as counter variable 
    count = 0

	# checks whether frames were extracted 
    success = 1
    
    while success: 
        # vidObj object calls read 
        # function extract frames 
        success, image = vidObj.read() 
        if not success:
            break
        frames.append(image)

		# Saves the frames with frame-count 
        #cv2.imwrite("frame%d.jpg" % count, image) # Unquote to save frames on your device
        count += 1
        
    return np.array(frames)

def infer_on_frame(frame, vision_model, embedding_model, frame_id, global_face_id):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    vision_model.crop_faces(Image.fromarray(rgb_frame))
    
    embedded_faces = embedding_model.get_embedding(batch_size = 64, detected_faces = vision_model.cropped_faces)

    predictions_gender = []
    predictions_age = []

    for face in vision_model.cropped_faces:
        gender, age = vision_model.predict_age_gender(face)
        predictions_gender.append(gender)
        predictions_age.append(age)

    predictions_ethnicity = []
    if len(vision_model.cropped_faces) > 0:
        predictions_ethnicity = vision_model.predict_ethnicity(vision_model.cropped_faces)

    #predictions_str = [str(x) + ", " + str(y) for x, y in zip(predictions_gender, predictions_ethnicity)]
    #vision_model.draw_bounding_boxes(vision_model.image, vision_model.cropped_faces_boxes, predictions_age, predictions_str)
    #print(predictions_str, datetime.now() - start_time)
    
    faces_id = [i for i in range(global_face_id, global_face_id + len(predictions_age))]
    persons_in_frame = [Frame_person(age, gender, ethnicity, face, bbox, frame_id, face_id) for face, bbox, gender, age, ethnicity, face_id in zip(vision_model.cropped_faces, vision_model.cropped_faces_boxes, predictions_gender, predictions_age, predictions_ethnicity, faces_id)]

    return persons_in_frame, embedded_faces

def draw_predictions_on_video(frames, video_persons: list, frame_persons: list):
    frame_index = 0
    for frame in frames:
        for person in frame_persons:
            if person.frame_id == frame_index:
                bbox = [int(coord) for coord in person.bbox]  # Ensure bbox coordinates are integers
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
                for video_person in video_persons:
                    if person.face_id in video_person.faces_id:
                        cv2.putText(frame, f"{video_person.person_id}, {video_person.age}, {video_person.gender}", (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (36,255,12), 2)
        frame_index += 1
    
    return frames

def store_predictions_on_video(frames, video_persons: list, frame_persons: list, fps: int = 25, output_path: str = 'predictions_video.avi'):
    # Draw predictions on video frames
    modified_frames = draw_predictions_on_video(frames, video_persons, frame_persons)

    # Define the codec and create VideoWriter object
    height, width, layers = modified_frames[0].shape
    video = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'DIVX'), fps, (width, height))

    # Write each frame to the video file
    for frame in modified_frames:
        video.write(frame)

    # Release the VideoWriter object
    video.release()         

def main():
    if len(sys.argv) < 2:
        print("Erreur : Aucun lien fourni !")
        sys.exit(1)

    link = sys.argv[1]
    print(f"Looking for data at: {link}")

    start_time = datetime.now()
    vision_model = VisionModel()
    vision_model.get_data_from_url(link)

    frame_id = 0
    global_face_id = 0

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Transformation for model compliance
    face_transform = transforms.Compose([
        transforms.ToTensor(),          # Convertir en tenseur
        transforms.Resize((160, 160)),  # Taille attendue par FaceNet
        transforms.Normalize([0.5], [0.5])  # Normalisation [-1, 1]
    ])

    embedding_model = Embedding_model(model = "facenet", transform = face_transform, device = device)

    frames = FrameCapture(vision_model.trailer_path)
    persons_list = []
    embedded_faces_list = []

    for frame in frames:
        persons_in_frame, embedded_faces = infer_on_frame(frame, vision_model, embedding_model, frame_id, global_face_id)
        if len(persons_in_frame) > 0:
            persons_list.append(persons_in_frame) # To change for all frames
            embedded_faces_list.append(embedded_faces)

        frame_id += 1
        global_face_id += len(vision_model.cropped_faces)

        print(frame_id, datetime.now() - start_time)

    embedded_faces = np.concatenate(embedded_faces_list)
    persons_in_frame = [person for persons in persons_list for person in persons]

    faces_clustering = Faces_clustering(model="chinese_whispers", threshold=0.92)
    aggregated_estimations = faces_clustering.aggregate_estimations(persons_in_frame, embedded_faces, method="majority")

    '''
    print(f"{len(aggregated_estimations)} detected separated characters", datetime.now() - start_time)
    for person in aggregated_estimations:
        print(person)
        person.show_faces(persons_in_frame, max_faces = 25)
    '''
    store_predictions_on_video(frames, aggregated_estimations, persons_in_frame, fps=25, output_path='predictions_video.avi')
    print("Video with predictions saved", datetime.now() - start_time)

if __name__ == '__main__':
    main()