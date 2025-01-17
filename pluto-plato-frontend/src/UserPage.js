import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./UserPage.css";
import cityImage from "./city.png";
import searchIcon from "./search-icon.svg";

const UserPage = () => {
    const [city, setCity] = useState("");
    const [suggestedCity, setSuggestedCity] = useState("");
    const [showSuggestion, setShowSuggestion] = useState(false);
    const [cityMeta, setCityMeta] = useState(null);
    const [error, setError] = useState(""); // For the "We don’t offer services" case
    const navigate = useNavigate();

    useEffect(() => {
        // Load city data from the Flask API
        fetch("http://localhost:5000/api/curr_city_name")
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => setCityMeta(data))
            .catch((error) => {
                console.error("Error loading city data:", error);
                setError("Failed to load city data. Please try again later.");
            });
    }, []);

    const calculateEditDistance = (a, b) => {
        const dp = Array.from({ length: a.length + 1 }, () =>
            Array(b.length + 1).fill(0)
        );
        for (let i = 0; i <= a.length; i++) dp[i][0] = i;
        for (let j = 0; j <= b.length; j++) dp[0][j] = j;
        for (let i = 1; i <= a.length; i++) {
            for (let j = 1; j <= b.length; j++) {
                dp[i][j] = Math.min(
                    dp[i - 1][j] + 1, // Deletion
                    dp[i][j - 1] + 1, // Insertion
                    dp[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1) // Substitution
                );
            }
        }
        return dp[a.length][b.length];
    };

    const handleSearch = () => {
        if (city && cityMeta) {
            const matchedCity = Object.keys(cityMeta).find((key) => {
                const variations = cityMeta[key];
                if (variations.includes(city)) return key;
                return calculateEditDistance(city.toLowerCase(), key.toLowerCase()) < 3;
            });

            if (matchedCity) {
                if (matchedCity.toLowerCase() === city.toLowerCase()) {
                    // Exact match: navigate to SearchPage
                    navigate("/search", { state: { city: matchedCity } });
                } else {
                    // Suggestion
                    setSuggestedCity(matchedCity);
                    setShowSuggestion(true);
                    setError("");
                }
            } else {
                // No match: error message
                setError("We don’t offer services in this city.");
                setShowSuggestion(false);
            }
        }
    };

    const handleSuggestionResponse = (response) => {
        if (response) {
            navigate("/search", { state: { city: suggestedCity } });
        } else {
            setCity("");
        }
        setShowSuggestion(false);
    };

    return (
        <div className="userpage-container">
            <h2>Enter your city to proceed:</h2>
            <div className="search-bar">
                <input
                    type="text"
                    placeholder="Enter city name"
                    className="city-input"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                />
                <button onClick={handleSearch} className="search-button">
                    <img src={searchIcon} alt="Search" />
                </button>
            </div>
            <div className="image-section">
                <img src={cityImage} alt="City Skyline" />
            </div>

            {showSuggestion && (
                <div className="suggestion-popup">
                    <p>Do you mean {suggestedCity}?</p>
                    <button onClick={() => handleSuggestionResponse(true)}>Yes</button>
                    <button onClick={() => handleSuggestionResponse(false)}>No</button>
                </div>
            )}

            {error && <p className="error-message">{error}</p>}
        </div>
    );
};

export default UserPage;