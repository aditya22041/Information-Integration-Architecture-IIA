import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import React, { useState } from 'react';
import HomePage from './HomePage';
import UserPage from './UserPage';
import AdminPage from './AdminPage';
import SearchPage from './SearchPage';
import CartPage from './CartPage';
import DishResultsPage from './DishResultsPage'; // Import the DishResultsPage component
import RestaurantResultsPage from "./RestaurantResultsPage";
import RestaurantDishPage from './RestaurantDishPage';
import DupCartPage from "./Dup_CartPage";
import NaturalLanguageResultsPage from './NaturalLanguageResults';

function App() {
  const [cartItems, setCartItems] = useState([]);

  const handlePlaceOrder = (orders) => {
    console.log('Order placed:', orders); // Log orders or integrate with the backend API
    setCartItems([]); // Clear the cart after placing the order
  };

  const handleAddQuery = () => {
    alert('Natural Language Query feature coming soon!');
  };

  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/user" element={<UserPage />} />
        <Route path="/admin" element={<AdminPage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/restaurant_results" element={<RestaurantResultsPage />} />
        <Route path="/restaurant-dishes" element={<RestaurantDishPage />} />
        <Route path="/NaturalLanguageResultsPage" element={<NaturalLanguageResultsPage />} />
        <Route path="/dup_cart" element={<DupCartPage />} />
        <Route
          path="/cart"
          element={
            <CartPage
              cartItems={cartItems}
              onPlaceOrder={handlePlaceOrder}
              onAddQuery={handleAddQuery}
            />
          }
        />
        <Route
          path="/dish_results"
          element={
            <DishResultsPage cartItems={cartItems} setCartItems={setCartItems} />
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
