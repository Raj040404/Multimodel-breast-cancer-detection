import React from 'react';

const Results = ({ results, modality }) => {
  // Return null if no results are provided or if it's an error object
  if (!results || 
      (typeof results === 'object' && 
       ('type' in results || 'loc' in results || 'msg' in results || 'input' in results || 'detail' in results))) {
    return null;
  }

  // Render individual results for a given modality and result object
  const renderIndividualResults = (modalityKey, result) => {
    if (!result || !result.results) return null;

    return (
      <div key={modalityKey} className="result-item">
        <h3 className="subtitle">
          {result.model_name ? `${result.model_name} Results` : `${modalityKey.replace(/_/g, ' ').toUpperCase()} Results`}
        </h3>
        {result.results.map((res, idx) => (
          <p key={idx} className="result-text">
            {modalityKey.startsWith('ultrasound') ? `Image ${res.image || idx + 1}: ` : ''}
            Probability = {res.probability.toFixed(6)}, Class = {res.class} ({res.class_label})
          </p>
        ))}
      </div>
    );
  };

  return (
    <div className="results-container">
      <h2 className="results-title">Prediction Results</h2>
      {modality === 'combined' && results.individual_results && (
        <>
          {Object.entries(results.individual_results).map(([modKey, result]) =>
            renderIndividualResults(modKey, result)
          )}
          {results.combined_result && (
            <div className="combined-result">
              <h3 className="subtitle">Combined Result</h3>
              <p className="result-text">
                Probability = {results.combined_result.probability.toFixed(6)}, 
                Class = {results.combined_result.class} ({results.combined_result.class_label})
              </p>
            </div>
          )}
        </>
      )}
      {modality !== 'combined' && results && (
        Object.entries(results).map(([modKey, result]) =>
          renderIndividualResults(modKey, result)
        )
      )}
    </div>
  );
};

export default Results;