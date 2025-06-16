📄 README.md
markdown
Copy
Edit
# Flask Test App

This is a simple Flask-based web application that includes user authentication, role-based access, test creation, and test-taking functionality.

## 🚀 Features

- User registration and login with secure password hashing
- Admin dashboard for:
  - Creating questions
  - Creating tests by selecting questions
  - Editing and viewing tests
  - Viewing user scores
  - Promoting/demoting users
- Users can:
  - Attempt each test only once
  - View their scores
- MySQL database integration using `Flask-MySQLdb`
- Clean and simple HTML templates

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS (basic)
- **Database:** MySQL
- **Tools:** VS Code, phpMyAdmin

## ⚙️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/navya906/flask_test_app.git
   cd flask_test_app
Create a virtual environment and activate it

bash
Copy
Edit
python -m venv venv
venv\Scripts\activate   # On Windows
Install dependencies

bash
Copy
Edit
pip install -r requirements.txt
Set up MySQL database

Create a database (e.g., flask_test_db)

Update app.config in app.py with your database credentials

Use phpMyAdmin to create required tables or import from a SQL file (if provided)

Run the Flask app

bash
Copy
Edit
python app.py
Open in browser

cpp
Copy
Edit
http://127.0.0.1:5000/
📂 Folder Structure
cpp
Copy
Edit
flask_test_app/
├── app.py
├── templates/
│   ├── index.html
│   ├── login.html
│   └── ...
├── static/
├── requirements.txt
└── README.md
🙋‍♀️ Author
Navya Ghatta
📫 LinkedIn
