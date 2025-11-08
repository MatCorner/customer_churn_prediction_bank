customer_churn_prediction_bank/      # Project root
│
├── churn_app/                       # Your app
│   ├── migrations/
│   ├── models.py                    # Database models
│   ├── views.py                     # Controllers (handle requests)
│   ├── urls.py                      # Routes (maps URL -> views)
│   └── serializers.py               # Convert models <-> JSON
│
├── config/                          # Project config
│   ├── settings.py
│   └── urls.py                      # Project-level routes
│
├── static/                           # Optional: front-end static files
├── templates/                        # Optional: front-end HTML templates
├── db.sqlite3                        # Database (if using SQLite)
├── manage.py
└── README.md
