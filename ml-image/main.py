import argparse
import os

from scripts import pipelines

PREDICTIONS_FOLDER = os.environ.get('PREDICTIONS_FOLDER', 'stored_predictions')
DOWNLOADED_MEDIA_FOLDER =  os.environ.get('DOWNLOADED_MEDIA_FOLDER', 'downloaded_media')
TEMP_FOLDER = os.environ.get('TEMP_FOLDER', 'tmp')
OUTPUTS_FOLDER = os.environ.get('OUTPUTS_FOLDER', 'outputs')
FINAL_PREDICTIONS_FOLDER = os.environ.get('FINAL_PREDICTIONS_FOLDER', 'final_predictions')

def main(parser):
    args = parser.parse_args()
    
    os.makedirs(TEMP_FOLDER, exist_ok=True)
    visuals_path = os.path.join(TEMP_FOLDER, args.visuals_path) #FIXME: use this arg or delete it
    os.makedirs(visuals_path, exist_ok=True)
    temp_predictions_path = os.path.join(TEMP_FOLDER, PREDICTIONS_FOLDER)
    os.makedirs(temp_predictions_path, exist_ok=True)
    downloaded_media_path = os.path.join(TEMP_FOLDER, DOWNLOADED_MEDIA_FOLDER)
    os.makedirs(downloaded_media_path, exist_ok=True)
    final_predictions_path = os.path.join(OUTPUTS_FOLDER, FINAL_PREDICTIONS_FOLDER)
    os.makedirs(final_predictions_path, exist_ok=True)

    paths = {
        'dl_media': downloaded_media_path,
        'final_preds': final_predictions_path,
        'temp_preds': temp_predictions_path,
        'visuals': visuals_path
    }

    pipelines.handler(args, paths)
        
if __name__ == '__main__':
    # Fetch args
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

    main(parser)
