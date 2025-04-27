InformationIntegrationProject-IIA-

📚 Overview
InformationIntegrationProject-IIA- is a course project for Information Integration and Analytics (IIA). The project focuses on integrating and analyzing information from various sources, particularly in the context of restaurants, dishes, and vendors. It aims to create a system that can process and unify data from different formats and sources, making it accessible and useful for applications like restaurant recommendations, menu analysis, and vendor management.Having following objective in a robust manner
(a)  Project Statement, Why you have chosen this project (Motivation, Importance, etc), and for whom you are building this II system (set of close-to-real applications, use-cases, stakeholders, and purpose), and focus on innovative application(s)/use-case(s)
(b) underlying data sources (Type of sources - relational/non-relation, etc, Schemas and/or APIs (input and output). Populating the data in these sources, what query execution support they have, how do they communicate with the Data Integration system (i.e. communication protocol)

(c) Defining the Data Integration System : Hybrid

(d) Schema matching and Mapping between Target and Sources 

(e)  Query Interface ,Query Federation, Execution and Results Integration 
(f)  Query Analyzer and Decomposer

(g)  Query federation and Execution-with load and traffic balancer

(h)  Aggregating the Results and Displaying the same

🧩 Backend Functionality
The backend, primarily written in Python, handles the core data processing and integration tasks. Key functionalities include:

Data Extraction:
Scripts like addpdf_llm.py and extract_dish_info.py extract relevant information from PDFs and other documents.

Entity Analysis:
Modules such as entityanalysis.py and docanalysis.py analyze text to identify entities like dish names, restaurant names, and vendor details.

Natural Language Processing:
Files like naturallanguageforadmin.py and naturalquery.py process natural language inputs, enabling users to query the system using everyday language.

Data Mapping and Integration:
algomapping.py and contextfromsql.py assist in mapping and integrating or deletion data from various sources into a unified format.

API Provisioning:
app.py sets up the web server and defines API routes for frontend consumption.

Caching:
.json files contain the cache and mets data for fast processing

Note:
You must define a global _Schema that must contain atleast two tables namely Restaurent and Dishes and add the data-base info like user-name and passowrd in global conn however datbases should be on same network however they can run different machines with diffent schemas 
🎨 Frontend Functionality
The frontend, located in the pluto-plato-frontend/ directory, is responsible for presenting the integrated data to users. Its functionalities include:

User Interface: Displays information about restaurants, dishes, and vendors in an organized manner.

Search and Query: Allows users to search for specific dishes or restaurants using natural language queries.

Interactive Elements: Provides interactive components for users to filter and sort data based on various criteria.

🚀 Getting Started
Prerequisites
Ensure you have the following installed on your system:

Python 3.8+

Node.js 14+

🔧 Backend Setup
Navigate to the backend directory:

bash
Copy
Edit
cd backend
(Optional) Create and activate a virtual environment:

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install the required Python packages:

bash
Copy
Edit
pip install -r requirements.txt
Run the backend server:

bash
Copy
Edit
python app.py  # Replace 'app.py' with the actual entry point if different
🎯 Frontend Setup
Navigate to the frontend directory:

bash
Copy
Edit
cd pluto-plato-frontend
Install the necessary Node.js packages:

bash
Copy
Edit
npm install
Start the frontend development server:

bash
Copy
Edit
npm start
🌐 Accessing the Application
Once both servers are running, open your web browser and navigate to:

arduino
Copy
Edit
http://localhost:3000
(or the port specified in your configuration)

✨ Features
Extraction of restaurant and dish information from semi-structured sources.

Natural language query support.

Data integration from multiple vendors.

User-friendly frontend interface.

🤝 Credits
This repository contains code created through the combined efforts of:

@aditya22041

@A-WASIF

@aastha1708

Uploaded with their permission, acknowledging their original contributions.
