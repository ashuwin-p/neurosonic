import React from 'react';
import './styles/Loader.css';

const Loader = () => {
  return (
    <div className="loader-container">
      <div className="brain-loader">
        <div className="brain">
          <div className="brain-lobe left"></div>
          <div className="brain-lobe right"></div>
          <div className="brain-lobe center"></div>
        </div>
        <div className="synapses">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="synapse"></div>
          ))}
        </div>
      </div>
      <div className="loader-text">Analyzing EEG Data</div>
      <div className="loader-progress">
        <div className="progress-bar"></div>
      </div>
    </div>
  );
};

export default Loader; 