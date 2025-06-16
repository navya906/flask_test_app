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
