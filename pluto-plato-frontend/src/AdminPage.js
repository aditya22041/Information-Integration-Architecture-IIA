import React, { useState } from 'react';
import axios from 'axios';
import './AdminPage.css'; // Ensure the CSS file is in place
import groupImage from './admin.png'; // Admin image

const AdminPage = () => {
    const [query, setQuery] = useState('');
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');

    const handleQueryChange = (e) => {
        setQuery(e.target.value);
    };

    const handleQuerySubmit = async (e) => {
        e.preventDefault();
        try {
            // Making the API request
            const response = await axios.post('http://localhost:5000/api/nataralanguage_query_admin', { query });

            setResult(response.data);  // Storing the result in state
            setError('');
        } catch (err) {
            // Handle error scenario
            setError('An error occurred while fetching the results.');
        }
    };

    return (
        <div className="adminpage-container">
            <div className="button-section">
                <button className="admin-button">Manage Vendor</button>
                <button className="admin-button">Analysis</button>
                <button className="admin-button">Update Cache</button>
            </div>

            <div className="image-section">
                <img src={groupImage} alt="Admin" />
            </div>

            <div className="query-section">
                <h2>Admin Query Input</h2>
                <form onSubmit={handleQuerySubmit}>
                    <textarea
                        value={query}
                        onChange={handleQueryChange}
                        placeholder="Enter your query here"
                        rows="4"
                        cols="50"
                    />
                    <br />
                    <button type="submit" className="admin-button">Submit Query</button>
                </form>
            </div>

            {error && <div className="error-message">{error}</div>}

            {result && (
                <div className="result-section">
                    <h3>Query Result</h3>
                    <div className="result-table">
                        <h4>Order History</h4>
                        <pre>{JSON.stringify(result.orderhistory, null, 2)}</pre>

                        <h4>Restaurant & Dishes</h4>
                        <pre>{JSON.stringify(result["Restaurant&Dishes"], null, 2)}</pre>

                        <h4>Explanation</h4>
                        <pre>{result.explanation}</pre>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AdminPage;
