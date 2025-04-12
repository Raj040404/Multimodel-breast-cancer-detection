import React from 'react';

const Results = ({ results, modality }) => {
  if (!results) return null;

  const renderIndividualResults = (modality, result) => {
    if (!result) return null;
    return (
      <div key={modality}>
        <h3>{result.model_name} Results</h3>
        {result.results.map((res, idx) => (
          <p key={idx}>
            {modality.startsWith('ultrasound') ? `Image ${res.image}: ` : ''}Probability = {res.probability.toFixed(6)}, 
            Class = {res.class} ({res.class_label})
          </p>
        ))}
      </div>
    );
  };

  return (
    <div className="results">
      <h2>Prediction Results</h2>
      {modality === 'combined' && results.individual_results && (
        <>
          {Object.entries(results.individual_results).map(([mod, result]) =>
            renderIndividualResults(mod, result)
          )}
          {results.combined_result && (
            <>
              <h3>Combined Result</h3>
              <p>
                Probability = {results.combined_result.probability.toFixed(6)}, 
                Class = {results.combined_result.class} ({results.combined_result.class_label})
              </p>
            </>
          )}
        </>
      )}
      {modality !== 'combined' && results && (
        Object.entries(results).map(([mod, result]) =>
          renderIndividualResults(mod, result)
        )
      )}
    </div>
  );
};

export default Results;