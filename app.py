import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, session,redirect, url_for, flash
from database import get_connection
from flask_mail import Mail, Message
import random
from werkzeug.security import generate_password_hash, check_password_hash
import time
import datetime

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
    if user[4]==None:
        flash("Please Forgot your password first!.", "danger")
        return redirect(url_for("forgot_password"))

    if user and check_password_hash(user[4], entered_password):
        session['user_id'] = user[0]
        session['email'] = email
        session['role_id'] = user[1]
        session['full_name'] = user[2]
        session['profile_img'] = user[5]

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
        return redirect(url_for('login'))

@app.route('/admin_profile_update', methods=['POST'])
def admin_profile_update():
    if session.get('user_id') and session.get('role_id') == 1:
        full_name = request.form.get('full_name')
        
        # Handle file upload
        profile_img_path = session.get('profile_img')
        if 'profile_img' in request.files:
            file = request.files['profile_img']
            if file.filename != '':
                filename = secure_filename(file.filename)
                # save it directly to the assets dir
                upload_folder = os.path.join(app.root_path, 'assets', 'img', 'Users', 'Admin')
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
                profile_img_path = f'/assets/img/Users/Admin/{filename}'
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET full_name=%s, profile_img=%s WHERE user_id=%s', (full_name, profile_img_path, session['user_id']))
            conn.commit()
            
            session['full_name'] = full_name
            session['profile_img'] = profile_img_path
            
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            flash(f'Error updating profile: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('admin_profile'))
    return redirect(url_for('login'))

@app.route('/admin_password_update', methods=['POST'])
def admin_password_update():
    if session.get('user_id') and session.get('role_id') == 1:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash('New password and confirm password do not match!', 'danger')
            return redirect(url_for('admin_profile'))

        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT password FROM users WHERE user_id=%s', (session['user_id'],))
            user = cursor.fetchone()
            
            if user and check_password_hash(user[0], current_password):
                hashed_password = generate_password_hash(new_password)
                cursor.execute('UPDATE users SET password=%s WHERE user_id=%s', (hashed_password, session['user_id']))
                conn.commit()
                flash('Password updated successfully!', 'success')
            else:
                flash('Incorrect current password!', 'danger')
        except Exception as e:
            flash(f'Error updating password: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('admin_profile'))
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

@app.route('/admin/faculty')
def admin_faculty():
    if session.get('user_id') and session.get('role_id')==1:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT u.user_id, u.full_name, u.email, u.profile_img, u.status, f.faculty_id, f.designation 
            FROM users u 
            JOIN faculty f ON u.user_id = f.user_id 
            WHERE u.role_id = 2
        ''')
        faculties = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('admin_faculty.html', faculties=faculties)
    else:
        flash('You are not authorized to access this page','danger')
        return redirect(url_for('login'))

@app.route('/admin/faculty/add', methods=['POST'])
def add_faculty():
    if session.get('user_id') and session.get('role_id')==1:
        full_name = request.form['full_name']
        email = request.form['email']
        designation = request.form['designation']
        profile_img = '/assets/img/Users/Faculty/Default.jpg'
        status = 1
        created_at = datetime.datetime.now()
        hashed_password = None
        
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO users (role_id, full_name, email, password, profile_img, status, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                           (2, full_name, email, hashed_password, profile_img, status, created_at))
            user_id = cursor.lastrowid
            
            cursor.execute('INSERT INTO faculty (user_id, designation) VALUES (%s, %s)', (user_id, designation))
            
            conn.commit()
            
            send_faculty_welcome(email, full_name)
            flash('Faculty member added successfully! Welcome email sent.', 'success')
        except Exception as e:
            flash(f'Error adding faculty: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('admin_faculty'))
    else:
        return redirect(url_for('login'))

@app.route('/admin/faculty/edit/<int:user_id>', methods=['POST'])
def edit_faculty(user_id):
    if session.get('user_id') and session.get('role_id')==1:
        full_name = request.form['full_name']
        email = request.form['email']
        designation = request.form['designation']
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET full_name=%s, email=%s WHERE user_id=%s', (full_name, email, user_id))
            cursor.execute('UPDATE faculty SET designation=%s WHERE user_id=%s', (designation, user_id))
            conn.commit()
            flash('Faculty details updated successfully!', 'success')
        except Exception as e:
            flash(f'Error updating faculty: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('admin_faculty'))
    else:
        return redirect(url_for('login'))

@app.route('/admin/faculty/delete/<int:user_id>', methods=['POST'])
def delete_faculty(user_id):
    if session.get('user_id') and session.get('role_id')==1:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET status=0 WHERE user_id=%s', (user_id,))
            conn.commit()
            flash('Faculty member deactivated successfully!', 'success')
        except Exception as e:
            flash(f'Error deactivating faculty: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('admin_faculty'))
    else:
        return redirect(url_for('login'))

@app.route('/admin/faculty/activate/<int:user_id>', methods=['POST'])
def activate_faculty(user_id):
    if session.get('user_id') and session.get('role_id')==1:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET status=1 WHERE user_id=%s', (user_id,))
            conn.commit()
            flash('Faculty member activated successfully!', 'success')
        except Exception as e:
            flash(f'Error activating faculty: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('admin_faculty'))
    else:
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

def send_faculty_welcome(email, name):
    msg = Message(
        "Welcome to Smart Attendance System",
        sender=("AttendEase | Admin",app.config['MAIL_USERNAME']),
        recipients=[email]
    )

    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
        <div style="background-color: #35ac39; padding: 20px; text-align: center;">
            <h2 style="color: #ffffff; margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">Smart Attendance System</h2>
        </div>
        <div style="padding: 40px 30px; background-color: #ffffff;">
            <h3 style="color: #333333; margin-top: 0; font-size: 20px;">Registration Successful</h3>
            <p style="color: #555555; line-height: 1.6; font-size: 15px;">Hello {name},</p>
            <p style="color: #555555; line-height: 1.6; font-size: 15px;">You have been successfully registered as a Faculty member in the Smart Attendance System.</p>
            <p style="color: #555555; line-height: 1.6; font-size: 15px;">To set up your password, please go to the website and use the <strong>Forgot Password</strong> feature with this email address.</p>
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





@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
        

if __name__ == '__main__':
    # Run the app in debug mode on port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
