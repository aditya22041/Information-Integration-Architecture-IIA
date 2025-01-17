import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './SearchPage.css';
import forksImage from './food.png';
import searchIcon from './search-icon.svg';

const SearchPage = () => {
    const { state } = useLocation();
    const navigate = useNavigate();

    // Extract the city name passed from UserPage
    const cityName = state?.city || '';

    const [query, setQuery] = useState('');
    const [searchType, setSearchType] = useState('restaurant');

    const handleSearch = async () => {
        if (!query) {
            alert('Please enter a search query!');
            return;
        }

        // Skip city validation for natural queries
        if (searchType !== 'natural' && !cityName) {
            alert('City name is missing! Please go back and select a city.');
            return;
        }

        // Define the API endpoint based on search type
        const apiEndpoint =
            searchType === 'restaurant'
                ? '/api/search_restaurant' // Restaurant search endpoint
                : searchType === 'dish'
                ? '/api/search_dish' // Dish search endpoint
                : '/api/natural_language_query'; // Natural language query endpoint

        // Prepare the request body
        const requestBody =
            searchType === 'natural'
                ? { query } // Only send the query for natural language queries
                : { city_name: cityName, query }; // Include city for restaurant/dish searches

        try {
            // Make the API request
            const response = await fetch(`http://localhost:5000${apiEndpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody),
            });

            const data = await response.json();

            if (response.ok) {
                // Navigate to the appropriate results page based on search type
                if (searchType === 'restaurant') {
                    navigate('/restaurant_results', { state: { results: data.results, city: cityName, query } });
                } else if (searchType === 'dish') {
                    navigate('/dish_results', { state: { results: data.results, city: cityName, query } });
                } else if (searchType === 'natural') {
                    navigate('/NaturalLanguageResultsPage', {
                        state: {
                            globalResults: data.global_results, // Extract the global results
                            explainQueryOutput: data.explain_query_output, // Extract the explanation
                            query, // Pass the user query
                        },
                    });
                }
                
            } else {
                alert(data.message || 'An error occurred while searching.');
            }
        } catch (error) {
            console.error('Error during search:', error);
            alert('Failed to perform the search. Please try again later.');
        }
    };

    return (
        <div className="searchpage-container">
            <h2 className="search-heading">Search for any dish or restaurant in {cityName || 'your selected location'}</h2>

            <div className="search-options">
                <label>
                    <input
                        type="radio"
                        name="searchType"
                        value="restaurant"
                        checked={searchType === 'restaurant'}
                        onChange={(e) => setSearchType(e.target.value)}
                    />
                    Search Restaurant
                </label>
                <label>
                    <input
                        type="radio"
                        name="searchType"
                        value="dish"
                        checked={searchType === 'dish'}
                        onChange={(e) => setSearchType(e.target.value)}
                    />
                    Search Dish
                </label>
                <label>
                    <input
                        type="radio"
                        name="searchType"
                        value="natural"
                        checked={searchType === 'natural'}
                        onChange={(e) => setSearchType(e.target.value)}
                    />
                    Natural Language Query
                </label>
            </div>

            <div className="search-bar">
                <input
                    type="text"
                    placeholder="Enter search query"
                    className="search-input"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                />
                <button onClick={handleSearch} className="search-button">
                    <img src={searchIcon} alt="Search" />
                </button>
            </div>

            <div className="image-section">
                <img src={forksImage} alt="Forks Illustration" />
            </div>
        </div>
    );
};

export default SearchPage;
