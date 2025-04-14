import React from 'react';
import './styles/Model.css';

const Model = () => {
  return (
    <section className="model-section">
      <div className="model-container">
        <h2 className="section-title">Our Model</h2>
        
        <div className="model-visualization">
          <div className="model-animation">
            <div className="brain-container">
              <div className="brain">
                <div className="brain-lobe left"></div>
                <div className="brain-lobe right"></div>
                <div className="brain-lobe center"></div>
              </div>
              <div className="synapses">
                {[...Array(8)].map((_, i) => (
                  <div key={i} className="synapse"></div>
                ))}
              </div>
            </div>
            <div className="eeg-waves">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="wave"></div>
              ))}
            </div>
            <div className="music-notes">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="note"></div>
              ))}
            </div>
          </div>
          <a href="#" className="access-model-btn">
            Access Our Model
          </a>
        </div>

        <div className="model-stats">
          <div className="stat-card">
            <div className="stat-value">86%</div>
            <div className="stat-label">Model Accuracy</div>
            <div className="stat-description">
              Our deep learning model achieves high accuracy in predicting brain activity patterns
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Model; 