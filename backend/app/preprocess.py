import os
import numpy as np
from PIL import Image
import pandas as pd
from pathlib import Path

# Class mapping (adjust based on your model's training)
CLASS_MAPPING = {0: "Benign", 1: "Malignant"}  # Extend if more classes exist

def preprocess_ultrasound(image_path, image_size=(128, 128)):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image {image_path} does not exist.")
    try:
        with Image.open(image_path) as img:
            img = img.resize(image_size).convert('RGB')
            image_array = np.array(img) / 255.0
        return np.array([image_array])
    except Exception as e:
        raise ValueError(f"Error processing ultrasound image {image_path}: {e}")

def preprocess_mammogram(img_path, breast_mask_path, dense_mask_path, img_size=(224, 224)):
    for path in [img_path, breast_mask_path, dense_mask_path]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File {path} does not exist.")
    try:
        img = Image.open(img_path).convert('L').resize(img_size)
        breast_mask = Image.open(breast_mask_path).convert('L').resize(img_size)
        dense_mask = Image.open(dense_mask_path).convert('L').resize(img_size)
        img = np.array(img) / 255.0
        breast_mask = np.array(breast_mask) / 255.0
        dense_mask = np.array(dense_mask) / 255.0
        combined = np.stack([img, breast_mask, dense_mask], axis=-1)
        return np.array([combined])
    except Exception as e:
        raise ValueError(f"Error processing mammogram images: {e}")

def preprocess_mri(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File {csv_path} does not exist.")
    try:
        df = pd.read_csv(csv_path)
        required_columns = [f'feature{i}' for i in range(1, 31)]  # 30 features
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"CSV missing required columns: {required_columns}")
        features = df[required_columns].values
        return features
    except Exception as e:
        raise ValueError(f"Error processing MRI CSV {csv_path}: {e}")