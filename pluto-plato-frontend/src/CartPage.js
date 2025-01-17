import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./CartPage.css";

const CartPage = ({ cartItems, onPlaceOrder }) => {
    const navigate = useNavigate();
    const location = useLocation();

    const [selectedCity, setSelectedCity] = useState(location.state?.city || (cartItems[0]?.city || ''));
    const [cart, setCart] = useState(cartItems || []);
    const [orderMessage, setOrderMessage] = useState("");
    const [orderId, setOrderId] = useState(null); // Track the order ID

    useEffect(() => {
        if (location.state?.city) {
            setSelectedCity(location.state.city);
        }
    }, [location.state]);

    const calculateTotal = () => {
        return cart.reduce((total, item) => total + item.quantity * item.price, 0).toFixed(2);
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
                        dish_name: item.dish_name,
                        city: item.city,
                        restaurant_name: item.restaurant_name,
                        quantity: item.quantity,
                        price: item.price,
                    })),
                }),
            });

            const data = await response.json();

            if (response.ok) {
                setOrderMessage(`Order placed successfully! Your total is ₹${totalAmount}`);
                setOrderId(data.order_id); // Store the order ID
                setCart([]); // Clear local cart
                onPlaceOrder(); // Clear global cart via parent
            } else {
                setOrderMessage(`Failed to place order: ${data.message}`);
            }
        } catch (error) {
            setOrderMessage(`Error placing order: ${error.message}`);
        }
    };

    return (
        <div className="cart-container">
            <h2>Your Cart for {selectedCity}</h2>
            {cart.length > 0 ? (
                <div className="cart-items">
                    {cart.map((item, index) => (
                        <div className="cart-item" key={index}>
                            <h4>{item.dish_name}</h4>
                            <p>Restaurant: {item.restaurant_name}</p>
                            <p>Vendor: {item.vendor_name}</p>
                            <p>Quantity: {item.quantity}</p>
                            <p>Price per Item: ₹{item.price}</p>
                            <p>Total: ₹{(item.quantity * item.price).toFixed(2)}</p>
                        </div>
                    ))}
                </div>
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
                    {orderId && <p>Order ID: <strong>{orderId}</strong></p>} {/* Display order ID */}
                    <button onClick={() => navigate("/user")} className="continue-button">
                        Continue Shopping
                    </button>
                </div>
            )}
        </div>
    );
};

export default CartPage;
