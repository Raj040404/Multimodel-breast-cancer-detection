```bash
# Clone the repository
git clone https://github.com/your-username/breast-cancer-prediction.git
cd breast-cancer-prediction

# Set up the backend
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Ensure model files are placed in the correct paths:
# backend/models/ultrasound/cnn_model1.h5
# backend/models/ultrasound/imagenet_model2.h5
# backend/models/mammogram/breast_cancer_model_mamogram.h5
# backend/models/mri/mri_ensemble_model.pkl

# Start the FastAPI backend
cd backend/app
uvicorn main:app --host 0.0.0.0 --port 8000
# (Keep this running or run it in the background using `&` if needed)

# Open a new terminal and set up the frontend
cd ../../../frontend
npm install
npm start
or
.\start_all.ps1
```

