import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./CartPage.css";

const CartPage = ({ onPlaceOrder }) => {
    const navigate = useNavigate();
    const location = useLocation();

    // Retrieve cart and city from location state or fallback to empty/defaults
    const initialCart = location.state?.cart || [];
    const initialCity = location.state?.city || (initialCart[0]?.city || "");

    const [selectedCity, setSelectedCity] = useState(initialCity);
    const [cart, setCart] = useState(initialCart);
    const [orderMessage, setOrderMessage] = useState("");
    console.log("Carrrr", cart);

    useEffect(() => {
        // Update city and cart if location state changes
        if (location.state?.city) {
            setSelectedCity(location.state.city);
        }
        if (location.state?.cart) {
            setCart(location.state.cart);
        }
    }, [location.state]);

    const calculateTotal = () => {
        return cart
            .reduce((total, item) => total + item.quantity * item.Price, 0)
            .toFixed(2);
    };

    const handlePlaceOrder = async () => {
        if (cart.length === 0) {
            alert("Your cart is empty! Please add items to the cart.");
            return;
        }

        const totalAmount = calculateTotal();

        try {
            const response = await fetch("http://localhost:5000/api/Order_cart", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    cart_items: cart.map((item) => ({
                        vendor_name: item.vendor_name,
                        dish_name: item.Dishname,
                        city: item.city,
                        restaurant_name: item.RestaurantName,
                        quantity: item.quantity,
                        price: item.Price,
                    })),
                }),
            });

            const data = await response.json();

            if (response.ok) {
                setOrderMessage(`Order placed successfully! Your total is ₹${totalAmount}`);
                setCart([]); // Clear local cart
                onPlaceOrder && onPlaceOrder(); // Optional: clear global cart if parent prop exists
            } else {
                setOrderMessage(`Failed to place order: ${data.message}`);
            }
        } catch (error) {
            setOrderMessage(`Error placing order: ${error.message}`);
        }
    };

    const renderCartItems = () => {
        const items = [];
        for (let i = 0; i < cart.length; i++) {
            const item = cart[i];
            console.log(item)
            items.push(
                <div className="cart-item" key={i}>
                    <h4>{item.Dishname}</h4>
                    <p>Restaurant: {item.RestaurantName}</p>
                    <p>Vendor: {item.vendor_name}</p>
                    <p>Quantity: {item.quantity}</p>
                    <p>Price per Item: ₹{item.Price}</p>
                    <p>Total: ₹{(item.quantity * item.Price).toFixed(2)}</p>
                </div>
            );
        }
        return items;
    };

    return (
        <div className="cart-container">
            <h2>Your Cart for {selectedCity}</h2>
            {cart.length > 0 ? (
                <div className="cart-items">{renderCartItems()}</div>
            ) : (
                <p>Your cart is empty!</p>
            )}

            {cart.length > 0 && (
                <div className="cart-footer">
                    <h3>Final Total: ₹{calculateTotal()}</h3>
                    <button onClick={handlePlaceOrder} className="place-order-button">
                        Place Order
                    </button>
                </div>
            )}

            {orderMessage && (
                <div className="order-message">
                    <p>{orderMessage}</p>
                    <button onClick={() => navigate("/user")} className="continue-button">
                        Continue Shopping
                    </button>
                </div>
            )}
        </div>
    );
};

export default CartPage;
