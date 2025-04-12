import React, { useState } from 'react';
import axios from 'axios';
import UploadForm from './components/UploadForm';
import LoadingScreen from './components/LoadingScreen';
import Results from './components/Results';
import './App.css';

const App = () => {
  const [modality, setModality] = useState('ultrasound');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [files, setFiles] = useState({});

  const handleFileChange = (e) => {
    setFiles({ ...files, [e.target.name]: e.target.files[0] });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResults(null);

    const formData = new FormData();
    Object.keys(files).forEach((key) => {
      if (files[key]) formData.append(key, files[key]);
    });

    try {
      let url = `http://192.168.137.1:8000/predict/${modality}`; // Update IP as needed
      if (modality === 'combined') {
        url = `http://192.168.137.1:8000/predict/combined`;
      }
      const response = await axios.post(
        url,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      setResults(response.data);
    } catch (error) {
      console.error('Prediction error:', error);
      alert('Error making prediction: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Breast Cancer Prediction</h1>
      <select onChange={(e) => {
        setModality(e.target.value);
        setFiles({}); // Reset files when switching modalities
      }} value={modality}>
        <option value="ultrasound">Ultrasound (Separate)</option>
        <option value="mammogram">Mammogram (Separate)</option>
        <option value="mri">MRI (Separate)</option>
        <option value="combined">Combined Prediction</option>
      </select>
      <UploadForm onSubmit={handleSubmit} modality={modality} onFileChange={handleFileChange} />
      {loading && <LoadingScreen />}
      <Results results={results} modality={modality} />
    </div>
  );
};

export default App;