import React from 'react';

const LoadingScreen = () => {
  return (
    <div className="loading-container">
      <div className="loader"></div>
      <span className="loading-text">Processing...</span>
    </div>
  );
};

export default LoadingScreen;