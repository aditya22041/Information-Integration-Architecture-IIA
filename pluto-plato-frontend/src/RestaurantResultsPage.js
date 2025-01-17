import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './RestaurantResultsPage.css';

const RestaurantResultsPage = () => {
  const { state } = useLocation();
  let results = state?.results || '[]';  // Default to empty string if no results
  const city = state?.city || '';
  console.log("Results Type: ", typeof(results));  // Check if it's a string
  console.log("Results Length: ", results.length);

  // If results is a string, parse it into an array
  if (typeof results === 'string') {
    try {
      results = JSON.parse(results);  // Parse string to array
    } catch (error) {
      console.error("Error parsing results: ", error);
      results = [];  // Set to empty array if parsing fails
    }
  }

  // Create table rows manually using a loop
  const rows = [];
  const navigate = useNavigate();
  for (let i = 0; i < results.length; i++) {
    const restaurant = results[i];
    rows.push(
      <tr key={i}>
        <td>{restaurant.name}</td>
        <td>{restaurant.city}</td>
        <td>{restaurant.rating}</td>
        <td>{restaurant.address}</td>
        <td>{restaurant.vendor_name}</td>
        <td>
          <button
            onClick={() =>
              navigate('/restaurant-dishes', {
                state: {
                  restaurant_name: restaurant.name,
                  city_name: restaurant.city,
                  vendor_name: restaurant.vendor_name,
                },
              })
            }
          >
            View Dishes
          </button>
        </td>
      </tr>
    );
  }

  return (
    <div className="results-container">
      <h2>Restaurants in {city}</h2>
      {results.length > 0 ? (
        <table className="results-table">
          <thead>
            <tr>
              <th>Restaurant Name</th>
              <th>City</th>
              <th>Rating</th>
              <th>Address</th>
              <th>Vendor Name</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </table>
      ) : (
        <p>No restaurants found for your query.</p>
      )}
      {/* Button to go back to the previous page */}
      <button onClick={() => navigate(-1)} className="back-button">
        Go Back
      </button>
    </div>
  );
};

export default RestaurantResultsPage;
