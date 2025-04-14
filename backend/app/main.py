from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import logging
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.preprocess import preprocess_ultrasound, preprocess_mammogram, preprocess_mri
from app.predict_ultrasound import predict_ultrasound
from app.predict_mammogram import predict_mammogram
from app.predict_mri import predict_mri
from app.preprocess import CLASS_MAPPING

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://192.168.137.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "data"

# SQLite Database Setup
DATABASE_URL = "sqlite:///" + str(BASE_DIR / "predictions.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    modality = Column(String, index=True)
    file_name = Column(String)
    probability = Column(Float)
    class_value = Column(String)
    class_label = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Create the table
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Use Depends for database injection
def get_database_session():
    return next(get_db())

@app.post("/predict/ultrasound")
async def predict_ultrasound_endpoint(file: UploadFile = File(...), db=Depends(get_database_session)):
    try:
        ultrasound_dir = UPLOAD_DIR / "ultrasound/images"
        ultrasound_dir.mkdir(parents=True, exist_ok=True)
        file_path = ultrasound_dir / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        images = preprocess_ultrasound(file_path)
        model1_path = BASE_DIR / "models/ultrasound/cnn_model1.h5"
        model2_path = BASE_DIR / "models/ultrasound/imagenet_model2.h5"
        
        pred1 = predict_ultrasound(images, model1_path, "CNN Model")
        pred2 = predict_ultrasound(images, model2_path, "ImageNet Model")
        
        # Store predictions in database
        for pred in [pred1, pred2]:
            db_prediction = Prediction(
                modality="ultrasound",
                file_name=file.filename,
                probability=pred["results"][0]["probability"],
                class_value=str(pred["results"][0]["class"]),
                class_label=pred["results"][0]["class_label"]
            )
            db.add(db_prediction)
        db.commit()

        return {"cnn_model": pred1, "imagenet_model": pred2}
    except Exception as e:
        logger.error(f"Ultrasound prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/mammogram")
async def predict_mammogram_endpoint(
    image: UploadFile = File(...),
    breast_mask: UploadFile = File(...),
    dense_mask: UploadFile = File(...),
    db=Depends(get_database_session)
):
    try:
        mammogram_dir = UPLOAD_DIR / "mammogram"
        img_path = mammogram_dir / "images" / image.filename
        breast_mask_path = mammogram_dir / "breast_mask" / breast_mask.filename
        dense_mask_path = mammogram_dir / "dense_mask" / dense_mask.filename
        
        for path in [img_path.parent, breast_mask_path.parent, dense_mask_path.parent]:
            path.mkdir(parents=True, exist_ok=True)
        
        with img_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        with breast_mask_path.open("wb") as buffer:
            shutil.copyfileobj(breast_mask.file, buffer)
        with dense_mask_path.open("wb") as buffer:
            shutil.copyfileobj(dense_mask.file, buffer)
        
        data = preprocess_mammogram(img_path, breast_mask_path, dense_mask_path)
        model_path = BASE_DIR / "models/mammogram/breast_cancer_model_mamogram.h5"
        mammogram_result = predict_mammogram(data, model_path)
        # Divide mammogram probability by 100
        mammogram_result["results"][0]["probability"] = min(1.0, max(0.0, mammogram_result["results"][0]["probability"] / 100.0))
        
        # Store prediction in database
        db_prediction = Prediction(
            modality="mammogram",
            file_name=image.filename,
            probability=mammogram_result["results"][0]["probability"],
            class_value=str(mammogram_result["results"][0]["class"]),
            class_label=mammogram_result["results"][0]["class_label"]
        )
        db.add(db_prediction)
        db.commit()

        return {"mammogram": mammogram_result}
    except Exception as e:
        logger.error(f"Mammogram prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/mri")
async def predict_mri_endpoint(file: UploadFile = File(...), db=Depends(get_database_session)):
    try:
        mri_dir = UPLOAD_DIR / "mri/uploads"
        mri_dir.mkdir(parents=True, exist_ok=True)
        file_path = mri_dir / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        data = preprocess_mri(file_path)
        model_path = BASE_DIR / "models/mri/mri_ensemble_model.pkl"
        mri_result = predict_mri(data, model_path)
        
        # Store prediction in database
        db_prediction = Prediction(
            modality="mri",
            file_name=file.filename,
            probability=mri_result["results"][0]["probability"],
            class_value=str(mri_result["results"][0]["class"]),
            class_label=mri_result["results"][0]["class_label"]
        )
        db.add(db_prediction)
        db.commit()

        return {"mri": mri_result}
    except Exception as e:
        logger.error(f"MRI prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/combined")
async def predict_combined(
    ultrasound_file: UploadFile = File(None),
    mammogram_image: UploadFile = File(None),
    mammogram_breast_mask: UploadFile = File(None),
    mammogram_dense_mask: UploadFile = File(None),
    mri_file: UploadFile = File(None),
    db=Depends(get_database_session)
):
    try:
        results = {}
        logger.info(f"Received files: ultrasound_file={ultrasound_file}, mammogram_image={mammogram_image}, "
                    f"mammogram_breast_mask={mammogram_breast_mask}, mammogram_dense_mask={mammogram_dense_mask}, "
                    f"mri_file={mri_file}")
        
        # Ultrasound
        if ultrasound_file:
            ultrasound_dir = UPLOAD_DIR / "ultrasound/images"
            ultrasound_dir.mkdir(parents=True, exist_ok=True)
            file_path = ultrasound_dir / ultrasound_file.filename
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(ultrasound_file.file, buffer)
            images = preprocess_ultrasound(file_path)
            model1_path = BASE_DIR / "models/ultrasound/cnn_model1.h5"
            model2_path = BASE_DIR / "models/ultrasound/imagenet_model2.h5"
            pred1 = predict_ultrasound(images, model1_path, "CNN Model", 0.15)
            pred2 = predict_ultrasound(images, model2_path, "ImageNet Model", 0.15)
            results["ultrasound_cnn"] = pred1
            results["ultrasound_imagenet"] = pred2
        
        # Mammogram
        if mammogram_image and mammogram_breast_mask and mammogram_dense_mask:
            mammogram_dir = UPLOAD_DIR / "mammogram"
            img_path = mammogram_dir / "images" / mammogram_image.filename
            breast_mask_path = mammogram_dir / "breast_mask" / mammogram_breast_mask.filename
            dense_mask_path = mammogram_dir / "dense_mask" / mammogram_dense_mask.filename
            for path in [img_path.parent, breast_mask_path.parent, dense_mask_path.parent]:
                path.mkdir(parents=True, exist_ok=True)
            with img_path.open("wb") as buffer:
                shutil.copyfileobj(mammogram_image.file, buffer)
            with breast_mask_path.open("wb") as buffer:
                shutil.copyfileobj(mammogram_breast_mask.file, buffer)
            with dense_mask_path.open("wb") as buffer:
                shutil.copyfileobj(mammogram_dense_mask.file, buffer)
            data = preprocess_mammogram(img_path, breast_mask_path, dense_mask_path)
            model_path = BASE_DIR / "models/mammogram/breast_cancer_model_mamogram.h5"
            mammogram_result = predict_mammogram(data, model_path, 0.3)
            mammogram_result["results"][0]["probability"] = min(1.0, max(0.0, mammogram_result["results"][0]["probability"] / 100.0))
            results["mammogram"] = mammogram_result
        
        # MRI
        if mri_file:
            mri_dir = UPLOAD_DIR / "mri/uploads"
            mri_dir.mkdir(parents=True, exist_ok=True)
            file_path = mri_dir / mri_file.filename
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(mri_file.file, buffer)
            data = preprocess_mri(file_path)
            model_path = BASE_DIR / "models/mri/mri_ensemble_model.pkl"
            mri_result = predict_mri(data, model_path, 0.4)
            results["mri"] = mri_result
        
        # Combine results if any modality is provided
        if results:
            combined_prob = 0.0
            total_weight = 0.0
            for modality, result in results.items():
                prob = result["results"][0]["probability"]
                weight = result["quality_weight"]
                combined_prob += prob * weight
                total_weight += weight
            
            final_prob = combined_prob / total_weight if total_weight > 0 else 0.0
            final_prob = min(1.0, max(0.0, final_prob))
            final_class = 1 if final_prob > 0.5 else 0
            combined_result = {
                "probability": float(final_prob),
                "class": int(final_class),
                "class_label": CLASS_MAPPING.get(final_class, f"Unknown Class {final_class}")
            }
            
            # Store combined result in database
            db_prediction = Prediction(
                modality="combined",
                file_name=(ultrasound_file.filename if ultrasound_file else mammogram_image.filename if mammogram_image else mri_file.filename if mri_file else "unknown"),
                probability=combined_result["probability"],
                class_value=str(combined_result["class"]),
                class_label=combined_result["class_label"]
            )
            db.add(db_prediction)
            db.commit()

            return {"individual_results": results, "combined_result": combined_result}
        return {"message": "No valid inputs provided"}
    except Exception as e:
        logger.error(f"Combined prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error making prediction: {str(e)}")

@app.get("/predictions")
async def get_predictions(db=Depends(get_database_session)):
    try:
        predictions = db.query(Prediction).all()
        return [
            {
                "id": p.id,
                "modality": p.modality,
                "file_name": p.file_name,
                "probability": p.probability,
                "class_value": p.class_value,
                "class_label": p.class_label,
                "timestamp": p.timestamp.isoformat()
            } for p in predictions
        ]
    except Exception as e:
        logger.error(f"Error fetching predictions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching predictions: {str(e)}")