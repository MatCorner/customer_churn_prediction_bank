# customer_churn_prediction_bank

A web-based banking platform designed for **customers** and **bank managers**, with integrated **machine learning churn prediction**.

This project provides both **core banking functions** (account management, transactions) and **predictive analytics** to help identify at-risk customers.

---

# Features

# Customer Features
- Register & log in securely (JWT authentication)
- Create and manage accounts
- Deposit, withdraw, and transfer money
- View transaction history
- Automatically ranked based on account balance

# Manager Features
- View all customers and accounts
- See churn-risk predictions
- Get insights from behavioral and demographic data

---

# Tech Stack

| Layer | Technology |
|--------|-------------|
| Backend | Python (Flask) |
| Database | SQLite / MariaDB (via SQLAlchemy) |
| Authentication | JWT (JSON Web Token) |
| Machine Learning | Scikit-learn |
| Frontend (optional) | HTML, React, or Vue.js |

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
Server will start at: http://127.0.0.1:5000/

# API Endpoints

| Method | Endpoint             | Description                      |
| ------ | -------------------- | -------------------------------- |
| POST   | `/api/auth/signup`   | Register new user                |
| POST   | `/api/auth/signin`   | Login and get JWT token          |
| GET    | `/api/customers/`    | Get all customers (JWT required) |
| POST   | `/api/transactions/` | Create a transaction             |

# uthentication

All protected endpoints require a JWT token in the request header:
Authorization: Bearer <your_token_here>

You can get your token by logging in through:
POST /api/auth/signin