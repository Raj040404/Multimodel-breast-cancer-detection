import numpy as np
import tensorflow as tf
from app.preprocess import CLASS_MAPPING

def predict_ultrasound(images, model_path, model_name="Model", quality_weight=0.15):
    try:
        model = tf.keras.models.load_model(model_path)
        predictions = model.predict(images)
        max_prob = np.max(predictions, axis=1)
        pred_class = np.argmax(predictions, axis=1)
        
        results = [
            {
                "image": i+1,
                "probability": float(prob),
                "class": int(cls),
                "class_label": CLASS_MAPPING.get(cls, f"Unknown Class {cls}")
            }
            for i, (prob, cls) in enumerate(zip(max_prob, pred_class))
        ]
        return {"results": results, "quality_weight": quality_weight, "model_name": model_name}
    except Exception as e:
        raise RuntimeError(f"Error predicting with model {model_path}: {e}")