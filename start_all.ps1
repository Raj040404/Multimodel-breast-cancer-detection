# start_all.ps1
Start-Process powershell -Verb RunAs -ArgumentList "-NoExit", "-Command", "cd 'C:\\Users\\91826\\projects\\breast_cancer_prediction\\backend'; .\\venv\\Scripts\\Activate.ps1; uvicorn app.main:app --host 0.0.0.0 --port 8000"
Start-Process powershell -Verb RunAs -ArgumentList "-NoExit", "-Command", "cd 'C:\\Users\\91826\\projects\\breast_cancer_prediction\\frontend'; npm start"