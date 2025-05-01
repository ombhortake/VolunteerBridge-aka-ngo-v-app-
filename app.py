# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from functools import wraps
import datetime

app = Flask(__name__)
# Make SURE you set a real secret key
app.secret_key = os.urandom(24) # Example: Use a random key for development

# Context processor to make 'now' available globally
@app.context_processor
def inject_now():
    return {'now': datetime.datetime.utcnow()}

# Database setup (ensure this function exists and is called once)
def setup_database():
    conn = sqlite3.connect('database/ngo_volunteer.db')
    cursor = conn.cursor()
    
    # Create NGOs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ngos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        description TEXT,
        mission TEXT,
        contact TEXT
    )
    ''')
    
    # Create Volunteers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS volunteers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        contact TEXT,
        interests TEXT,
        skills TEXT,
        availability TEXT
    )
    ''')
    
    # Create Tasks table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ngo_id INTEGER NOT NULL,
        volunteer_id INTEGER,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pending',
        FOREIGN KEY (ngo_id) REFERENCES ngos(id),
        FOREIGN KEY (volunteer_id) REFERENCES volunteers(id)
    )
    ''')
    
    # Create Volunteering History table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS volunteering_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        volunteer_id INTEGER NOT NULL,
        ngo_id INTEGER NOT NULL,
        task_id INTEGER NOT NULL,
        completion_date TEXT NOT NULL,
        FOREIGN KEY (volunteer_id) REFERENCES volunteers(id),
        FOREIGN KEY (ngo_id) REFERENCES ngos(id),
        FOREIGN KEY (task_id) REFERENCES tasks(id)
    )
    ''')
    
    conn.commit()
    conn.close()

if not os.path.exists('database/ngo_volunteer.db'):
     print("Database not found, creating...")
     if not os.path.exists('database'):
        os.makedirs('database')
     setup_database() # Call the setup function
     print("Database created.")
else:
    print("Database found.")


# Login required decorator (as before)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# === CORE ROUTES ===

