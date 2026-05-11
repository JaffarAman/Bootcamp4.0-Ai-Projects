import os
from deepface import DeepFace

dataset_path = r"d:\tmp\Bootcamp 4.0\ONLY COMPUTER VISION\Unified_System\Computer-Vision-mobile-detection\dataset_faces"
print("Existing dataset path:", os.path.exists(dataset_path))

img_path = os.path.join(dataset_path, "mohammad ukkasha_268466", "face_1.jpg")
print("Existing img path:", os.path.exists(img_path))

try:
    dfs = DeepFace.find(img_path=img_path, db_path=dataset_path, model_name="ArcFace", distance_metric="cosine", enforce_detection=False, silent=True)
    print("Find result:", dfs)
except Exception as e:
    print("Error:", e)
