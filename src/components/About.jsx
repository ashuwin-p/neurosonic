import React, { useState } from 'react';
import './styles/About.css';

const About = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle form submission here
    console.log('Form submitted:', formData);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <section className="about-section">
      <div className="about-container">
        <h2 className="section-title">About Us</h2>
        
        <div className="team-section">
          <h3>Our Team</h3>
          <div className="team-grid">
            <div className="team-member">
              <div className="member-info">
                <h4>Dr. V. Durgadevi</h4>
                <p className="designation">Assistant Professor</p>
                <p className="department">Department of Information Technology</p>
                <p className="institution">SSN College of Engineering</p>
                <a href="mailto:durgadeviv@ssn.edu.in" className="email">
                  <i className="fas fa-envelope"></i> durgadeviv@ssn.edu.in
                </a>
              </div>
            </div>

            <div className="team-member">
              <div className="member-info">
                <h4>Ashuwin P</h4>
                <p className="department">Department of Information Technology</p>
                <p className="institution">SSN College of Engineering</p>
                <a href="mailto:ashuwin2210335@ssn.edu.in" className="email">
                  <i className="fas fa-envelope"></i> ashuwin2210335@ssn.edu.in
                </a>
              </div>
            </div>

            <div className="team-member">
              <div className="member-info">
                <h4>Ananya Sivakumar</h4>
                <p className="department">Department of Information Technology</p>
                <p className="institution">SSN College of Engineering</p>
                <a href="mailto:ananya2210316@ssn.edu.in" className="email">
                  <i className="fas fa-envelope"></i> ananya2210316@ssn.edu.in
                </a>
              </div>
            </div>
          </div>
        </div>

        <div className="contact-section">
          <h3>Contact Us</h3>
          <form onSubmit={handleSubmit} className="contact-form">
            <div className="form-group">
              <input
                type="text"
                name="name"
                placeholder="Your Name"
                value={formData.name}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <input
                type="email"
                name="email"
                placeholder="Your Email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <input
                type="text"
                name="subject"
                placeholder="Subject"
                value={formData.subject}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <textarea
                name="message"
                placeholder="Your Message"
                value={formData.message}
                onChange={handleChange}
                required
              ></textarea>
            </div>
            <button type="submit" className="submit-button">Send Message</button>
          </form>
        </div>
      </div>
    </section>
  );
};

export default About; 