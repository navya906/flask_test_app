from flask import Flask, render_template, request, redirect, url_for,session, flash
from flask_mysqldb import MySQL
import hashlib


app = Flask(__name__,)
app.secret_key = 'navyaghatta' 

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # leave empty if default
app.config['MYSQL_DB'] = 'mydb'

mysql = MySQL(app)


#home page
@app.route('/')
def home():
    return render_template('index.html')

#registration page:
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        raw_password = request.form['password']
        
        if not is_valid(raw_password):
            return "Password must be at least 8 characters long and include uppercase, lowercase, number, and special character/s."
        
        password = hash_password(raw_password)
        fname = request.form['fname']
        lname = request.form['lname']
        gender = request.form['gender']
        birthday = request.form['birthday']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()

        if user:
            return "Username already exists!"
        else:
            cur.execute("""
                INSERT INTO users (username, fname, lname, gender, birthday, password)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, fname, lname, gender, birthday, password))
            
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('login'))

    return render_template('register.html')


#login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  
        hashed_password = hash_password(password)


        cur = mysql.connection.cursor()
        hashed_password = hash_password(password)
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, hashed_password))
        user = cur.fetchone()

        if user:
            approved = user[-1]  # assuming 'approved' is second last column
            if approved != 1:
                return "Your account is not yet approved by admin."

        cur.close()

        if user:
            session['username'] = user[1]  # assuming username is first column
            session['role'] = user[-2]     # assuming role is last column
            return redirect(url_for('welcome'))

        else:
            return "Invalid credentials. Try again."

    return render_template('login.html')

# Password validation function
import re
def is_valid(password):
    if len(password)>=8:
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])'
        return re.match(pattern,password)

# Welcome page
@app.route('/Welcome')
def welcome():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    # Get user's approval status and role
    cur.execute("SELECT approved, role FROM users WHERE username = %s", (session['username'],))
    user_data = cur.fetchone()

    if not user_data:
        cur.close()
        return "User not found."

    approved = user_data[0]
    role = user_data[1]
    tests = []
    if role == 'user' and approved == 1:
        cur.execute("SELECT id, test_name FROM tests")
        tests = cur.fetchall()

    cur.close()

    return render_template(
        'welcome.html',
        username=session['username'],
        role=role,
        approved=approved,
        tests=tests
    )

# User profile    
@app.route('/users')
def users():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT username, fname, lname, gender, birthday,role,approved FROM users")
    data = cur.fetchall()
    cur.close()
    return render_template('users.html', users=data)



#delete user
@app.route('/delete_user/<username>', methods=['POST'])
def delete_user(username):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    if username == session['username']:
        return "Admin cannot delete themselves."

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE username = %s AND role != 'admin'", (username,))
    mysql.connection.commit()
    cur.close()
    flash(f"{username} has been removed.")
    return redirect(url_for('users'))

#approve user
@app.route('/approve_user/<username>', methods=['POST'])
def approve_user(username):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET approved = 1 WHERE username = %s", (username,))
    mysql.connection.commit()
    cur.close()
    flash(f"{username} has been approved.")
    return redirect(url_for('users'))

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

#edit user
@app.route('/edit/<username>', methods=['GET', 'POST'])
def edit_user(username):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()

    if not user:
        cur.close()
        return "User not found."

    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        gender = request.form['gender']
        birthday = request.form['birthday']
        
        role = request.form['role']

        # If promoted to admin, also auto-approve
        approved = 1 if role == 'admin' else user[-1]

        cur.execute("""
            UPDATE users 
            SET fname = %s, lname = %s, gender = %s, birthday = %s, role = %s, approved = %s
            WHERE username = %s
        """, (fname, lname, gender, birthday,role, approved, username))
        mysql.connection.commit()

        # Re-fetch the updated user
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()

    cur.close()
    return render_template('edit.html', user=user)

#add question
@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        q = request.form
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO questions 
            (question_text, option_a, option_b, option_c, option_d, correct_option, category,marks, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            q['question_text'], q['a'], q['b'], q['c'], q['d'],
            q['correct_option'], q['category'],q['marks'], session['username']
        ))
        mysql.connection.commit()
        cur.close()
    return render_template('add_question.html')


#create test and view questions
@app.route('/create_test', methods=['GET', 'POST'])
def create_test():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM questions")  # This serves the 'view questions' part
    questions = cur.fetchall()

    if request.method == 'POST':
        test_name = request.form['test_name']
        selected_questions = request.form.getlist('questions')

        cur.execute("INSERT INTO tests (test_name, created_by) VALUES (%s, %s)", (test_name, session['username']))
        mysql.connection.commit()
        test_id = cur.lastrowid

        for qid in selected_questions:
            cur.execute("INSERT INTO test_questions (test_id, question_id) VALUES (%s, %s)", (test_id, qid))
        mysql.connection.commit()
        cur.close()

        flash("Test created successfully!")
        return redirect(url_for('view_tests'))

    cur.close()
    return render_template('create_test_and_view_questions.html', questions=questions)


# View tests and manage them
@app.route('/view_tests')
def view_tests():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tests")
    tests = cur.fetchall()
    cur.close()

    return render_template('view_tests.html', tests=tests)

#delete test
@app.route('/delete_test/<int:test_id>', methods=['POST'])
def delete_test(test_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM test_questions WHERE test_id = %s", (test_id,))
    cur.execute("DELETE FROM test_scores WHERE test_id = %s", (test_id,))
    cur.execute("DELETE FROM tests WHERE id = %s", (test_id,))

    mysql.connection.commit()
    cur.close()
    flash("Test deleted successfully.")
    return redirect(url_for('view_tests'))


#edit test
@app.route('/edit_test/<int:test_id>', methods=['GET', 'POST'])
def edit_test(test_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tests WHERE id = %s", (test_id,))
    test = cur.fetchone()
    cur.execute("SELECT question_id FROM test_questions WHERE test_id = %s", (test_id,))
    selected_question_ids = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT id, question_text, option_a, option_b, option_c, option_d, correct_option, category FROM questions")
    all_questions = cur.fetchall()

    if request.method == 'POST':
        new_test_name = request.form['test_name']
        new_selected_questions = request.form.getlist('questions')
        cur.execute("UPDATE tests SET test_name = %s WHERE id = %s", (new_test_name, test_id,))
        cur.execute("DELETE FROM test_questions WHERE test_id = %s", (test_id,))
        for qid in new_selected_questions:
            cur.execute("INSERT INTO test_questions (test_id, question_id) VALUES (%s, %s)", (test_id, qid))
        mysql.connection.commit()
        cur.close()

        flash("Test updated successfully.")
        return redirect(url_for('view_tests'))

    cur.close()

    return render_template('edit_test.html', test=test, all_questions=all_questions, selected_question_ids=selected_question_ids)

# View scores for a specific test
@app.route('/view_scores/<int:test_id>')
def view_scores(test_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT s.username, u.fname, u.lname, s.score, s.max_score, s.submitted_at
    FROM test_scores s
    JOIN users u ON s.username = u.username
    WHERE s.test_id = %s
""", (test_id,))

    scores = cur.fetchall()
    cur.close()

    return render_template('view_scores.html', scores=scores, test_id=test_id)


