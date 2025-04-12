import numpy as np
import tensorflow as tf
from app.preprocess import CLASS_MAPPING

def predict_mammogram(data, model_path, quality_weight=0.3):
    try:
        model = tf.keras.models.load_model(model_path, compile=False)
        prediction = model.predict(data)
        max_prob = np.max(prediction, axis=1)[0]
        pred_class = np.argmax(prediction, axis=1)[0]
        
        results = [{
            "probability": float(max_prob),
            "class": int(pred_class),
            "class_label": CLASS_MAPPING.get(pred_class, f"Unknown Class {pred_class}")
        }]
        return {"results": results, "quality_weight": quality_weight, "model_name": "Mammogram"}
    except Exception as e:
        raise RuntimeError(f"Error predicting with model {model_path}: {e}")