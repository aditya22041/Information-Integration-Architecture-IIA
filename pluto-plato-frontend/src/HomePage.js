import React from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css'; // Create a CSS file for styling
import scooterImage from './Illustration1.png';
function HomePage() {
    const navigate = useNavigate();
  
    return (
      <div className="homepage-container">
        <div className="text-section">
          <h1>PlutoPlato</h1>
          <p>Your daily food price aggregator</p>
          <div className="button-group">
            <button onClick={() => navigate('/user')} className="nav-button">User</button>
            <button onClick={() => navigate('/admin')} className="nav-button">Admin</button>
          </div>
        </div>
        <div className="image-section">
          <img src={scooterImage} alt="Scooter" />
        </div>
      </div>
    );
  }
  
export default HomePage;