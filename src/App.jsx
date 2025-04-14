import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './components/Home';
import Analysis from './components/Analysis';
import About from './components/About';
import Model from './components/Model';
import './styles/App.css';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/about" element={<About />} />
          <Route path="/model" element={<Model />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
