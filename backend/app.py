from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import mysql.connector
app = Flask(__name__)
CORS(app)
# import naturalquery
import extract_dish_info

# Route to serve the current city name
@app.route('/api/curr_city_name', methods=['GET'])
def curr_city_name():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'curr_city_name.json')

        with open(file_path) as f:
            data = json.load(f)
        return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({"message": "File not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"message": "Error decoding JSON"}), 500



# Search Dish Endpoint
@app.route('/api/search_dish', methods=['POST'])
def search_dish():
    # Parse request data from front end
    data = request.json
    city_name = data.get('city_name')
    dish_name = data.get('query')  # Assuming 'query' refers to the dish name
    # param = data.get('param')  # Optional: 'price' or 'rating'
    # order = data.get('order', 'asc')  # Default to ascending order


    # Validate mandatory fields
    if not city_name or not dish_name:
        return jsonify({"message": "City name and dish query are required"}), 400

    try:
        # Call the sort_and_print_dishes function and capture the results
        print("Infos : ", city_name, dish_name)

        results = extract_dish_info.sort_and_print_dishes(dish_name, city_name)
        
        if not results:
            return jsonify({"message": "No results found for the given query"}), 404

        # Return the results to the front end
        return jsonify({"results": results}), 200

    except Exception as e:
        # Handle exceptions and return a meaningful error response
        return jsonify({"message": "An error occurred while processing your request", "error": str(e)}), 500

import mysql

# Set up the database connection
global_conn = mysql.connector.connect(
    host="localhost",
    user="sqluser",
    password="password",
    database="orderhistory",
    auth_plugin="mysql_native_password",
)

# Create a cursor to interact with the database
cursor = global_conn.cursor()

# Function to insert order history into the database
def execute_order_history(cart_items, order_id):
    print(type(cart_items))
    try:
        # Prepare the SQL query to insert data
        for item in cart_items:
            print(item)
            cursor.execute("""
                INSERT INTO OrderHistory (
                    order_id, vendor, dish_name, restaurant_name, 
                    city, quantity, total_price, order_date
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                order_id, 
                item['vendor_name'],  # Assuming the front end sends vendor_name
                item['dish_name'], 
                item['restaurant_name'], 
                item['city'], 
                item['quantity'], 
                item['quantity'] * item['price']
            ))
        # Commit the transaction to the database
        global_conn.commit()
        return True
    except mysql.connector.Error as err:
        # Rollback in case of an error
        global_conn.rollback()
        print("Error: ", err)
        return False

@app.route('/api/Order_cart', methods=['POST'])
def Order_cart():
    try:
        # Get the cart data from the request
        data = request.json
        
        # Ensure the data contains the necessary information
        if not data or 'cart_items' not in data or not data['cart_items']:
            return jsonify({"message": "No cart data provided"}), 400
        
        cart_items = data['cart_items']
        
        # Generate a new order_id (for simplicity, you could generate this dynamically)
        cursor.execute("SELECT MAX(order_id) FROM OrderHistory")
        result = cursor.fetchone()
        order_id = (result[0] + 1) if result[0] is not None else 1

        # Insert the cart data into the database
        if execute_order_history(cart_items, order_id):
            return jsonify({
                "message": f"Order placed successfully with Order ID {order_id}",
                "order_id": order_id
            }), 200
        else:
            return jsonify({"message": "Failed to place order"}), 500
    
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500



import show_restaurant
@app.route('/api/search_restaurant', methods=['POST'])
def search_restaurant():
    data = request.json
    city_name = data.get('city_name')
    restaurant_name = data.get('query')

    print(city_name, restaurant_name)

    if not city_name or not restaurant_name:
        return jsonify({"message": "City name and restaurant query are required"}), 400

    try:
        restaurant_query = """
         SELECT `Restaurant`.`restaurant_id`, `Restaurant`.`Name`, `Restaurant`.`Address`, `Restaurant`.`City`, 
           `Restaurant`.`Rating`, `Restaurant`.`availability`
            FROM `Restaurant`
            WHERE `Restaurant`.`City` = '{CITY_NAME}' AND `Restaurant`.`Name` = '{RESTAURANT_NAME}';
        """

        # Call the function to fetch and format results
        results = show_restaurant.print_table_for_query(restaurant_query, city_name, restaurant_name)
        
        if not results:
            return jsonify({"message": "No results found for the given query"}), 404

        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while processing your request", "error": str(e)}), 500


import extract_dish_for_vendors_restaurant
@app.route('/api/get_dishes_by_restaurant_and_city', methods=['POST'])
def get_dishes_by_restaurant_and_city():
    data = request.json
    print("data", data.get('restaurant_name'), data.get('city_name'), data.get('vendor_name'))
    
    output = extract_dish_for_vendors_restaurant.get_dishes_by_restaurant_and_city(
        data.get('restaurant_name'), 
        data.get('city_name'), 
        data.get('vendor_name')
    )

    print(output)

    return jsonify(output), 200


import naturalquery
# Natural Language Query Endpoint
@app.route('/api/natural_language_query', methods=['POST'])
def natural_language_query():
    data = request.json
    query = data.get('query')

    if not query:
        return jsonify({"message": "query are required"}), 400
    query+="consider that this is being asked by the user and not by admin"
    response=naturalquery.give_response(query)

    print(response)

    return jsonify(response), 200



import naturallanguageforadmin
@app.route('/api/nataralanguage_query_admin',methods=['POST'])
def natural_language_query_admin():
    
    data=request.json
    query=data.get('query')
    print(query)    
    response=naturallanguageforadmin.natural_language_for_admin(query)
    print("response from backend",response)
    return jsonify(response),200

if __name__ == '__main__':
    app.run(debug=True)
