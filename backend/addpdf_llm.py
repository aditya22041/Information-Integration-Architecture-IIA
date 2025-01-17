import json
import google.generativeai as genai
import pymysql
import os
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import re

# Configure API key for Generative AI
genai.configure(api_key="AIzaSyC4GdJWSMVUFKqP3eH4d-v-2TxDpTTCdzU")  

# Database connection
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='sqluser',
        password='password',
        database='global_schema',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# Check if restaurant exists
def check_if_restaurant_exists(restaurant_name, city):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT Restaurant_id FROM Restaurant WHERE Name = %s AND City = %s"
            cursor.execute(sql, (restaurant_name, city))
            result = cursor.fetchone()
            if result:
                return result['Restaurant_id']
            else:
                return None
    finally:
        connection.close()

# Check if a dish already exists
def check_dish(restaurant_id, name):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT Dish_id FROM Dishes WHERE Restaurant_id = %s AND Dishname = %s"
            cursor.execute(sql, (restaurant_id, name))
            result = cursor.fetchone()
            return result is not None
    finally:
        connection.close()

# Insert restaurant
def insert_restaurant_data(restaurant_data):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = """
            INSERT INTO Restaurant (Name, Address, City, Zip, Rating, Availability)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                restaurant_data['Name'],
                restaurant_data['Address'],
                restaurant_data['City'],
                restaurant_data['Zip'],
                restaurant_data['Rating'],
                restaurant_data['Availability']
            ))
            connection.commit()
            return cursor.lastrowid
    except KeyError as e:
        print(f"KeyError: Missing key in restaurant data: {e}")
        return None
    except Exception as e:
        print(f"An error occurred while inserting restaurant data: {e}")
        return None
    finally:
        connection.close()

# Insert dish
def insert_into_dishes(restaurant_id, name, price, rating, about):
    connection = get_db_connection()
    try:
        if check_dish(restaurant_id, name):
            return  # Dish already exists
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO Dishes (Dishname, Price, Restaurant_id, Rating, About)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (name, price, restaurant_id, rating, about))
            connection.commit()
    finally:
        connection.close()

# Extract text from file
def get_text_from_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    if file_extension.lower() == '.txt':
        with open(file_path, 'r') as file:
            return file.read()
    elif file_extension.lower() == '.pdf':
        pages = convert_from_path(file_path, 500)
        text = ""
        for page in pages:
            text += pytesseract.image_to_string(page)
        return text
    elif file_extension.lower() in ['.png', '.jpg', '.jpeg']:
        return pytesseract.image_to_string(Image.open(file_path))
    else:
        raise ValueError("Unsupported file type")

# Process input file
def process_input_file():
    file_path = input("Enter the path to the input file (txt, pdf, or image): ")
    text = get_text_from_file(file_path)
    
    model = genai.GenerativeModel('gemini-pro')
    prompt = """
    Find the structured data from the following document:
    - Restaurant details (name, address, city, zip code, rating, availability)
    - Dishes with prices, ratings, and descriptions (if available)

    Provide the extracted data in the following format only so that it can be decoded as JSON:
    {
      "Restaurant": {
        "Name": "Example Name",
        "Address": "Example Address",
        "City": "Example City",
        "Zip": "12345",
        "Rating": 4.5,
        "Availability": 1
      },
      "Dishes": [
        {
          "Dishname": "Dish 1",
          "Price": 20.00,
          "Rating": 4.7,
          "About": "Description of Dish 1"
        },
        {
          "Dishname": "Dish 2",
          "Price": 15.00,
          "Rating": 4.2,
          "About": "Description of Dish 2"
        }
      ]
    }
    """
    prompt += text

    response = model.generate_content(prompt)
    print(response.text)
    structured_data = parse_response(response.text)
    
    if structured_data:
        restaurant_id = insert_restaurant_data(structured_data['restaurant'])
        if restaurant_id:
            insert_dish_data(restaurant_id, structured_data['dishes'])
            print("Data successfully inserted into the database.")
        else:
            print("Failed to insert restaurant data.")
    else:
        print("Failed to parse and insert data.")

# Parse response
def parse_response(response_text):
    try:
        response_text = response_text.strip()
        structured_data = json.loads(response_text)

        if 'Restaurant' not in structured_data or 'Dishes' not in structured_data:
            raise ValueError("Required 'Restaurant' or 'Dishes' key missing from structured data.")

        return {
            'restaurant': structured_data['Restaurant'],
            'dishes': structured_data['Dishes']
        }
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error parsing the response: {e}")
        return None

# Insert dish data
def insert_dish_data(restaurant_id, dishes):
    for dish in dishes:
        insert_into_dishes(
            restaurant_id,
            dish['Dishname'],
            dish['Price'],
            dish['Rating'],
            dish.get('About', '')
        )

if __name__ == "__main__":
    process_input_file()