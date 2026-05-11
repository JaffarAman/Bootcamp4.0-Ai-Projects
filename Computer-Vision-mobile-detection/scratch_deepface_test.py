import cv2
from deepface import DeepFace
import os

dataset_path = "dataset_faces"
img_path = os.path.join(dataset_path, "ahmed_22112121", "face_1.jpg") # pick an existing face
frame = cv2.imread(img_path)

if frame is not None:
    try:
        dfs = DeepFace.find(img_path=frame, db_path=dataset_path, model_name="ArcFace", distance_metric="cosine", enforce_detection=False, silent=True)
        print("dfs type:", type(dfs))
        if len(dfs) > 0:
            print("dfs[0] type:", type(dfs[0]))
            print("dfs[0] empty:", dfs[0].empty)
            if not dfs[0].empty:
                print("columns:", dfs[0].columns)
                matched_path = dfs[0].iloc[0]['identity']
                print("matched_path:", matched_path)
                folder_name = os.path.basename(os.path.dirname(matched_path))
                print("folder_name:", folder_name)
    except Exception as e:
        print("Error:", e)
else:
    print("Could not load image.")