# Take a test
@app.route('/take_test/<int:test_id>', methods=['GET', 'POST'])
def take_test(test_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    cur = mysql.connection.cursor()

    # ✅ Check if the user has already attempted this test
    cur.execute("SELECT * FROM test_scores WHERE username = %s AND test_id = %s", (username, test_id))
    already_taken = cur.fetchone()

    if already_taken:
        cur.close()
        return "You have already attempted this test. You cannot take it again."

    # Proceed to fetch test details and render questions
    cur.execute("SELECT test_name FROM tests WHERE id = %s", (test_id,))
    test_name_row = cur.fetchone()
    if not test_name_row:
        return "Test not found"
    test_name = test_name_row[0]

    cur.execute("""
        SELECT q.id, q.question_text, q.option_a, q.option_b, q.option_c, q.option_d
        FROM test_questions tq
        JOIN questions q ON tq.question_id = q.id
        WHERE tq.test_id = %s
    """, (test_id,))
    rows = cur.fetchall()

    columns = ['id', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d']
    questions = [dict(zip(columns, row)) for row in rows]

    cur.close()
    return render_template('take_test.html', test_name=test_name, questions=questions, test_id=test_id)


# Submit test answers
@app.route('/submit_test/<int:test_id>', methods=['POST'])
def submit_test(test_id):
    if 'username' not in session or session.get('role') != 'user':
        return redirect(url_for('login'))

    username = session['username']
    cur = mysql.connection.cursor()

    # Get all question info
    cur.execute("""
        SELECT q.id, q.question_text, q.option_a, q.option_b, q.option_c, q.option_d, q.correct_option, q.marks
        FROM test_questions tq
        JOIN questions q ON tq.question_id = q.id
        WHERE tq.test_id = %s
    """, (test_id,))
    questions = cur.fetchall()

    score = 0
    max_score = 0
    results = []

    for q in questions:
        q_id, text, a, b, c, d, correct_option, marks = q
        user_answer = request.form.get(f"q{q_id}")
        is_correct = (user_answer and user_answer.lower() == correct_option.lower())

        max_score += marks
        if is_correct:
            score += marks

        results.append({
            'question_text': text,
            'options': {'A': a, 'B': b, 'C': c, 'D': d},
            'user_answer': user_answer,
            'correct_answer': correct_option,
            'is_correct': is_correct,
            'marks': marks
        })

    # Store the score
    cur.execute("""
        INSERT INTO test_scores (username, test_id, score, max_score)
        VALUES (%s, %s, %s, %s)
    """, (username, test_id, score, max_score))
    mysql.connection.commit()
    cur.close()

    return render_template('test_result.html', score=score, max_score=max_score, results=results)





#hash password function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

if __name__ == '__main__':
    app.run(debug=True)

