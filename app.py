from flask import Flask, render_template, request, redirect, url_for, flash

# Initialize Flask App
# By setting static_folder to 'assets', we don't have to rewrite all the HTML <script> and <link> tags!
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

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html')

@app.route('/thank-you')
def thank_you():
    return render_template('thank-you.html')

# --- ADMIN ROUTES ---
@app.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/profile')
def admin_profile():
    return render_template('Admin-profile.html')

@app.route('/admin/register-face')
def face_registration():
    return render_template('face_registration.html')

# --- API / FORM PROCESSING ROUTES ---
@app.route('/register_face', methods=['POST'])
def process_face_registration():
    # This is a placeholder for the actual backend logic
    # request.form will contain: role, user_id, full_name, department, face_data
    user_id = request.form.get('user_id')
    print(f"Received face registration for {user_id}")
    
    # Normally you would decode the Base64 image and save to DB here
    
    return {"success": True, "message": f"Successfully registered {user_id}"}

if __name__ == '__main__':
    # Run the app in debug mode on port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
