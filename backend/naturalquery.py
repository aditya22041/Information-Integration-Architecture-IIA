import mysql.connector
import groqllm
import queryfederator
import re

# Define the global schema
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

# Prompt handling for natural language queries
def give_response(natural_language_query):
    prompt1 = f"""
    given this natural language query: {natural_language_query}
    and the global schema: {global_schema} please output a single SQL query that will return the desired results without any explanation or anything  like following please alway have tablename.attribute even in case of single table:    
    SELECT Restaurant.Name,Dishes.Dishname, Dishes.price FROM Restaurant JOIN Dishes ON Restaurant.Restaurant_id = Dishes.restaurant_id  WHERE Restaurant.City = New York  AND Dishes.availability = 1;
    else output just no without any explanation and anything else
    """

    # Generate intelligent query
    global_schema_query = groqllm.generate_intelligent_query(prompt1)

    # Clean and fix escaped characters
    global_schema_query = re.sub(r"\\_", "_", global_schema_query)
    
    print("Generated SQL Query:", global_schema_query)
    output={}
    # Execute the query
    global_results=queryfederator.fedquerywithvendor(global_schema_query)
    output['global_results']=global_results
    print("Global Results:", global_results)
    #print(global_results)
    # noofrows=len(global_results)
    noofrows=0
    if global_results:
        noofrows=len(global_results)
        if noofrows>7:
            global_results=global_results[:7]
    
    # # reduce the no of lists in orderhistory_results to max of 7
    # if len(orderhistory_results)>7:
    #     orderhistory_results=orderhistory_results[:7]

    #ask llm to explain the query and results and other info that it has
    explain_query_prompt = f"""
    the user gave the natural language query: {natural_language_query} and we got the following results:
    from global schema: {global_results} have  been limited to first 7 and had total of {noofrows} no of items so please explain these results and give info about the things mentioned in the query

    """
    explain_query_output = groqllm.generate_intelligent_query(explain_query_prompt)
    #print("Explanation:", explain_query_output)
    print("Explanation:", explain_query_output)
    output['explain_query_output']=explain_query_output

    print("Output:", output)
    return output


if __name__ == "__main__":
    # Example query
    give_response("show me all the dishes name which are available in the city of rome")
