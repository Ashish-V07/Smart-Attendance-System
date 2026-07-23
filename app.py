from flask import Flask, render_template, request, session,redirect, url_for, flash
from database import get_connection
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='assets', static_url_path='/assets')
app.secret_key = 'super_secret_key_for_development'

# --- PUBLIC ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route("/login-check",methods=['post'])
def login_check():
    email = request.form['email']
    entered_password = request.form['password']

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user and check_password_hash(user[4], entered_password):
        session['user_id'] = user[0]
        session['email'] = email
        session['role_id'] = user[1]

        if user[1] == 1:
            return redirect('/admin_dashboard')
        elif user[1] == 2:
            return redirect('/faculty_dashboard')
        elif user[1] == 3:
            return redirect('/student_dashboard')

    flash("Invalid email or password", "danger")
    return redirect(url_for("login"))
    

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html')

@app.route('/thank-you')
def thank_you():
    return render_template('thank-you.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('user_id') and session.get('role_id')==1:
        return render_template('admin_dashboard.html')
    else:
        flash('You are not authorized to access this page','danger')
        return redirect(url_for('login'))
    

@app.route('/admin/profile')
def admin_profile():
    if session.get('user_id') and session.get('role_id')==1:
        return render_template('Admin-profile.html')
    else:
        flash('You are not authorized to access this page','danger')
        return redirect(url_for('login'))

@app.route('/admin/register-face')
def face_registration():
    if session.get('user_id') and session.get('role_id')==1:
        return render_template('face_registration.html')
    else:
        flash('You are not authorized to access this page','danger')
        return redirect(url_for('login'))

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
        
if __name__ == '__main__':
    # Run the app in debug mode on port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
