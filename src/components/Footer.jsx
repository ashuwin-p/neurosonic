import React from 'react';
import { Link } from 'react-router-dom';
import './styles/Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-section">
          <h3>Neurosonic</h3>
          <p>Analyzing the impact of music on brain activity through EEG signals.</p>
        </div>
        <div className="footer-section">
          <h4>Quick Links</h4>
          <ul>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/analysis">Analysis</Link></li>
            <li><Link to="/model">Model</Link></li>
            <li><Link to="/about">About Us</Link></li>
          </ul>
        </div>
        <div className="footer-section">
          <h4>Connect With Us</h4>
          <div className="social-links">
            <a href="#" className="social-link">
              <i className="fab fa-github"></i>
              <span>GitHub</span>
            </a>
            <a href="#" className="social-link">
              <i className="fab fa-linkedin"></i>
              <span>LinkedIn</span>
            </a>
          </div>
        </div>
      </div>
      <div className="footer-bottom">
        <p>&copy; 2025 Neurosonic. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default Footer; 