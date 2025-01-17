import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './DishResultsPage.css';


const DishResultsPage = ({ cartItems, setCartItems }) => {
    const { state } = useLocation(); // Access results and other params passed via navigate
    const { results, city, query } = state || {};
    const [quantities, setQuantities] = useState({});

    const navigate = useNavigate();

    if (!results || results.length === 0) {
        return <div>No dishes found for "{query}" in {city}.</div>;
    }

    const handleQuantityChange = (dishName, quantity) => {
        setQuantities((prevQuantities) => ({
            ...prevQuantities,
            [dishName]: quantity,
        }));
    };

    const handleAddToCart = (dish) => {
        const quantity = parseInt(quantities[dish.dish_name], 10);
        if (!quantity || quantity <= 0) {
            alert('Please enter a valid quantity.');
            return;
        }

        const updatedCart = [
            ...cartItems,
            {
                ...dish,
                quantity,
                city, // Add the city from the `DishResultsPage` state
            },
        ];
        setCartItems(updatedCart);
        alert(`${quantity} ${dish.dish_name}(s) added to cart.`);
    };

    return (
        <div className="dish-results-container">
            <h2>Dishes available for "{query}" in {city}</h2>
            <div className="dish-results-list">

                {results.map((dish, index) => (
                    <div key={index} className="dish-card">
                        <h3>{dish.dish_name}</h3>
                        <p>Vendor: {dish.vendor_name}</p>
                        <p>Restaurant: {dish.restaurant_name}</p>
                        <p>Price: ${dish.price.toFixed(2)}</p>
                        <p>Rating: {dish.rating} / 5</p>
                        <p>City Name: {city}</p>

                        <input
                            type="number"
                            placeholder="Quantity"
                            min="1"
                            value={quantities[dish.dish_name] || ''}
                            onChange={(e) => handleQuantityChange(dish.dish_name, e.target.value)}
                        />
                        <button onClick={() => handleAddToCart(dish)}>Add to Cart</button>
                    </div>
                ))}
            </div>
            <button className="go-to-cart" onClick={() => navigate('/cart')}>
                Go to Cart
            </button>
        </div>
    );
};

export default DishResultsPage;
