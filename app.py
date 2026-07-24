import os
import base64
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, session,redirect, url_for, flash, Response, jsonify
import cv2
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

@app.route('/contact-check', methods=['POST'])
def contact_check():
    name = request.form['name']
    email = request.form['email']
    subject=request.form['subject']
    message = request.form['message']

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO feedback (name, email, subject,message) VALUES (%s, %s, %s, %s)", (name, email, subject,message))
    conn.commit()

    cursor.close()
    conn.close()
    flash("Message sent successfully!", "success")

    return redirect(url_for('contact'))

@app.route('/admin_feedback')
def feedback_show():
    if session.get('user_id') and session.get('role_id')==1:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM feedback")
        feedback = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('admin_feedback.html', feedback=feedback)
    else:
        return redirect(url_for('login'))

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
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT COUNT(*) as count FROM students")
        total_students = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM faculty")
        total_faculty = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM courses")
        total_courses = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM feedback")
        total_feedbacks = cursor.fetchone()['count']
        
        cursor.execute('''
            SELECT u.full_name, r.role_name, a.attendance_time, a.status, u.profile_img 
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            JOIN users u ON s.user_id = u.user_id
            JOIN roles r ON u.role_id = r.role_id
            ORDER BY a.attendance_time DESC
            LIMIT 5
        ''')
        recent_attendance = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('admin_dashboard.html', 
                               total_students=total_students, 
                               total_faculty=total_faculty,
                               total_courses=total_courses,
                               total_feedbacks=total_feedbacks,
                               recent_attendance=recent_attendance)
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

@app.route('/admin/register-face', methods=['GET', 'POST'])
def face_registration():
    if session.get('user_id') and session.get('role_id')==1:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            student_id = request.form.get('student_id')
            face_data = request.form.get('face_data')
            
            if student_id and face_data:
                try:
                    header, encoded = face_data.split(",", 1)
                    data = base64.b64decode(encoded)
                    
                    filename = f"student_{student_id}.jpg"
                    filepath = os.path.join(app.root_path, 'static', 'faces', filename)
                    
                    with open(filepath, "wb") as f:
                        f.write(data)
                        
                    db_path = f"/static/faces/{filename}"
                    
                    cursor.execute('''
                        INSERT INTO face_data (student_id, image_path) 
                        VALUES (%s, %s) 
                        ON DUPLICATE KEY UPDATE image_path = %s
                    ''', (student_id, db_path, db_path))
                    
                    conn.commit()
                    flash("Face registered successfully!", "success")
                except Exception as e:
                    flash(f"Error saving face data: {e}", "danger")
            else:
                flash("Missing student selection or face data.", "danger")
                
            cursor.close()
            conn.close()
            return redirect(url_for('face_registration'))
            
        cursor.execute('''
            SELECT s.student_id, u.full_name, u.user_id, s.course_id, s.semester_id 
            FROM students s 
            JOIN users u ON s.user_id = u.user_id 
            WHERE u.status = 1
            ORDER BY u.full_name ASC
        ''')
        students = cursor.fetchall()
        
        cursor.execute('SELECT * FROM courses')
        courses = cursor.fetchall()
        
        cursor.execute('SELECT * FROM semesters')
        semesters = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('face_registration.html', students=students, courses=courses, semesters=semesters)
    else:
        flash('You are not authorized to access this page','danger')
        return redirect(url_for('login'))

# --- OpenCV Camera Integration ---
camera = None

def get_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
    return camera

def gen_frames():
    cam = get_camera()
    while True:
        success, frame = cam.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    if session.get('user_id') and session.get('role_id')==1:
        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    return "Unauthorized", 403

@app.route('/capture_frame')
def capture_frame():
    if session.get('user_id') and session.get('role_id')==1:
        global camera
        cam = get_camera()
        success, frame = cam.read()
        if success:
            ret, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            
            # Release the camera so the light turns off
            cam.release()
            camera = None
            
            return jsonify({"status": "success", "image": "data:image/jpeg;base64," + jpg_as_text})
        return jsonify({"status": "error", "message": "Failed to capture frame"})
    return jsonify({"status": "error", "message": "Unauthorized"}), 403


