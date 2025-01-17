import React from 'react';
import { useLocation } from 'react-router-dom';

const NaturalLanguageResultsPage = () => {
    const { state } = useLocation();

    const { globalResults, explainQueryOutput, query } = state || {};

    console.log(globalResults)
    return (
        <div>
            <h2>Results for: {query}</h2>
            <h3>Global Results:</h3>
            <ul>
                {globalResults.map((resultSet, idx) => (
                    <li key={idx}>
                        {resultSet.map(([dish, source]) => (
                            <div key={dish}>
                                {dish} - {source}
                            </div>
                        ))}
                    </li>
                ))}
            </ul>
            <h3>Explanation:</h3>
            <p>{explainQueryOutput}</p>
        </div>
    );
};

export default NaturalLanguageResultsPage;
