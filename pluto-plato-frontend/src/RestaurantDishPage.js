import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./RestaurantDishPage.css";

const RestaurantDishPage = () => {
  const { state } = useLocation();
  const { restaurant_name, city_name, vendor_name } = state || {};

  const [dishes, setDishes] = useState([]);
  const [quantities, setQuantities] = useState({});
  const [cart, setCart] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDishes = async () => {
      try {
        const response = await fetch(
          "http://localhost:5000/api/get_dishes_by_restaurant_and_city",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              restaurant_name,
              city_name,
              vendor_name,
            }),
          }
        );

        if (!response.ok) throw new Error(`Error: ${response.status}`);
        const data = await response.json();
        setDishes(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error("Error fetching dishes:", error.message);
      }
    };

    if (restaurant_name && city_name && vendor_name) {
      fetchDishes();
    }
  }, [restaurant_name, city_name, vendor_name]);

  const handleQuantityChange = (dishName, value) => {
    setQuantities((prev) => ({
      ...prev,
      [dishName]: value,
    }));
  };

  const handleAddToCart = (dish) => {
    const quantity = parseInt(quantities[dish.Dishname], 10);
    if (!quantity || quantity <= 0) {
      alert("Please enter a valid quantity.");
      return;
    }

    const existingItemIndex = cart.findIndex(
      (item) => item.Dishname === dish.Dishname && item.city === city_name
    );

    if (existingItemIndex !== -1) {
      const updatedCart = [...cart];
      updatedCart[existingItemIndex] = {
        ...updatedCart[existingItemIndex],
        quantity: updatedCart[existingItemIndex].quantity + quantity,
      };
      setCart(updatedCart);
    } else {
      setCart([
        ...cart,
        {
          ...dish,
          quantity,
          city: city_name,
          vendor_name, // Add vendor_name here
        },
      ]);
    }

    alert(`${quantity} ${dish.Dishname}(s) added to cart.`);
  };

  const goToCart = () => {
    console.log(cart);
    if (cart.length === 0) {
      alert("Your cart is empty!");
      return;
    }
    // Pass vendor_name with the cart
    navigate("/dup_cart", { state: { cart, vendor_name } });
  };

  return (
    <div className="dish-results-container">
      <h2>Dishes available for "{restaurant_name}" in {city_name}</h2>
      {dishes.length > 0 ? (
        <div className="dish-results-list">
          {dishes.map((dish, index) => (
            <div key={index} className="dish-card">
              <h3>{dish.Dishname}</h3>
              <p>Restaurant: {dish.RestaurantName}</p>
              <p>Price: ₹{dish.Price.toFixed(2)}</p>
              <p>Rating: {dish.Rating} / 5</p>
              <p>City: {dish.City}</p>
              <p>Available: {dish.Availability ? "Yes" : "No"}</p>

              <input
                type="number"
                placeholder="Quantity"
                min="1"
                value={quantities[dish.Dishname] || ""}
                onChange={(e) =>
                  handleQuantityChange(dish.Dishname, e.target.value)
                }
              />
              <button onClick={() => handleAddToCart(dish)}>Add to Cart</button>
            </div>
          ))}
        </div>
      ) : (
        <p>No dishes found for this restaurant.</p>
      )}

      <button className="go-to-cart" onClick={goToCart}>
        Go to Cart
      </button>
    </div>
  );
};

export default RestaurantDishPage;
