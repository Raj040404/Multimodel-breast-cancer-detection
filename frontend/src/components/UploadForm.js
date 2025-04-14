import React from 'react';

const UploadForm = ({ onSubmit, modality, onFileChange, loading }) => {
  const titleCaseModality = modality.charAt(0).toUpperCase() + modality.slice(1);

  return (
    <form onSubmit={onSubmit} className="upload-form">
      <h2 className="title">{`${titleCaseModality} Prediction`}</h2>

      {modality === 'ultrasound' && (
        <label className="file-label">
          Ultrasound Image:
          <input
            type="file"
            name="file"
            accept="image/*"
            onChange={onFileChange}
            required
            className="file-input"
          />
        </label>
      )}

      {modality === 'mammogram' && (
        <>
          <label className="file-label">
            Mammogram Image:
            <input
              type="file"
              name="image"
              accept="image/*"
              onChange={onFileChange}
              required
              className="file-input"
            />
          </label>
          <label className="file-label">
            Breast Mask:
            <input
              type="file"
              name="breast_mask"
              accept="image/*"
              onChange={onFileChange}
              required
              className="file-input"
            />
          </label>
          <label className="file-label">
            Dense Mask:
            <input
              type="file"
              name="dense_mask"
              accept="image/*"
              onChange={onFileChange}
              required
              className="file-input"
            />
          </label>
        </>
      )}

      {modality === 'mri' && (
        <label className="file-label">
          MRI CSV:
          <input
            type="file"
            name="file"
            accept=".csv"
            onChange={onFileChange}
            required
            className="file-input"
          />
        </label>
      )}

      {modality === 'combined' && (
        <>
          <label className="file-label">
            Ultrasound Image (Optional):
            <input
              type="file"
              name="ultrasound_file"
              accept="image/*"
              onChange={onFileChange}
              className="file-input"
            />
          </label>
          <label className="file-label">
            Mammogram Image (Optional):
            <input
              type="file"
              name="mammogram_image"
              accept="image/*"
              onChange={onFileChange}
              className="file-input"
            />
          </label>
          <label className="file-label">
            Breast Mask (Optional):
            <input
              type="file"
              name="mammogram_breast_mask"
              accept="image/*"
              onChange={onFileChange}
              className="file-input"
            />
          </label>
          <label className="file-label">
            Dense Mask (Optional):
            <input
              type="file"
              name="mammogram_dense_mask"
              accept="image/*"
              onChange={onFileChange}
              className="file-input"
            />
          </label>
          <label className="file-label">
            MRI CSV (Optional):
            <input
              type="file"
              name="mri_file"
              accept=".csv"
              onChange={onFileChange}
              className="file-input"
            />
          </label>
        </>
      )}

      <button type="submit" className="predict-button" disabled={loading}>
        {loading ? 'Processing...' : 'Predict'}
      </button>
    </form>
  );
};

export default UploadForm;
