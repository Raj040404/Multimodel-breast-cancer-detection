import joblib
import numpy as np
from app.preprocess import CLASS_MAPPING

def predict_mri(data, model_path, quality_weight=0.4):
    try:
        model = joblib.load(model_path)
        prediction = model.predict_proba(data)
        max_prob = np.max(prediction, axis=1)[0]
        pred_class = np.argmax(prediction, axis=1)[0]
        
        results = [{
            "probability": float(max_prob),
            "class": int(pred_class),
            "class_label": CLASS_MAPPING.get(pred_class, f"Unknown Class {pred_class}")
        }]
        return {"results": results, "quality_weight": quality_weight, "model_name": "MRI"}
    except Exception as e:
        raise RuntimeError(f"Error predicting with model {model_path}: {e}")