@app.route('/admin/feedback')
def admin_feedback():
    if session.get('user_id') and session.get('role_id')==1:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM feedback ORDER BY feedback_id DESC')
        feedbacks = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('admin_feedback.html', feedbacks=feedbacks)
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



@app.route('/admin/students')
def admin_students():
    if session.get('user_id') and session.get('role_id')==1:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Fetch all students with their course and semester info
        cursor.execute('''
            SELECT u.user_id, u.full_name, u.email, u.profile_img, u.status, 
                   s.student_id, fd.student_id as fd_student_id,c.course_name, c.course_id, sem.semester_name, sem.semester_id 
            FROM users u 
            JOIN students s ON u.user_id = s.user_id 
            LEFT JOIN face_data fd ON s.student_id = fd.student_id
            JOIN courses c ON s.course_id = c.course_id
            JOIN semesters sem ON s.semester_id = sem.semester_id
            WHERE u.role_id = 3
        ''')
        students = cursor.fetchall()
        
        # Fetch courses and semesters for dropdowns
        cursor.execute('SELECT * FROM courses')
        courses = cursor.fetchall()
        
        cursor.execute('SELECT * FROM semesters')
        semesters = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return render_template('admin_student.html', students=students, courses=courses, semesters=semesters)
    else:
        flash('You are not authorized to access this page','danger')
        return redirect(url_for('login'))

@app.route('/admin/students/add', methods=['POST'])
def add_student():
    if session.get('user_id') and session.get('role_id')==1:
        full_name = request.form['full_name']
        email = request.form['email']
        course_id = request.form['course_id']
        semester_id = request.form['semester_id']
        profile_img = '/assets/img/Users/Student/Default.jpg'
        status = 1
        created_at = datetime.datetime.now()
        hashed_password = None
        
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Insert into users table with role_id 3
            cursor.execute('INSERT INTO users (role_id, full_name, email, password, profile_img, status, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                           (3, full_name, email, hashed_password, profile_img, status, created_at))
            user_id = cursor.lastrowid
            
            # Insert into students table
            cursor.execute('INSERT INTO students (user_id, course_id, semester_id) VALUES (%s, %s, %s)', 
                           (user_id, course_id, semester_id))
            
            conn.commit()
            
            send_student_welcome(email, full_name)
            flash('Student added successfully! Welcome email sent.', 'success')
        except Exception as e:
            flash(f'Error adding student: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('admin_students'))
    else:
        return redirect(url_for('login'))

@app.route('/admin/students/edit/<int:user_id>', methods=['POST'])
def edit_student(user_id):
    if session.get('user_id') and session.get('role_id')==1:
        full_name = request.form['full_name']
        email = request.form['email']
        course_id = request.form['course_id']
        semester_id = request.form['semester_id']
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET full_name=%s, email=%s WHERE user_id=%s', (full_name, email, user_id))
            cursor.execute('UPDATE students SET course_id=%s, semester_id=%s WHERE user_id=%s', 
                           (course_id, semester_id, user_id))
            conn.commit()
            flash('Student details updated successfully!', 'success')
        except Exception as e:
            flash(f'Error updating student: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('admin_students'))
    else:
        return redirect(url_for('login'))

@app.route('/admin/students/delete/<int:user_id>', methods=['POST'])
def delete_student(user_id):
    if session.get('user_id') and session.get('role_id')==1:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET status=0 WHERE user_id=%s', (user_id,))
            conn.commit()
            flash('Student deactivated successfully!', 'success')
        except Exception as e:
            flash(f'Error deactivating student: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('admin_students'))
    else:
        return redirect(url_for('login'))

@app.route('/admin/students/activate/<int:user_id>', methods=['POST'])
def activate_student(user_id):
    if session.get('user_id') and session.get('role_id')==1:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET status=1 WHERE user_id=%s', (user_id,))
            conn.commit()
            flash('Student activated successfully!', 'success')
        except Exception as e:
            flash(f'Error activating student: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('admin_students'))
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

def send_student_welcome(email, name):
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
            <p style="color: #555555; line-height: 1.6; font-size: 15px;">You have been successfully registered as a Student in the Smart Attendance System.</p>
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
