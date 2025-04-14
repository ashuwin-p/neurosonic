import React, { useState } from 'react';
import './styles/Analysis.css';
import Loader from './Loader';

const Analysis = () => {
  const [beforeMusic, setBeforeMusic] = useState(null);
  const [duringMusic, setDuringMusic] = useState(null);
  const [afterMusic, setAfterMusic] = useState(null);
  const [uploadStatus, setUploadStatus] = useState({
    before: false,
    during: false,
    after: false
  });
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedBand, setSelectedBand] = useState('alpha');
  const [selectedCondition, setSelectedCondition] = useState('before');

  const handleFileChange = (e, type) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type !== 'text/csv') {
        setError('Please upload a CSV file');
        return;
      }
      switch (type) {
        case 'before':
          setBeforeMusic(file);
          setUploadStatus(prev => ({ ...prev, before: true }));
          break;
        case 'during':
          setDuringMusic(file);
          setUploadStatus(prev => ({ ...prev, during: true }));
          break;
        case 'after':
          setAfterMusic(file);
          setUploadStatus(prev => ({ ...prev, after: true }));
          break;
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!beforeMusic || !duringMusic || !afterMusic) {
      setError('Please upload all three files');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('before_music', beforeMusic);
    formData.append('during_music', duringMusic);
    formData.append('after_music', afterMusic);

    try {
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError('Error analyzing EEG data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const bands = ['delta', 'theta', 'alpha', 'beta', 'gamma'];
  const conditions = ['before', 'during', 'after'];

  return (
    <section className="analysis-section">
      <div className="analysis-container">
        <h2 className="section-title">EEG Signal Analysis</h2>
        <p className="section-subtitle">
          Upload your EEG data files to analyze brain activity patterns
        </p>

        <form onSubmit={handleSubmit} className="upload-form">
          <div className="upload-grid">
            <div className="upload-card">
              <h3>Before Music</h3>
              <div className="upload-area">
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => handleFileChange(e, 'before')}
                  className="file-input"
                  id="before-input"
                />
                <label htmlFor="before-input" className="upload-label">
                  <span className="upload-icon">
                    <i className="fas fa-file-csv"></i>
                    <span className="eeg-indicator">EEG</span>
                  </span>
                  <span className="file-name">
                    {beforeMusic ? beforeMusic.name : 'Upload CSV file'}
                  </span>
                </label>
              </div>
            </div>

            <div className="upload-card">
              <h3>During Music</h3>
              <div className="upload-area">
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => handleFileChange(e, 'during')}
                  className="file-input"
                  id="during-input"
                />
                <label htmlFor="during-input" className="upload-label">
                  <span className="upload-icon">
                    <i className="fas fa-file-csv"></i>
                    <span className="eeg-indicator">EEG</span>
                  </span>
                  <span className="file-name">
                    {duringMusic ? duringMusic.name : 'Upload CSV file'}
                  </span>
                </label>
              </div>
            </div>

            <div className="upload-card">
              <h3>After Music</h3>
              <div className="upload-area">
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => handleFileChange(e, 'after')}
                  className="file-input"
                  id="after-input"
                />
                <label htmlFor="after-input" className="upload-label">
                  <span className="upload-icon">
                    <i className="fas fa-file-csv"></i>
                    <span className="eeg-indicator">EEG</span>
                  </span>
                  <span className="file-name">
                    {afterMusic ? afterMusic.name : 'Upload CSV file'}
                  </span>
                </label>
              </div>
            </div>
          </div>

          <button
            type="submit"
            className="analyze-button"
            disabled={loading || !beforeMusic || !duringMusic || !afterMusic}
          >
            {loading ? (
              <Loader />
            ) : (
              'Analyze Signals'
            )}
          </button>
        </form>

        {error && <div className="error-message">{error}</div>}

        {results && (
          <div className="results-section">
            <h3>Analysis Results</h3>

            {/* Raw EEG Plots */}
            <div className="raw-eeg-section">
              <h4>Raw EEG Signals</h4>
              <div className="plot-grid">
                {conditions.map((condition) => (
                  <div key={condition} className="plot-card">
                    <h5>{condition.charAt(0).toUpperCase() + condition.slice(1)} Music</h5>
                    <img
                      src={`data:image/png;base64,${results.raw_plots[condition]}`}
                      alt={`Raw EEG - ${condition}`}
                      className="analysis-plot"
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* PSD Plots */}
            <div className="psd-section">
              <h4>Power Spectral Density</h4>
              <div className="plot-grid">
                {conditions.map((condition) => (
                  <div key={condition} className="plot-card">
                    <h5>{condition.charAt(0).toUpperCase() + condition.slice(1)} Music</h5>
                    <img
                      src={`data:image/png;base64,${results.psd_plots[condition]}`}
                      alt={`PSD - ${condition}`}
                      className="analysis-plot"
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Interactive Band Selection */}
            <div className="band-selection">
              <h4>Select Frequency Band</h4>
              <div className="band-buttons">
                {bands.map((band) => (
                  <button
                    key={band}
                    className={`band-button ${selectedBand === band ? 'active' : ''}`}
                    onClick={() => setSelectedBand(band)}
                  >
                    {band.charAt(0).toUpperCase() + band.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* Topographic Maps */}
            <div className="topomap-section">
              <h4>Topographic Maps</h4>
              <div className="plot-grid">
                {conditions.map((condition) => (
                  <div key={condition} className="plot-card">
                    <h5>{condition.charAt(0).toUpperCase() + condition.slice(1)} Music</h5>
                    <img
                      src={`data:image/png;base64,${results.topomaps[selectedBand][condition]}`}
                      alt={`${selectedBand} Band Topography - ${condition}`}
                      className="analysis-plot"
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Band Power Comparison */}
            <div className="band-powers-section">
              <h4>Band Power Comparison</h4>
              <div className="band-powers-grid">
                <div className="band-power-card">
                  <img
                    src={`data:image/png;base64,${results.band_powers[selectedBand]}`}
                    alt={`${selectedBand} Band Power Comparison`}
                    className="band-power-plot"
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default Analysis; 