@app.route('/')
def home():
    # This route simply renders home.html, which extends base.html
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # (Login logic as before - Check user/pass, set session)
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')

        if not email or not password or not user_type:
             flash('Email, password, and user type are required.', 'danger')
             return redirect(url_for('login'))

        conn = sqlite3.connect('database/ngo_volunteer.db')
        cursor = conn.cursor()
        user = None

        if user_type == 'ngo':
            cursor.execute("SELECT id, name, email, password FROM ngos WHERE email = ?", (email,))
            user_data = cursor.fetchone()
            # IMPORTANT: Add password verification here in a real app (e.g., using werkzeug.security)
            if user_data and user_data[3] == password: # Direct password check (INSECURE!)
                 user = user_data
        elif user_type == 'volunteer':
             cursor.execute("SELECT id, name, email, password FROM volunteers WHERE email = ?", (email,))
             user_data = cursor.fetchone()
             # IMPORTANT: Add password verification here too
             if user_data and user_data[3] == password: # Direct password check (INSECURE!)
                 user = user_data
        else:
             flash('Invalid user type specified.', 'danger')
             conn.close()
             return redirect(url_for('login'))

        conn.close()

        if user:
            session.clear() # Clear old session data first
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_type'] = user_type
            session.permanent = True # Optional: Make session last longer
            flash(f'Welcome back, {user[1]}!', 'success')

            if user_type == 'ngo':
                return redirect(url_for('ngo_dashboard'))
            else:
                return redirect(url_for('volunteer_dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            return redirect(url_for('login')) # Redirect back to login on failure

    # For GET request
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
     if request.method == 'POST':
         # (Registration logic as before - Insert into DB)
         name = request.form.get('name')
         email = request.form.get('email')
         password = request.form.get('password') # Store hashed password in real app
         user_type = request.form.get('user_type')

         if not name or not email or not password or not user_type:
             flash('All fields are required for registration.', 'warning')
             return render_template('register.html')

         conn = sqlite3.connect('database/ngo_volunteer.db')
         cursor = conn.cursor()
         try:
             if user_type == 'ngo':
                 cursor.execute("INSERT INTO ngos (name, email, password) VALUES (?, ?, ?)",
                               (name, email, password)) # Store hashed password
             elif user_type == 'volunteer':
                 cursor.execute("INSERT INTO volunteers (name, email, password) VALUES (?, ?, ?)",
                               (name, email, password)) # Store hashed password
             else:
                  flash('Invalid user type.', 'danger')
                  conn.close()
                  return render_template('register.html')

             conn.commit()
             flash('Registration successful! Please login.', 'success')
             return redirect(url_for('login'))
         except sqlite3.IntegrityError:
             flash('Email address already registered. Please use a different email or login.', 'warning')
         except Exception as e:
             flash(f'An unexpected error occurred: {e}', 'danger')
         finally:
             conn.close()

     # For GET request
     return render_template('register.html')

@app.route('/logout')
def logout():
    user_name = session.get('user_name', 'There') # Get name before clearing
    session.clear()
    flash(f'Goodbye, {user_name}! You have been logged out.', 'success')
    return redirect(url_for('home'))
# NGO Dashboard
@app.route('/ngo/dashboard')
@login_required
def ngo_dashboard():
    if session.get('user_type') != 'ngo':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    ngo_id = session.get('user_id')
    conn = sqlite3.connect('database/ngo_volunteer.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
    SELECT t.*, v.name as volunteer_name
    FROM tasks t
    LEFT JOIN volunteers v ON t.volunteer_id = v.id
    WHERE t.ngo_id = ? ORDER BY t.id DESC
    ''', (ngo_id,))
    tasks = cursor.fetchall()
    conn.close()

    return render_template('ngo_dashboard.html', tasks=tasks)

# Create Task
@app.route('/ngo/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    if session.get('user_type') != 'ngo':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        title = request.form.get('title') # Use .get() for safety
        description = request.form.get('description')
        ngo_id = session.get('user_id')

        if not title or not description:
             flash('Task title and description are required.', 'warning')
             return render_template('create_task.html') # Stay on page if invalid

        conn = sqlite3.connect('database/ngo_volunteer.db')
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO tasks (ngo_id, title, description, status)
            VALUES (?, ?, ?, 'Pending')
            ''', (ngo_id, title, description))
            conn.commit()
            flash('Task created successfully!', 'success')
            return redirect(url_for('ngo_dashboard'))
        except Exception as e:
             flash(f'An error occurred: {e}', 'danger')
        finally:
            conn.close()

    return render_template('create_task.html')

# NGO Profile
@app.route('/ngo/profile', methods=['GET', 'POST'])
@login_required
def ngo_profile():
    if session.get('user_type') != 'ngo':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    ngo_id = session.get('user_id')
    conn = sqlite3.connect('database/ngo_volunteer.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == 'POST':
        # Get form data using .get() for safety
        description = request.form.get('description', '')
        mission = request.form.get('mission', '')
        contact = request.form.get('contact', '')

        try:
            cursor.execute('''
            UPDATE ngos
            SET description = ?, mission = ?, contact = ?
            WHERE id = ?
            ''', (description, mission, contact, ngo_id))
            conn.commit()
            flash('Profile updated successfully!', 'success')
            # Redirect to GET request to avoid form resubmission issues
            return redirect(url_for('ngo_profile'))
        except Exception as e:
             flash(f'An error occurred during update: {e}', 'danger')

    # Always fetch fresh data for GET request or after POST failure
    cursor.execute('SELECT * FROM ngos WHERE id = ?', (ngo_id,))
    ngo = cursor.fetchone()
    conn.close()

    if not ngo:
        flash('NGO profile not found.', 'danger')
        return redirect(url_for('ngo_dashboard'))

    return render_template('ngo_profile.html', ngo=ngo)


# Volunteer Dashboard
@app.route('/volunteer/dashboard')
@login_required
def volunteer_dashboard():
    if session.get('user_type') != 'volunteer':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    volunteer_id = session.get('user_id')
    conn = sqlite3.connect('database/ngo_volunteer.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get tasks assigned to this volunteer (Pending first)
    cursor.execute('''
    SELECT t.*, n.name as ngo_name
    FROM tasks t
    JOIN ngos n ON t.ngo_id = n.id
    WHERE t.volunteer_id = ?
    ORDER BY CASE WHEN t.status = 'Pending' THEN 0 ELSE 1 END, t.id DESC
    ''', (volunteer_id,))
    assigned_tasks = cursor.fetchall()

    # Get available tasks (not assigned to any volunteer)
    cursor.execute('''
    SELECT t.*, n.name as ngo_name
    FROM tasks t
    JOIN ngos n ON t.ngo_id = n.id
    WHERE t.volunteer_id IS NULL AND t.status = 'Pending'
    ORDER BY t.id DESC
    ''')
    available_tasks = cursor.fetchall()

    conn.close()

    return render_template('volunteer_dashboard.html',
                          assigned_tasks=assigned_tasks,
                          available_tasks=available_tasks)

# Volunteer Profile
@app.route('/volunteer/profile', methods=['GET', 'POST'])
@login_required
def volunteer_profile():
    if session.get('user_type') != 'volunteer':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    volunteer_id = session.get('user_id')
    conn = sqlite3.connect('database/ngo_volunteer.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == 'POST':
        # Get form data using .get()
        contact = request.form.get('contact', '')
        interests = request.form.get('interests', '')
        skills = request.form.get('skills', '')
        availability = request.form.get('availability', '')

        try:
            cursor.execute('''
            UPDATE volunteers
            SET contact = ?, interests = ?, skills = ?, availability = ?
            WHERE id = ?
            ''', (contact, interests, skills, availability, volunteer_id))
            conn.commit()
            flash('Profile updated successfully!', 'success')
            # Redirect to GET request
            return redirect(url_for('volunteer_profile'))
        except Exception as e:
             flash(f'An error occurred during update: {e}', 'danger')

    # Always fetch fresh data
    cursor.execute('SELECT * FROM volunteers WHERE id = ?', (volunteer_id,))
    volunteer = cursor.fetchone()
    conn.close()

    if not volunteer:
        flash('Volunteer profile not found.', 'danger')
        return redirect(url_for('volunteer_dashboard'))

    return render_template('volunteer_profile.html', volunteer=volunteer)


# Volunteer Opportunities
@app.route('/volunteer/opportunities')
@login_required
def volunteer_opportunities():
    if session.get('user_type') != 'volunteer':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    conn = sqlite3.connect('database/ngo_volunteer.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get available tasks with NGO details
    cursor.execute('''
    SELECT t.*, n.name as ngo_name, n.description as ngo_description, n.mission as ngo_mission
    FROM tasks t
    JOIN ngos n ON t.ngo_id = n.id
    WHERE t.volunteer_id IS NULL AND t.status = 'Pending'
    ORDER BY t.id DESC
    ''')
    opportunities = cursor.fetchall()
    conn.close()

    return render_template('volunteer_opportunities.html', opportunities=opportunities)

# Volunteer History
@app.route('/volunteer/history')
@login_required
def volunteer_history():
    if session.get('user_type') != 'volunteer':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    volunteer_id = session.get('user_id')
    conn = sqlite3.connect('database/ngo_volunteer.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get completed tasks history including completion date
    cursor.execute('''
    SELECT t.*, n.name as ngo_name, vh.completion_date
    FROM tasks t
    JOIN ngos n ON t.ngo_id = n.id
    JOIN volunteering_history vh ON t.id = vh.task_id
    WHERE t.volunteer_id = ? AND t.status = 'Completed' AND vh.volunteer_id = ?
    ORDER BY vh.completion_date DESC, t.id DESC
    ''', (volunteer_id, volunteer_id)) # Added join and WHERE clause for vh.volunteer_id
    history = cursor.fetchall()

    # Calculate stats
    completed_count = len(history)
    ngos_helped = set(task['ngo_name'] for task in history)
    ngos_helped_count = len(ngos_helped)

    conn.close()

    return render_template('volunteer_history.html',
                           history=history,
                           completed_count=completed_count,
                           ngos_helped_count=ngos_helped_count)


# Accept Task
@app.route('/volunteer/accept_task/<int:task_id>', methods=['POST']) # Use POST for actions
@login_required
def accept_task(task_id):
    if session.get('user_type') != 'volunteer':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    volunteer_id = session.get('user_id')
    conn = sqlite3.connect('database/ngo_volunteer.db')
    cursor = conn.cursor()
    try:
        # Check if task is still available
        cursor.execute("SELECT volunteer_id FROM tasks WHERE id = ? AND status = 'Pending'", (task_id,))
        task = cursor.fetchone()

        if task and task[0] is None:
            cursor.execute('''
            UPDATE tasks
            SET volunteer_id = ?, status = 'Assigned'  -- Change status to Assigned maybe? Or keep Pending? Let's use Assigned
            WHERE id = ? AND volunteer_id IS NULL
            ''', (volunteer_id, task_id))
            conn.commit()
            flash('Task accepted successfully!', 'success')
        elif task and task[0] is not None:
             flash('Task already accepted by another volunteer.', 'warning')
        else:
            flash('Task not found or no longer available.', 'danger')

    except Exception as e:
         flash(f'An error occurred: {e}', 'danger')
    finally:
        conn.close()

    # Redirect to referrer or dashboard
    return redirect(request.referrer or url_for('volunteer_dashboard'))

# Mark Task as Completed
@app.route('/volunteer/complete_task/<int:task_id>', methods=['POST']) # Use POST for actions
@login_required
def complete_task(task_id):
    if session.get('user_type') != 'volunteer':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    volunteer_id = session.get('user_id')
    conn = sqlite3.connect('database/ngo_volunteer.db')
    cursor = conn.cursor()
    try:
        # Check if task belongs to this volunteer and is not already completed
        cursor.execute("SELECT ngo_id, status FROM tasks WHERE id = ? AND volunteer_id = ?", (task_id, volunteer_id))
        task = cursor.fetchone()

        if task and task[1] != 'Completed':
            ngo_id = task[0]
            today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Store timestamp

            # Use a transaction
            conn.execute('BEGIN TRANSACTION')

            # Update task status
            cursor.execute('''
            UPDATE tasks
            SET status = 'Completed'
            WHERE id = ? AND volunteer_id = ?
            ''', (task_id, volunteer_id))

            # Check if history record already exists (to prevent duplicates if clicked twice fast)
            cursor.execute("SELECT id FROM volunteering_history WHERE task_id = ? AND volunteer_id = ?", (task_id, volunteer_id))
            existing_history = cursor.fetchone()

            if not existing_history:
                # Add to volunteering history
                cursor.execute('''
                INSERT INTO volunteering_history (volunteer_id, ngo_id, task_id, completion_date)
                VALUES (?, ?, ?, ?)
                ''', (volunteer_id, ngo_id, task_id, today))

            conn.commit() # Commit transaction
            flash('Task marked as completed!', 'success')
        elif task and task[1] == 'Completed':
             flash('Task is already marked as completed.', 'info')
        else:
            flash('Task not found or not assigned to you.', 'danger')

    except Exception as e:
        conn.rollback() # Rollback transaction on error
        flash(f'An error occurred: {e}', 'danger')
    finally:
        conn.close()

    return redirect(url_for('volunteer_dashboard'))

# Remove the custom unique filter if you calculated stats in the route
# @app.template_filter('unique')
# def unique_filter(l):
#    return set(l)

# Run the application
if __name__ == '__main__':
    app.run(debug=True, port=5001)