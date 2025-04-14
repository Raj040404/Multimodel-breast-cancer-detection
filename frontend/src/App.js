import React, { useState, useEffect } from 'react';
import axios from 'axios';
import UploadForm from './components/UploadForm';
import Results from './components/Results';
import LoadingScreen from './components/LoadingScreen';
import './App.css';
import stethoscope from './assets/stethoscope.jpg';
import heartbeat from './assets/heartbeat.png';

function App() {
  const [modality, setModality] = useState('ultrasound');
  const [files, setFiles] = useState({});
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [predictions, setPredictions] = useState([]);

  const handleModalityChange = (e) => {
    setModality(e.target.value);
    setFiles({});
    setResults(null);
    setError(null);
  };

  const handleFileChange = (e) => {
    setFiles({ ...files, [e.target.name]: e.target.files[0] });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    const formData = new FormData();
    Object.keys(files).forEach((key) => {
      if (files[key]) formData.append(key, files[key]);
    });

    try {
      let url = `http://192.168.137.1:8000/predict/${modality}`;
      if (modality === 'combined') {
        url = `http://192.168.137.1:8000/predict/combined`;
      }

      const response = await axios.post(url, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      if (
        response.data &&
        typeof response.data === 'object' &&
        ('type' in response.data || 'loc' in response.data || 'msg' in response.data || 'input' in response.data)
      ) {
        throw new Error(
          Array.isArray(response.data)
            ? response.data.map(e => e.msg).join('; ')
            : response.data.msg || 'Invalid input'
        );
      }

      if (
        !response.data.individual_results &&
        !response.data.combined_result &&
        modality !== 'combined' &&
        !Object.values(response.data).some(r => r.results)
      ) {
        throw new Error('Unexpected response format');
      }

      setResults(response.data);
      // Fetch updated predictions after successful prediction
      fetchPredictions();
    } catch (error) {
      const apiError = error.response?.data;
      if (Array.isArray(apiError)) {
        setError(apiError);
      } else {
        setError(apiError?.detail || apiError?.msg || error.message || 'An error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchPredictions = async () => {
    try {
      const response = await axios.get('http://192.168.137.1:8000/predictions');
      setPredictions(response.data);
    } catch (error) {
      console.error('Error fetching predictions:', error);
      setError('Failed to fetch predictions');
    }
  };

  useEffect(() => {
    fetchPredictions(); // Fetch predictions on initial load
  }, []);

  return (
    <div className="app-container">
      <nav className="navbar">
        <ul className="nav-list">
          <li><a href="#home">Home</a></li>
          <li><a href="#predict">Predict</a></li>
          <li><a href="#about">About</a></li>
          <li><a href="#history">History</a></li>
        </ul>
      </nav>

      <div className="content" id="home">
        <img src={stethoscope} alt="Medical Theme" className="hero-image" />
        <h1 className="title">Breast Cancer Prediction</h1>

        <p style={{ fontSize: '16px', marginBottom: '20px', lineHeight: '1.6' }}>
          Breast cancer is one of the most common cancers affecting women worldwide. Early detection
          and diagnosis significantly increase the chances of successful treatment. Our platform allows
          you to upload diagnostic images such as ultrasound, mammogram, and MRI scans to assist in
          breast cancer detection. Please consult a healthcare professional for a complete diagnosis.
        </p>

        <div className="modality-select">
          <label>Select Modality:</label>
          <select value={modality} onChange={handleModalityChange} className="modality-dropdown">
            <option value="ultrasound">Ultrasound</option>
            <option value="mammogram">Mammogram</option>
            <option value="mri">MRI</option>
            <option value="combined">Combined</option>
          </select>
        </div>

        <UploadForm
          modality={modality}
          onFileChange={handleFileChange}
          onSubmit={handleSubmit}
          loading={loading}
        />

        {loading && <LoadingScreen />}

        {error && (
          <div className="error">
            {Array.isArray(error)
              ? error.map((e, idx) => <p key={idx}>{e.msg}</p>)
              : <p>{error}</p>}
          </div>
        )}

        {results && <Results results={results} modality={modality} />}
        <div className="heartbeat-icon" style={{ backgroundImage: `url(${heartbeat})` }}></div>
      </div>

      <div className="content" id="about">
        <h2 className="subtitle">Precautions & Awareness</h2>
        <ul style={{ fontSize: '16px', lineHeight: '1.6' }}>
          <li>Perform regular self-examinations and report any changes to a doctor.</li>
          <li>Schedule regular mammograms based on age and risk factors.</li>
          <li>Maintain a healthy weight and lifestyle to reduce cancer risks.</li>
          <li>Avoid smoking and limit alcohol consumption.</li>
          <li>Know your family history and discuss genetic testing if necessary.</li>
          <li>Stay informed and encourage others to be proactive about their health.</li>
        </ul>
      </div>

      <div className="content" id="history">
        <h2 className="subtitle">Prediction History</h2>
        {predictions.length > 0 ? (
          <table className="prediction-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Modality</th>
                <th>File Name</th>
                <th>Probability</th>
                <th>Class</th>
                <th>Label</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {predictions.map((pred) => (
                <tr key={pred.id}>
                  <td>{pred.id}</td>
                  <td>{pred.modality}</td>
                  <td>{pred.file_name}</td>
                  <td>{pred.probability.toFixed(6)}</td>
                  <td>{pred.class_value}</td>
                  <td>{pred.class_label}</td>
                  <td>{new Date(pred.timestamp).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No predictions recorded yet.</p>
        )}
      </div>
    </div>
  );
}

export default App;