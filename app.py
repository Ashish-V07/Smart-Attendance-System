from flask import Flask, render_template, request, session,redirect, url_for, flash
from database import get_connection
from flask_mail import Mail, Message
import random
from werkzeug.security import generate_password_hash, check_password_hash
import time

app = Flask(__name__, static_folder='assets', static_url_path='/assets')
app.secret_key = '@Yash_(05-smart-attendance-system-15)_Ashish@'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '22bmiit150@gmail.com'
app.config['MAIL_PASSWORD'] = 'amfz qmxs dtom ibkx'

mail = Mail(app)
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

@app.route('/forgot-password-check',methods=['post'])
def forgot_password_check():
    email=request.form['email']
    otp=random.randint(100000,999999)
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()
    if user:
        session['otp']=str(otp)
        session['email']=email
        session['otp_time'] = time.time()
        send_otp(email,otp)
        return redirect('verify_otp')
    else:
        flash("User Not Found!", "danger")
        return redirect("/forgot-password")


@app.route('/verify_otp')
def verify_otp():
    return render_template('verify_otp.html')

@app.route('/verify_otp_check',methods=['post'])
def verify_otp_check():
    otp=request.form['otp']
    
    otp_time = session.get('otp_time')
    if not otp_time or (time.time() - otp_time > 600):
        session.pop('otp', None)
        session.pop('otp_time', None)
        flash("OTP has expired. Please request a new one.", "danger")
        return redirect("/forgot-password")
        
    if otp==session.get('otp'):
        flash("OTP Verified Successfully", "success")
        return redirect('reset_password')
    else:
        flash("Invalid OTP", "danger")
        return redirect("verify_otp")


@app.route('/reset_password')
def reset_password():
    return render_template('reset_password.html')

@app.route('/reset_password_check',methods=['post'])
def reset_password_check():
    password=request.form['password']
    hashed_password = generate_password_hash(password)
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password=%s WHERE email=%s", (hashed_password, session['email']))
    conn.commit()
    cursor.close()
    conn.close()
    
    session.pop('email', None)
    session.pop('otp', None)
    
    flash("Password Reset Successfully", "success")
    return redirect("login")


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



#default functions

def send_otp(email,otp):
    msg = Message(
        "Password Reset OTP - Smart Attendance System",
        sender=("AttendEase | Admin",app.config['MAIL_USERNAME']),
        recipients=[email]
    )

    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
        <div style="background-color: #35ac39; padding: 20px; text-align: center;">
            <h2 style="color: #ffffff; margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">Smart Attendance System</h2>
        </div>
        <div style="padding: 40px 30px; background-color: #ffffff;">
            <h3 style="color: #333333; margin-top: 0; font-size: 20px;">Password Reset Request</h3>
            <p style="color: #555555; line-height: 1.6; font-size: 15px;">Hello,</p>
            <p style="color: #555555; line-height: 1.6; font-size: 15px;">We received a request to reset your password. Please use the following One-Time Password (OTP) to proceed with the reset process.</p>
            <div style="text-align: center; margin: 35px 0;">
                <span style="display: inline-block; padding: 15px 40px; background-color: #f4f7f6; color: #35ac39; font-size: 32px; font-weight: bold; letter-spacing: 8px; border-radius: 6px; border: 2px dashed #35ac39;">{otp}</span>
            </div>
            <p style="color: #555555; line-height: 1.6; font-size: 15px;">This OTP is valid until you complete the reset process. If you did not request a password reset, please safely ignore this email.</p>
            <br>
            <p style="color: #555555; line-height: 1.6; margin-bottom: 0; font-size: 15px;">Best regards,<br><strong>The Smart Attendance Team</strong></p>
        </div>
        <div style="background-color: #f9f9f9; padding: 20px; text-align: center; border-top: 1px solid #eeeeee;">
            <p style="color: #999999; font-size: 12px; margin: 0;">&copy; 2026 Smart Attendance System. All rights reserved.</p>
        </div>
    </div>
    """
    
    msg.html = html_body
    mail.send(msg)
    flash("OTP sent successfully", "success")




@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
        

if __name__ == '__main__':
    # Run the app in debug mode on port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
