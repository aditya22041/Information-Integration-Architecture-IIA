import pandas as pd
import pymysql
from sklearn.feature_extraction.text import TfidfVectorizer
import re

# Connect to MySQL database
def connect_to_mysql():
    return pymysql.connect(
        host='localhost',
        user='sqluser',
        password='password',
        db='orderhistory',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# Run SQL query and return results as a DataFrame
def run_query(query, connection):
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    return pd.DataFrame(result)

# Automatically generate the unselected query by inverting the WHERE clause or excluding selected values
def generate_unselected_query(selected_query, selected_df):
    # Find the position of the WHERE clause if it exists
    where_index = selected_query.upper().find("WHERE")
    
    # List the original grouping columns only (non-aggregated columns)
    grouping_columns = [col for col in selected_df.columns if col not in ["total_orders", "latest_order_date", "avg_price"]]
    grouping_columns_str = ", ".join(grouping_columns)
    
    if where_index == -1:
        # If no WHERE clause, construct exclusion conditions for each unique value of the key column
        base_query = selected_query.split("GROUP BY")[0]
        key_column = selected_df.columns[0]
        exclude_values = selected_df[key_column].unique()
        exclusion_conditions = " AND ".join([f"{key_column} != '{val}'" for val in exclude_values])
        unselected_query = f"{base_query} WHERE {exclusion_conditions} GROUP BY {grouping_columns_str}"
    
    else:
        # If there is a WHERE clause, invert conditions and group by the original columns
        base_query = selected_query[:where_index]
        where_clause = selected_query[where_index + len("WHERE "):]
        conditions = re.split(r"\s+AND\s+|\s+OR\s+", where_clause, flags=re.IGNORECASE)
        inverted_conditions = [f"NOT ({cond.strip()})" for cond in conditions]
        unselected_where_clause = " AND ".join(inverted_conditions)
        unselected_query = f"{base_query} WHERE {unselected_where_clause} GROUP BY {grouping_columns_str}"
    
    return unselected_query


# Remove overlapping tuples from unselected results
def remove_overlapping_tuples(selected_df, unselected_df):
    unselected_df = unselected_df[~unselected_df.isin(selected_df)].dropna()
    return unselected_df

# Process data using TF-IDF for categorical and numeric differences, handling all detected columns
def analyze_differences(selected_df, unselected_df):
    explanations = {}
    significant_columns = []
    
    for column in selected_df.columns:
        if pd.api.types.is_numeric_dtype(selected_df[column]):
            # Numeric processing
            selected_mean = selected_df[column].mean()
            unselected_mean = unselected_df[column].mean()
            difference = selected_mean - unselected_mean
            explanations[column] = f"Selected results have a higher average {column}: {difference:.2f} more than unselected."
            significant_columns.append(column)

        elif pd.api.types.is_datetime64_any_dtype(selected_df[column]):
            # Date processing
            selected_date = selected_df[column].max()  # Latest date in selected
            unselected_date = unselected_df[column].max()
            date_difference = selected_date - unselected_date
            explanations[column] = f"Selected results are more recent, with the latest date being {selected_date} compared to {unselected_date}."
            significant_columns.append(column)

        elif pd.api.types.is_string_dtype(selected_df[column]):
            # Categorical processing
            combined_series = pd.concat([selected_df[column], unselected_df[column]], axis=0).fillna("")
            labels = [1] * len(selected_df) + [0] * len(unselected_df)
            
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(combined_series)
            terms = vectorizer.get_feature_names_out()
            
            selected_tfidf = tfidf_matrix[:len(selected_df)].mean(axis=0).A1
            unselected_tfidf = tfidf_matrix[len(selected_df):].mean(axis=0).A1
            tfidf_diff = selected_tfidf - unselected_tfidf
            
            top_indices = tfidf_diff.argsort()[-5:][::-1]  # Consider top 5 terms for better context
            top_terms = [(terms[i], tfidf_diff[i]) for i in top_indices if tfidf_diff[i] > 0.1]
            
            if top_terms:
                explanations[column] = ", ".join([f"{term} (Score: {score:.2f})" for term, score in top_terms])
                significant_columns.append(column)
    
    return explanations, significant_columns

# Main function to execute the explanation process
def main_explanation_query(selected_query):
    
    connection = connect_to_mysql()
    
    try:
        selected_df = run_query(selected_query, connection)
        
        unselected_query = generate_unselected_query(selected_query, selected_df)
        print(f"Generated Unselected Query:\n{unselected_query}")
        
        unselected_df = run_query(unselected_query, connection)
        unselected_df = remove_overlapping_tuples(selected_df, unselected_df)
        
        explanations, significant_columns = analyze_differences(selected_df, unselected_df)
        
        print("\nSelected Query Results:")
        print(selected_df)
        print("\nUnselected Query Results:")
        print(unselected_df)
        print("\nExplanation for why the selected results differ from the rest:\n")
        for column in significant_columns:
            print(f"{column} (Reason): {explanations.get(column, 'No specific reason identified')}")
    
    finally:
        connection.close()

# Run the explanation process
main_explanation_query(selected_query = """
    SELECT restaurant_name, vendor, dish_name, SUM(quantity) AS total_orders, MAX(order_date) AS latest_order_date, AVG(total_price) AS avg_price
    FROM OrderHistory
    GROUP BY restaurant_name, vendor, dish_name
    ORDER BY total_orders DESC
    LIMIT 3;
    """)
