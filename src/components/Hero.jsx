import React from 'react';
import { Link } from 'react-router-dom';
import './styles/Hero.css';

const Hero = () => {
  return (
    <section className="hero" id="home">
      <div className="hero-background">
        <div className="gradient-overlay"></div>
        <div className="animated-waves"></div>
      </div>
      <div className="hero-content">
        <div className="hero-text">
          <h1 className="hero-title">
            Understanding Music's Impact on Brain Activity
          </h1>
          <p className="hero-subtitle">
            Advanced EEG analysis revealing the profound connection between music and neural responses
          </p>
          <div className="hero-buttons">
            <Link to="/analysis" className="cta-button primary">Explore Analysis</Link>
            <Link to="/model" className="cta-button secondary">View Model</Link>
          </div>
        </div>
        <div className="hero-visual">
          <div className="brain-waves">
            <div className="wave"></div>
            <div className="wave"></div>
            <div className="wave"></div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero; 