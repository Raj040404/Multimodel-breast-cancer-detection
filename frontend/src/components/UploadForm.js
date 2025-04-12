import React from 'react';

const UploadForm = ({ onSubmit, modality, onFileChange }) => {
  return (
    <form onSubmit={onSubmit} className="upload-section">
      <h2>{modality.charAt(0).toUpperCase() + modality.slice(1)} Prediction</h2>
      {modality === 'ultrasound' && (
        <label>
          Ultrasound Image:
          <input type="file" name="file" accept="image/*" onChange={onFileChange} required />
        </label>
      )}
      {modality === 'mammogram' && (
        <>
          <label>
            Mammogram Image:
            <input type="file" name="image" accept="image/*" onChange={onFileChange} required />
          </label>
          <label>
            Breast Mask:
            <input type="file" name="breast_mask" accept="image/*" onChange={onFileChange} required />
          </label>
          <label>
            Dense Mask:
            <input type="file" name="dense_mask" accept="image/*" onChange={onFileChange} required />
          </label>
        </>
      )}
      {modality === 'mri' && (
        <label>
          MRI CSV:
          <input type="file" name="file" accept=".csv" onChange={onFileChange} required />
        </label>
      )}
      {modality === 'combined' && (
        <>
          <label>
            Ultrasound Image (Optional):
            <input type="file" name="ultrasound_file" accept="image/*" onChange={onFileChange} />
          </label>
          <label>
            Mammogram Image (Optional):
            <input type="file" name="mammogram_image" accept="image/*" onChange={onFileChange} />
          </label>
          <label>
            Breast Mask (Optional):
            <input type="file" name="mammogram_breast_mask" accept="image/*" onChange={onFileChange} />
          </label>
          <label>
            Dense Mask (Optional):
            <input type="file" name="mammogram_dense_mask" accept="image/*" onChange={onFileChange} />
          </label>
          <label>
            MRI CSV (Optional):
            <input type="file" name="mri_file" accept=".csv" onChange={onFileChange} />
          </label>
        </>
      )}
      <button type="submit">Predict</button>
    </form>
  );
};

export default UploadForm;