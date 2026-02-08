
import os
import requests
import bz2
import shutil

MODEL_URL = "https://github.com/davisking/dlib-models/raw/master/shape_predictor_68_face_landmarks.dat.bz2"
MODEL_DIR = "models"
BZ2_PATH = os.path.join(MODEL_DIR, "shape_predictor_68_face_landmarks.dat.bz2")
DAT_PATH = os.path.join(MODEL_DIR, "shape_predictor_68_face_landmarks.dat")

def download_model():
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        
    if os.path.exists(DAT_PATH):
        print("Model already exists.")
        return

    print(f"Downloading model from {MODEL_URL}...")
    response = requests.get(MODEL_URL, stream=True)
    with open(BZ2_PATH, "wb") as f:
        shutil.copyfileobj(response.raw, f)
    
    print("Extracting model...")
    with bz2.BZ2File(BZ2_PATH) as fr:
        with open(DAT_PATH, "wb") as fw:
            shutil.copyfileobj(fr, fw)
    
    os.remove(BZ2_PATH)
    print("Model downloaded and extracted successfully.")

if __name__ == "__main__":
    download_model()
