import mysql.connector
import groqllm
import naturalquery
global_schema = """
CREATE TABLE Restaurant (
    Restaurant_id INT PRIMARY KEY,
    Name VARCHAR(255),              
    Address VARCHAR(255), 
    City VARCHAR(100),              
    Zip VARCHAR(10),                
    Rating FLOAT,                   
    availability TINYINT
);
CREATE TABLE Dishes (
    dish_id INT PRIMARY KEY,
    Dishname VARCHAR(255),         
    price DECIMAL(10, 2),                    
    restaurant_id INT, 
    rating FLOAT,                  
    availability TINYINT,
    about TEXT,
    FOREIGN KEY (restaurant_id) REFERENCES Restaurant(Restaurant_id)
);
"""

def executetheorderhistor(query):
    orderhistory_conn = mysql.connector.connect(
    host="localhost",
    user="sqluser",
    password="password",
    database="orderhistory",
    auth_plugin='mysql_native_password'
    )
    try:
        orderhistory_conn.ping(reconnect=True)
        orderhistory_cursor = orderhistory_conn.cursor()
        orderhistory_cursor.execute(query)
        results = orderhistory_cursor.fetchall()
        orderhistory_cursor.close()
        return results
    except mysql.connector.Error as err:
        print(f"Error executing orderhistory query: {err}")
        print(f"Query that failed: {query}")
    return None
    
orderhistory="""
create database orderhistory;
use orderhistory;
CREATE TABLE OrderHistory (
    order_id BIGINT UNSIGNED NOT NULL,
    -- dish_id bigint unsigned default null ,
    -- restaurant_id INT unsigned default NULL ,
    vendor VARCHAR(255) default NULL,
    dish_name varchar(255),
    restaurant_name varchar(255),
    city varchar(255),
    quantity INT NOT NULL,
    total_price INT  default 0,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP
   -- FOREIGN KEY (dish_id) REFERENCES Dishes(id),
   -- FOREIGN KEY (restaurant_id) REFERENCES Restaurant(id)
);"""
def natural_language_for_admin(query):
    output = {}
    output["orderhistory"] = 0
    output["Restaurant&Dishes"] = 0
    output["explanation"] = "None"

    prompt1 = f"""given the query "{query}" and the order history database schema {orderhistory}, write a sqlquery to answer the query 
    without any explanation or assumption or alternate way strictly in the following fashion that your response can directly executed in SQL without any other word but the query in double quotes: "select columnname from orderhistory where condition;"
    """
    query = groqllm.generate_intelligent_query(prompt1)

    # Clean the string by removing extraneous double quotes and leading/trailing spaces
    cleaned_query = query.strip().replace('"', '')

    # Now print the cleaned query to verify
    print(f"Cleaned Query: {cleaned_query}")

    # Execute the cleaned query
    try:
        orderhistoryresult = executetheorderhistor(cleaned_query)
        output["orderhistory"] = orderhistoryresult
    except Exception as e:
        print(f"Error executing orderhistory query: {e}")
    res=naturalquery.give_response(query)
    output["Restaurant&Dishes"] = res['global_results']
    output["explanation"] = res['explain_query_output']
    return output

if __name__ == "__main__":
    natural_language_for_admin("show me all the orders")

