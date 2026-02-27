# ML Image Analysis Pipeline Documentation

## Overview

This pipeline performs automated face detection, classification, and demographic analysis on movie trailers and posters. It uses computer vision and machine learning models to identify characters, cluster them across frames, and extract demographic information (gender, age, ethnicity).

## Pipeline Architecture

The pipeline consists of three main processing stages:

1. **Trailer Analysis** - Process video frames to detect and classify faces
2. **Poster Analysis** - Process poster images and match faces to trailer characters
3. **Aggregation & Storage** - Combine results and save predictions

---

## 1. Trailer Analysis Pipeline (`infer_on_trailer`)

### Step 1: Frame Extraction
- Extract all frames from the video trailer
- Capture frame rate (fps) for temporal analysis normalisation (24 appearances at 24 fps is not the same as 24 appearances at 50fps)

### Step 2: Constant Initialization
- Calculate original video dimensions (height, width)
- Compute effective detection area
- Initialize parameters based on movie ID and mode (we compute video sharpness to compare later with detected face sharpness [NOT USED ACTUALLY])

### Step 3: Face Detection
- Use vision detection models (YOLO) to identify faces in all frames
- Detect bounding boxes [with configurable expansion factor - to be merged]
- Process in batches for efficiency (GPU/CPU)

### Step 4: Filtering (Pre-Classification)

We exclude here detected faces with very low quality.
- Filter detections based on:
  - Minimum area threshold
  - Maximum area threshold
  - Minimum confidence score
- Exclude detections outside effective area
- **Memory optimization**: Delete original detections

### Step 5: Face Classification
- Classify filtered faces for demographic attributes
- Extract demographic features:
  - Gender
  - Age
  - Ethnicity
- **Memory optimization**: Clear filtered detections after classification

### Step 6: Face Quality scoring
- Compute quality scores based of the following criteria:
  - Minimum classification confidence
  - Minimum sharpness score
  - Maximum "z-score" (person facing camera, or not, by calculating nose tip z-orientation) [to not be confused with z-score of statistical deviation]
- These scores are used later (in Step 8.) for ponderation.

### Step 7: Face Embedding
- Generate embeddings for face recognition
- Convert faces to high-dimensional vectors for clustering
- **Memory optimization**: Delete flattened faces after embedding

### Step 8: Face Clustering and Attributes Computing
- Group faces belonging to the same character across frames
- Use configurable clustering model (ChineseWhispers) and threshold
- Aggregate predictions per character:
  - Weighted Average demographic attributes (using scores weights from Step 6.)
  - Track person IDs
  - Calculate temporal presence (accordingly to video frame-rate)
  - Compute screen time and area
- Exclude clusters with very low number of faces detected (threshold as parameter)

### Step 9: Visual Output (Optional)
- If `store_visuals` is enabled:
  - Draw bounding boxes on frames
  - Annotate with demographic predictions
  - Save annotated video

### Step 10: Memory Cleanup
- Delete intermediate variables
- Clear CUDA cache (if using GPU)
- Free memory for next processing

### Output
- `aggregated_estimations`: List of character clusters with demographic data
- `embedded_faces`: Face embeddings generated in this pipeline will be reuse in poster matching
- `flattened_faces_perso_ids`: Person IDs corresponding to each embedding

---

## 2. Poster Analysis Pipeline (`infer_on_poster`)

### Step 1: Constant Initialization
- Calculate poster dimensions
- Compute total area for area calculations

### Step 2: Face Detection
- Detect faces in poster image (YoLo)
- Single batch processing (posters are static images)

### Step 3: Filtering
- Apply area and confidence thresholds
- Remove very low-quality detections

### Step 4: Face Embedding
- Extract embeddings for detected poster faces
- Prepare for matching with trailer embeddings characters

### Step 5: Embedding Filtering
- Extract person IDs from trailer aggregations
- Filter trailer embeddings to only include selected characters (only those selected on Step8 of `infer_on_trailer`)
- **Memory optimization**: Clear detection tensors and CUDA cache

### Step 6: Assign Poster
- Compare each poster detected face with each trailer detected embeddings

##### Matching Process
For each face detected in the poster:

1. **Find Closest Match**
   - Calculate Euclidean distance to all trailer embeddings
   - Identify the closest character cluster

2. **Assign Demographics**
   - Match to aggregated trailer estimations
   - Transfer demographic attributes:
     - Gender
     - Age
     - Ethnicity

3. **Calculate Occupied Area**
   - Compute relative screen area occupied by face
   - Normalize by total poster area

