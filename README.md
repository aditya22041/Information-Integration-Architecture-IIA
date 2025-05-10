# Pluto Plato 

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Node.js](https://img.shields.io/badge/Node.js-14%2B-green?style=for-the-badge&logo=node.js)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Contributions](https://userpic.codeforces.org/3401002/title/bd7983885a6d2c6.jpg)

---

## 📚 Overview

**Pluto plato** Information Integration Application (IIA) course project: end-to-end ETL pipelines, schema matching, federated SQL querying, and AI-driven analytics for restaurant/vendor data. Built with Python, React, and LLM-powered natural-language interfaces.  
The project focuses on integrating and analyzing information from various sources, particularly in the context of restaurants, dishes, and vendors.  
It aims to create a system that can **process and unify data from different formats and sources**, making it accessible and useful for:

- Restaurant recommendations
- Menu analysis
- Vendor management

The project has the following robust objectives:

---

### 🧠 Objectives

- **(a) Project Statement**:  
  Motivation: To create a scalable and dynamic system for real-world applications.  
  Importance: Enhances data accessibility and utility for stakeholders such as restaurant owners, vendors, and end-users.  
  Target Users: Restaurants, food delivery apps, vendors, and foodies.  
  Focus: Innovative applications like real-time menu analytics and vendor comparison systems.

- **(b) Underlying Data Sources**:  
  - Type: Relational databases (MySQL)  
  - Schemas/APIs: Well-defined schemas for structured data exchange  
  - Data Population: Populated via extraction scripts and document analysis  
  - Communication Protocols: Standard SQL and REST APIs

- **(c) Defining the Data Integration System**:  
  - Approach: **Hybrid** — combines structured integration with AI-based enhancements.

- **(d) Schema Matching and Mapping**:  
  - Smart mapping between a **global schema** (with `Restaurant` and `Dishes` tables) and different vendor-specific schemas.

- **(e) Query Interface, Query Federation, Execution, and Result Integration**:  
  - Allowing federated query execution across databases with result integration.

- **(f) Query Analyzer and Decomposer**:  
  - Breaks down complex queries for optimized and efficient execution.

- **(g) Query Federation with Load and Traffic Balancer**:  
  - Efficient load distribution across databases to minimize latency.

- **(h) Aggregating and Displaying Results**:  
  - Merging, ranking, and presenting results seamlessly on the frontend.

---

## 🧩 Backend Functionality

The backend, primarily written in **Python**, handles core data processing and integration tasks.

### Major Components:

- **Data Extraction**:  
  `addpdf_llm.py`, `extract_dish_info.py` — extract restaurant and dish information from semi-structured sources like PDFs in context of a given sql query.

- **Entity Analysis**:  
  `entityanalysis.py`, `docanalysis.py` — identify entities such as dish names, restaurant names, and vendors in context of a fiven sql query.

- **Natural Language Processing**:  
  `naturallanguageforadmin.py`, `naturalquery.py` — process natural language queries from users/admins.

- **Data Mapping and Integration**:  
  `algomapping.py`, `contextfromsql.py` — unify data by mapping different schemas, support addition and deletion.

- **API Provisioning**:  
  `app.py` — defines and exposes backend routes for frontend consumption.

- **Caching**:  
  `.json` files — store intermediate cache and metadata for faster processing.

### Important Note

- Define a **global schema** containing at least two tables:  
  `Restaurant` and `Dishes`.
- Add database connection info (user, password) in a global connection config.
- Databases must be on the **same network** (can be on **different machines** and **different schemas**).

---

## 🎨 Frontend Functionality

Located in the `pluto-plato-frontend/` directory, the frontend is built using **React.js** and offers:

- **User Interface**:  
  Displays restaurant, dish, and vendor data cleanly and intuitively.

- **Search and Query Support**:  
  Users can search restaurants or dishes using **natural language**.

- **Interactive Elements**:  
  Filter, sort, and navigate easily using dynamic UI components.

---

## 🚀 Getting Started

### Prerequisites

Ensure you have installed:

- **[Python 3.8+](https://www.python.org/downloads/)**
- **[Node.js 14+](https://nodejs.org/en/download/)**

---

### 🔧 Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the backend server:
   ```bash
   python app.py  # (or the appropriate entry point)
   ```

---

### 🎯 Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd pluto-plato-frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

---

### 🌐 Accessing the Application

Open your browser and visit:

```
http://localhost:3000
```

(or the port specified in your configuration)

---

## ✨ Features

- 🔍 Extraction of restaurant and dish information from semi-structured sources
- 🗣️ Natural language query support
- 🔗 Data integration across multiple vendors
- 🖥️ User-friendly frontend interface
- ⚡ Fast caching and smart query decomposition
- 🔄 Federated query processing and load balancing

---

## 🤝 Credits

This repository contains code created through the combined efforts of:

- [@aditya22041](https://github.com/aditya22041)
- [@A-WASIF](https://github.com/A-WASIF)
- [@aastha1708](https://github.com/aastha1708)

> Uploaded with their permission, acknowledging their original contributions. 🚀