4. **Handle Unmatched Faces**
   - Track faces that don't match any trailer character
   - Remove from final detections

##### Visual Output (Optional)
- If `store_visuals` is enabled:
  - Draw predictions on poster
  - Save annotated poster image

### Output
- `filtered_detections`: Poster faces with assigned demographics

---

## 3. Single Item Prediction (`predict_one_item`)

Orchestrates the complete analysis for one movie:

### Steps
1. **Data Loading**
   - Load poster and trailer from paths or URLs
   - Extract movie identifier

2. **Device Selection**
   - Auto-detect GPU availability
   - Configure CUDA/CPU processing

3. **Trailer Processing**
   - Call `infer_on_trailer` with all parameters
   - Get character clusters and embeddings

4. **Poster Processing** (if available)
   - Call `infer_on_poster` for face detection

5. **Output**
   - Return trailer aggregations and poster detections

---

## 5. Batch Inference Pipeline (`infer_pipeline`)

Processes multiple movies from a CSV file:

### Workflow

1. **Data Preparation**
   - Load CSV with movie metadata
   - Select subset based on `istart` and `istop` indices

2. **Memory Profiling** (Optional)
   - Track GPU memory usage
   - Log allocation statistics

3. **Batch Processing**
   - Iterate through each movie row
   - For each movie:
     - Load poster and trailer
     - Run `predict_one_item`
     - Save predictions to pickle files:
       - `{movie_id}_poster_predictions.pkl`
       - `{movie_id}_trailer_predictions.pkl`
     - Clean up downloaded media files
     - Clear memory and CUDA cache

4. **Error Handling**
   - Log errors for individual movies
   - Continue processing remaining movies
   - Always clear CUDA cache on error

5. **Final Aggregation**
   - Gather all prediction files
   - Combine into final output format
   - Save consolidated predictions

### Output Files
- Individual predictions: `tmp/stored_predictions/{movie_id}_*.pkl`
- Final aggregated: `outputs/final_predictions/`

---


## Key Configuration Parameters

### Detection Parameters
- `min_area`: Minimum face area threshold
- `max_area`: Maximum face area threshold
- `min_conf`: Minimum detection confidence
- `bbox_expand_factor`: Factor to expand bounding boxes (default: 0.3)

### Classification Parameters
- `min_conf_cla`: Minimum classification confidence
- `min_sharpness_cla`: Minimum image sharpness
- `max_z_cla`: Maximum score for nose point z-orientation
- `min_mouth_opening_cla`: Minimum mouth opening threshold (not used)

### Clustering Parameters
- `cluster_model`: Clustering algorithm to use
- `cluster_threshold`: Threshold for cluster assignment
- `agr_method`: Aggregation method for cluster predictions

### Processing Parameters
- `batch_size`: Batch size for model inference
- `device`: Processing device (auto/cuda/cpu)
- `num_cpu`: Number of CPU threads
- `store_visuals`: Whether to save annotated images/videos

---

## Memory Management

The pipeline implements aggressive memory management:

1. **Explicit Deletion**
   - Delete large arrays after use
   - Clear intermediate results

2. **CUDA Cache Management**
   - Clear GPU cache after each movie
   - Synchronize CUDA operations
   - Monitor memory allocation

3. **Batch Processing**
   - Process images/frames in configurable batches
   - Prevent out-of-memory errors

4. **File Cleanup**
   - Remove downloaded media after processing
   - Use temporary storage for predictions

---

## Output Data Structure

### Trailer Predictions

TODO: UPDATE 
```python
{
    "persons_ids": [list of frame indices],
    "gender": "male/female",
    "age": estimated_age,
    "ethnicity": "ethnicity_label",
    "screen_time": seconds,
    "occupied_area": percentage
}
```

### Poster Predictions

TODO: UPDATE 
```python
{
    "bbox": [x, y, width, height],
    "gender": "male/female",
    "age": estimated_age,
    "ethnicity": "ethnicity_label",
    "occupied_area": percentage,
    "cropped_face": numpy_array
}
```

---

## Error Handling

The pipeline includes robust error handling:

1. **Missing Data**: Skips movies without trailers
2. **Processing Errors**: Logs errors and continues with next movie
3. **Memory Errors**: Clears cache and attempts to continue
4. **Invalid Input**: Validates CSV format and columns

---

## Future Improvements

1. Evaluate improvements of expanded bounding boxes
2. Main characters may be too frequent and poluate clusters
3. Include humans-in-the-loop for labeling process
4. CHECK FOR LINUX/WINDOWS TORCH ISSUE
