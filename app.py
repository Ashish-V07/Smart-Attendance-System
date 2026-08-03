import os
import base64
import json
import face_recognition

from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, session,redirect, url_for, flash, Response, jsonify
import cv2
import numpy as np
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
    if user is None:
        flash("Invalid email or password", "danger")
        return redirect(url_for("login"))
        
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
                        
                    if face_recognition is None:
                        flash("Face recognition library is not installed. Please install it to use this feature.", "danger")
                        return redirect(url_for('face_registration'))
                        
                    # Process image with face_recognition
                    image_array = face_recognition.load_image_file(filepath)
                    face_locations = face_recognition.face_locations(image_array)
                    
                    if len(face_locations) == 0:
                        os.remove(filepath)
                        flash("No face detected. Please ensure your face is clearly visible.", "danger")
                        return redirect(url_for('face_registration'))
                    elif len(face_locations) > 1:
                        os.remove(filepath)
                        flash("Multiple faces detected! Security violation. Only one person allowed.", "danger")
                        return redirect(url_for('face_registration'))
                        
                    # 1. Distance / Size Check
                    top, right, bottom, left = face_locations[0]
                    face_area = (right - left) * (bottom - top)
                    image_area = image_array.shape[0] * image_array.shape[1]
                    face_ratio = face_area / image_area
                    
                    if face_ratio < 0.05:
                        os.remove(filepath)
                        flash("Face is too far away. Please move closer to the camera.", "danger")
                        return redirect(url_for('face_registration'))
                    elif face_ratio > 0.40:
                        os.remove(filepath)
                        flash("Face is too close. Please step back slightly from the camera.", "danger")
                        return redirect(url_for('face_registration'))
                        
                    # 2. Brightness Check using OpenCV HSV values
                    img_cv2 = cv2.imread(filepath)
                    hsv = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2HSV)
                    brightness = hsv[...,2].mean()
                    
                    if brightness < 70:
                        os.remove(filepath)
                        flash("Lighting is too dark! Please move to a brighter environment.", "danger")
                        return redirect(url_for('face_registration'))
                    elif brightness > 210:
                        os.remove(filepath)
                        flash("Lighting is too bright or overexposed! Please adjust your lighting.", "danger")
                        return redirect(url_for('face_registration'))
                        
                    # 3. Liveness / Spoofing Check (Blur, Glare, Screen Border detection)
                    gray = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2GRAY)
                    
                    # A. Blur / Flatness / Screen Noise Check
                    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                    if laplacian_var < 15: # Adjusted threshold for standard webcams
                        os.remove(filepath)
                        flash("Spoofing Detected: Image is extremely blurry. Live face required!", "danger")
                        return redirect(url_for('face_registration'))
                    elif laplacian_var > 3000: # Increased threshold to avoid false positives on noisy/sharp webcams
                        os.remove(filepath)
                        flash("Spoofing Detected: Digital screen noise/pixels detected. Live face required!", "danger")
                        return redirect(url_for('face_registration'))
                        
                    # B. Phone/Screen Border Detection (Straight Lines)
                    edges = cv2.Canny(gray, 50, 150)
                    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=150, minLineLength=200, maxLineGap=10)
                    if lines is not None and len(lines) >= 8:
                        # Strong straight lines often mean a rectangular screen or photo border is visible
                        os.remove(filepath)
                        flash("Spoofing Detected: Screen or photo borders detected! Please use a live face.", "danger")
                        return redirect(url_for('face_registration'))
                        
                    # C. Glare / Reflection Detection (Flash / Screen backlight)
                    overexposed_pixels = np.sum(gray > 240)
                    if (overexposed_pixels / gray.size) > 0.15: # >15% of image is pure white
                        os.remove(filepath)
                        flash("Spoofing Detected: Extreme glare/reflection found. Are you holding a screen or glossy photo?", "danger")
                        return redirect(url_for('face_registration'))
                        
                    # 4. Occlusion Checks (Masks, Goggles, Caps)
                    landmarks = face_recognition.face_landmarks(image_array, face_locations)
                    if len(landmarks) > 0:
                        lm = landmarks[0]
                        
                        # A. Goggles / Sunglasses check (Comparing Eye brightness to Cheek brightness)
                        if 'left_eye' in lm and 'right_eye' in lm and 'chin' in lm:
                            chin_pts = np.array(lm['chin'])
                            if len(chin_pts) > 4:
                                cheek_x, cheek_y = chin_pts[3][0], chin_pts[3][1]
                                cheek_roi = img_cv2[max(0, cheek_y-10):cheek_y+10, max(0, cheek_x-10):cheek_x+10]
                                
                                left_eye_pts = np.array(lm['left_eye'])
                                right_eye_pts = np.array(lm['right_eye'])
                                eye_pts = np.vstack((left_eye_pts, right_eye_pts))
                                x, y, w, h = cv2.boundingRect(eye_pts)
                                
                                pad = 10
                                y1, y2 = max(0, y - pad), min(img_cv2.shape[0], y + h + pad)
                                x1, x2 = max(0, x - pad), min(img_cv2.shape[1], x + w + pad)
                                eye_roi = img_cv2[y1:y2, x1:x2]
                                
                                if eye_roi.size > 0 and cheek_roi.size > 0:
                                    eye_hsv = cv2.cvtColor(eye_roi, cv2.COLOR_BGR2HSV).mean(axis=(0,1))
                                    cheek_hsv = cv2.cvtColor(cheek_roi, cv2.COLOR_BGR2HSV).mean(axis=(0,1))
                                    
                                    # If the eyes are significantly darker than the cheek (sunglasses)
                                    if eye_hsv[2] < cheek_hsv[2] * 0.6:
                                        os.remove(filepath)
                                        flash("Eyes not clearly visible! Please remove any goggles or dark glasses.", "danger")
                                        return redirect(url_for('face_registration'))

                        # B. Mask Check (Strict Variance)
                        if 'bottom_lip' in lm and 'top_lip' in lm:
                            mouth_pts = np.vstack((np.array(lm['bottom_lip']), np.array(lm['top_lip'])))
                            mx, my, mw, mh = cv2.boundingRect(mouth_pts)
                            
                            pad_m = 10
                            my1, my2 = max(0, my - pad_m), min(img_cv2.shape[0], my + mh + pad_m)
                            mx1, mx2 = max(0, mx - pad_m), min(img_cv2.shape[1], mx + mw + pad_m)
                            
                            mouth_roi = gray[my1:my2, mx1:mx2]
                            if mouth_roi.size > 0:
                                mouth_var = cv2.Laplacian(mouth_roi, cv2.CV_64F).var()
                                
                                if mouth_var < 15: # Adjusted variance threshold for natural clean-shaven faces
                                    os.remove(filepath)
                                    flash("Face mask detected! Please remove your mask for registration.", "danger")
                                    return redirect(url_for('face_registration'))
                        
                    # Finally get encoding since all security checks passed
                    encodings = face_recognition.face_encodings(image_array, known_face_locations=face_locations)
                    if len(encodings) == 0:
                        os.remove(filepath)
                        flash("Could not generate face encoding. Please try again.", "danger")
                        return redirect(url_for('face_registration'))
                        
                    encoding_json = json.dumps(encodings[0].tolist())
                    db_path = f"/static/faces/{filename}"

                    
                    
                    cursor.execute('''
                        INSERT INTO face_data (student_id, image_path, face_encoding) 
                        VALUES (%s, %s, %s) 
                        ON DUPLICATE KEY UPDATE image_path = %s, face_encoding = %s
                    ''', (student_id, db_path, encoding_json, db_path, encoding_json))
                    
             # Update the face_registered column in students table
                    cursor.execute("UPDATE students SET face_registered = 1 WHERE student_id = %s", (student_id,))
                    

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


# --- SUBJECT MANAGEMENT ---
@app.route('/admin/subjects')
def admin_subjects():
    if 'user_id' not in session or session.get('role_id') != 1:
        return redirect('/login')
        
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT s.subject_id, s.subject_name, s.subject_code, s.faculty_id,
                   c.course_name, sem.semester_name, 
                   u.full_name as faculty_name
            FROM subjects s
            LEFT JOIN courses c ON s.course_id = c.course_id
            LEFT JOIN semesters sem ON s.semester_id = sem.semester_id
            LEFT JOIN faculty f ON s.faculty_id = f.faculty_id
            LEFT JOIN users u ON f.user_id = u.user_id
        ''')
        subjects = cursor.fetchall()
        
        cursor.execute("SELECT * FROM courses")
        courses = cursor.fetchall()
        cursor.execute("SELECT * FROM semesters")
        semesters = cursor.fetchall()
        cursor.execute("SELECT f.faculty_id as user_id, u.full_name as name FROM faculty f JOIN users u ON f.user_id = u.user_id WHERE u.status = 1")
        faculties = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return render_template('admin_subjects.html', subjects=subjects, courses=courses, semesters=semesters, faculties=faculties)
    return redirect('/admin_dashboard')

@app.route('/admin/subjects/add', methods=['POST'])
def add_subject():
    if 'user_id' not in session or session.get('role_id') != 1:
        return redirect('/login')
        
    subject_name = request.form.get('subject_name')
    subject_code = request.form.get('subject_code')
    course_id = request.form.get('course_id')
    semester_id = request.form.get('semester_id')
    faculty_id = request.form.get('faculty_id')
    
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO subjects (course_id, semester_id, faculty_id, subject_name, subject_code)
                VALUES (%s, %s, %s, %s, %s)
            ''', (course_id, semester_id, faculty_id, subject_name, subject_code))
            conn.commit()
            flash('Subject added successfully!', 'success')
        except Exception as err:
            flash(f'Error adding subject: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('admin_subjects'))

@app.route('/admin/subjects/delete/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    if 'user_id' not in session or session.get('role_id') != 1:
        return redirect('/login')
        
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM subjects WHERE subject_id = %s", (subject_id,))
            conn.commit()
            flash('Subject deleted successfully!', 'success')
        except Exception as err:
            flash(f'Error deleting subject (might be referenced in classes): {err}', 'danger')
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('admin_subjects'))


# --- CLASS MANAGEMENT ---
@app.route('/admin/classes')
def admin_classes():
    if 'user_id' not in session or session.get('role_id') != 1:
        return redirect('/login')
        
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT c.class_id, c.class_date, c.start_time, c.end_time,
                   s.subject_name, f.faculty_id,u.full_name as faculty_name
            FROM classes c
            LEFT JOIN subjects s ON c.subject_id = s.subject_id
            LEFT JOIN faculty f ON c.faculty_id = f.faculty_id
            LEFT JOIN users u ON f.user_id = u.user_id
            ORDER BY c.class_date DESC, c.start_time DESC
        ''')
        classes = cursor.fetchall()
        
        cursor.execute("SELECT subject_id, subject_name FROM subjects")
        subjects = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        for c in classes:
            if c['start_time']: 
                c['start_time'] = (datetime.datetime.min + c['start_time']).strftime('%I:%M %p')
            if c['end_time']: 
                c['end_time'] = (datetime.datetime.min + c['end_time']).strftime('%I:%M %p')
            if c['class_date']: c['class_date'] = str(c['class_date'])

        return render_template('admin_classes.html', classes=classes, subjects=subjects)
    return redirect('/admin_dashboard')

@app.route('/admin/classes/add', methods=['POST'])
def add_class():
    if 'user_id' not in session or session.get('role_id') != 1:
        return redirect('/login')
        
    subject_id = request.form.get('subject_id')
    class_date = request.form.get('class_date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    
    try:
        class_datetime_str = f"{class_date} {start_time}"
        class_dt = datetime.datetime.strptime(class_datetime_str, "%Y-%m-%d %H:%M")
        
        end_datetime_str = f"{class_date} {end_time}"
        end_dt = datetime.datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M")
        
        if end_dt <= class_dt:
            flash("End time must be strictly after start time.", "danger")
            return redirect(url_for('admin_classes'))
            
        if (end_dt - class_dt).total_seconds() < 1800:
            flash("Class duration must be at least 30 minutes.", "danger")
            return redirect(url_for('admin_classes'))
            
        if class_dt <= datetime.datetime.now():
            flash("Cannot schedule a class in the past.", "danger")
            return redirect(url_for('admin_classes'))
    except Exception as e:
        flash("Invalid date or time format.", "danger")
        return redirect(url_for('admin_classes'))
        
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT faculty_id FROM subjects WHERE subject_id = %s", (subject_id,))
            result = cursor.fetchone()
            if result:
                faculty_id = result[0]
                
                # Check for faculty schedule conflicts
                cursor.execute('''
                    SELECT class_id FROM classes 
                    WHERE faculty_id = %s AND class_date = %s
                    AND start_time < %s AND end_time > %s
                ''', (faculty_id, class_date, end_time, start_time))
                conflict = cursor.fetchone()
                
                if conflict:
                    flash('Faculty already has a class scheduled during this time slot.', 'danger')
                else:
                    cursor.execute('''
                        INSERT INTO classes (subject_id, faculty_id, class_date, start_time, end_time)
                        VALUES (%s, %s, %s, %s, %s)
                    ''', (subject_id, faculty_id, class_date, start_time, end_time))
                    conn.commit()
                    flash('Class scheduled successfully!', 'success')
            else:
                flash('Subject not found!', 'danger')
        except Exception as err:
            flash(f'Error scheduling class: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('admin_classes'))

@app.route('/admin/classes/delete/<int:class_id>', methods=['POST'])
def delete_class(class_id):
    if 'user_id' not in session or session.get('role_id') != 1:
        return redirect('/login')
        
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT class_date, start_time FROM classes WHERE class_id = %s", (class_id,))
            cls = cursor.fetchone()
            
            if cls:
                class_start_dt = datetime.datetime.combine(cls['class_date'], datetime.datetime.min.time()) + cls['start_time']
                if class_start_dt <= datetime.datetime.now():
                    flash('Cannot delete past or currently running classes.', 'danger')
                    return redirect(url_for('admin_classes'))
                    
            cursor.execute("DELETE FROM classes WHERE class_id = %s", (class_id,))
            conn.commit()
            flash('Class deleted successfully!', 'success')
        except Exception as err:
            flash(f'Error deleting class: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('admin_classes'))

# --- FACULTY MODULES ---
@app.route('/faculty_dashboard')
def faculty_dashboard():
    if not session.get('user_id') or session.get('role_id') != 2:
        return redirect('/login')
        
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT faculty_id FROM faculty WHERE user_id = %s", (session['user_id'],))
        fac = cursor.fetchone()
        if not fac:
            return "Faculty record not found", 403
            
        faculty_id = fac['faculty_id']
        
        cursor.execute("SELECT COUNT(*) as count FROM subjects WHERE faculty_id = %s", (faculty_id,))
        total_subjects = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM classes WHERE faculty_id = %s", (faculty_id,))
        total_classes = cursor.fetchone()['count']
        
        cursor.execute('''
            SELECT u.full_name, r.role_name, a.attendance_time, a.status, u.profile_img, s.subject_name
            FROM attendance a
            JOIN students st ON a.student_id = st.student_id
            JOIN users u ON st.user_id = u.user_id
            JOIN roles r ON u.role_id = r.role_id
            JOIN classes c ON a.class_id = c.class_id
            JOIN subjects s ON c.subject_id = s.subject_id
            WHERE c.faculty_id = %s
            ORDER BY a.attendance_time DESC
            LIMIT 5
        ''', (faculty_id,))
        recent_attendance = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('faculty_dashboard.html', 
                               total_subjects=total_subjects, 
                               total_classes=total_classes,
                               recent_attendance=recent_attendance)
    return redirect('/login')

@app.route('/faculty_subjects')
def faculty_subjects():
    if not session.get('user_id') or session.get('role_id') != 2:
        return redirect('/login')
        
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT faculty_id FROM faculty WHERE user_id = %s", (session['user_id'],))
        fac = cursor.fetchone()
        if fac:
            cursor.execute('''
                SELECT s.subject_id, s.subject_name, s.subject_code,
                       c.course_name, sem.semester_name
                FROM subjects s
                LEFT JOIN courses c ON s.course_id = c.course_id
                LEFT JOIN semesters sem ON s.semester_id = sem.semester_id
                WHERE s.faculty_id = %s
            ''', (fac['faculty_id'],))
            subjects = cursor.fetchall()
        else:
            subjects = []
            
        cursor.close()
        conn.close()
        return render_template('faculty_subjects.html', subjects=subjects)
    return redirect('/login')

@app.route('/faculty_classes')
def faculty_classes():
    if not session.get('user_id') or session.get('role_id') != 2:
        return redirect('/login')
        
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT faculty_id FROM faculty WHERE user_id = %s", (session['user_id'],))
        fac = cursor.fetchone()
        if fac:
            cursor.execute('''
                SELECT c.class_id, c.class_date, c.start_time, c.end_time, c.attendance_started,
                       s.subject_name, s.subject_code
                FROM classes c
                LEFT JOIN subjects s ON c.subject_id = s.subject_id
                WHERE c.faculty_id = %s
                ORDER BY c.class_date DESC, c.start_time DESC
            ''', (fac['faculty_id'],))
            all_classes = cursor.fetchall()
            
            now = datetime.datetime.now()
            today_date = now.date()
            current_time = now.time()
            
            live_classes = []
            upcoming_classes = []
            past_classes = []
            
            for c in all_classes:
                c_date = c['class_date']
                # Start and end are timedelta, convert to time
                s_time = (datetime.datetime.min + c['start_time']).time()
                e_time = (datetime.datetime.min + c['end_time']).time()
                
                # Format strings for display
                c['start_time_str'] = s_time.strftime('%I:%M %p')
                c['end_time_str'] = e_time.strftime('%I:%M %p')
                c['class_date_str'] = str(c_date)
                
                if c_date < today_date:
                    past_classes.append(c)
                elif c_date > today_date:
                    upcoming_classes.append(c)
                else:
                    if current_time > e_time:
                        past_classes.append(c)
                    elif current_time < s_time:
                        upcoming_classes.append(c)
                    else:
                        # Auto-start logic
                        import datetime as dt
                        s_dt = dt.datetime.combine(today_date, s_time)
                        if c['attendance_started'] == 1 or now >= (s_dt + dt.timedelta(minutes=10)):
                            c['is_attendance_open'] = True
                        else:
                            c['is_attendance_open'] = False
                        live_classes.append(c)
        else:
            live_classes, upcoming_classes, past_classes = [], [], []
            
        cursor.close()
        conn.close()
        return render_template('faculty_classes.html', 
                               live_classes=live_classes,
                               upcoming_classes=upcoming_classes,
                               past_classes=past_classes)
    return redirect('/login')

@app.route('/faculty_start_attendance/<int:class_id>')
def faculty_start_attendance(class_id):
    if not session.get('user_id') or session.get('role_id') != 2:
        return redirect('/login')
        
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        # Verify class belongs to this faculty
        cursor.execute("SELECT faculty_id FROM faculty WHERE user_id = %s", (session['user_id'],))
        fac = cursor.fetchone()
        if fac:
            cursor.execute('''
                SELECT c.*, s.subject_name, s.subject_code 
                FROM classes c
                JOIN subjects s ON c.subject_id = s.subject_id
                WHERE c.class_id = %s AND c.faculty_id = %s
            ''', (class_id, fac['faculty_id']))
            cls = cursor.fetchone()
            if cls:
                cursor.execute('UPDATE classes SET attendance_started = 1 WHERE class_id = %s', (class_id,))
                conn.commit()
                cursor.close()
                conn.close()
                return render_template('take_attendance.html', cls=cls)
        
        cursor.close()
        conn.close()
        flash("Class not found or unauthorized.", "danger")
        return redirect(url_for('faculty_classes'))
    return redirect('/login')

@app.route('/api/get_live_attendance/<int:class_id>')
def get_live_attendance(class_id):
    if not session.get('user_id') or session.get('role_id') != 2:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT u.full_name, a.attendance_time 
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            JOIN users u ON s.user_id = u.user_id
            WHERE a.class_id = %s
            ORDER BY a.attendance_time DESC
        ''', (class_id,))
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for r in records:
            if r['attendance_time']:
                r['attendance_time'] = r['attendance_time'].strftime('%I:%M:%S %p')
        return jsonify(records)
    return jsonify({'error': 'Database connection failed'}), 500

@app.route('/faculty_attendance')
def faculty_attendance():
    if not session.get('user_id') or session.get('role_id') != 2:
        return redirect('/login')
        
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT faculty_id FROM faculty WHERE user_id = %s", (session['user_id'],))
        fac = cursor.fetchone()
        if fac:
            cursor.execute('''
                SELECT a.attendance_id, a.attendance_time, a.status,
                       u.full_name as student_name, c.class_date, s.subject_name
                FROM attendance a
                JOIN students st ON a.student_id = st.student_id
                JOIN users u ON st.user_id = u.user_id
                JOIN classes c ON a.class_id = c.class_id
                JOIN subjects s ON c.subject_id = s.subject_id
                WHERE c.faculty_id = %s
                ORDER BY c.class_date DESC, a.attendance_time DESC
            ''', (fac['faculty_id'],))
            attendances = cursor.fetchall()
            for a in attendances:
                if a['class_date']: a['class_date'] = str(a['class_date'])
        else:
            attendances = []
            
        cursor.close()
        conn.close()
        return render_template('faculty_attendance.html', attendances=attendances)
    return redirect('/login')

@app.route('/faculty_profile')
def faculty_profile():
    if not session.get('user_id') or session.get('role_id') != 2:
        return redirect('/login')
    return render_template('faculty_profile.html')

@app.route('/faculty_profile_update', methods=['POST'])
def faculty_profile_update():
    if session.get('user_id') and session.get('role_id') == 2:
        full_name = request.form.get('full_name')
        
        # Handle file upload
        profile_img_path = session.get('profile_img')
        if 'profile_img' in request.files:
            file = request.files['profile_img']
            if file.filename != '':
                filename = secure_filename(file.filename)
                upload_folder = os.path.join(app.root_path, 'assets', 'img', 'Users', 'Faculty')
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
                profile_img_path = f'/assets/img/Users/Faculty/{filename}'
        
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
            
    return redirect(url_for('faculty_profile'))
    
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
        


# ==========================================
# STUDENT ROUTES
# ==========================================

@app.route('/student_dashboard')
def student_dashboard():
    if not session.get('user_id') or session.get('role_id') != 3:
        return redirect('/login')
        
    conn = get_connection()
    total_subjects = 0
    total_attended = 0
    total_classes = 0
    overall_percentage = 0
    live_classes = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT student_id, course_id, semester_id, face_registered FROM students WHERE user_id = %s", (session['user_id'],))
        student = cursor.fetchone()
        
        if student:
            face_registered = student.get('face_registered', 0)
            cursor.execute("SELECT COUNT(*) as count FROM subjects WHERE course_id = %s AND semester_id = %s", 
                           (student['course_id'], student['semester_id']))
            total_subjects = cursor.fetchone()['count']
            
            cursor.execute('''
                SELECT COUNT(*) as count FROM classes c
                JOIN subjects s ON c.subject_id = s.subject_id
                WHERE s.course_id = %s AND s.semester_id = %s AND c.class_date <= CURDATE()
            ''', (student['course_id'], student['semester_id']))
            total_classes = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM attendance WHERE student_id = %s AND status = 'Present'", (student['student_id'],))
            total_attended = cursor.fetchone()['count']
            
            if total_classes > 0:
                overall_percentage = round((total_attended / total_classes) * 100)
            else:
                overall_percentage = 100
                
            import datetime as dt
            today_date = dt.date.today()
            now = dt.datetime.now()
            current_time = now.time()
            
            cursor.execute('''
                SELECT c.*, s.subject_name, s.subject_code 
                FROM classes c
                JOIN subjects s ON c.subject_id = s.subject_id
                WHERE s.course_id = %s AND s.semester_id = %s AND c.class_date = %s
            ''', (student['course_id'], student['semester_id'], today_date))
            
            today_classes = cursor.fetchall()
            for c in today_classes:
                s_dt = dt.datetime.combine(today_date, (dt.datetime.min + c['start_time']).time())
                e_dt = dt.datetime.combine(today_date, (dt.datetime.min + c['end_time']).time())
                
                if s_dt.time() <= current_time <= e_dt.time():
                    if c['attendance_started'] == 1 or now >= (s_dt + dt.timedelta(minutes=10)):
                        cursor.execute("SELECT * FROM attendance WHERE student_id = %s AND class_id = %s", (student['student_id'], c['class_id']))
                        if not cursor.fetchone():
                            live_classes.append(c)
                            
        cursor.close()
        conn.close()
        
    return render_template('student_dashboard.html', 
                           total_subjects=total_subjects, 
                           overall_percentage=overall_percentage,
                           total_attended=total_attended,
                           total_classes=total_classes,
                           live_classes=live_classes,
                           face_registered=face_registered)

@app.route('/student_classes')
def student_classes():
    if not session.get('user_id') or session.get('role_id') != 3:
        return redirect('/login')
        
    live_classes, upcoming_classes, past_classes = [], [], []
    
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT student_id, course_id, semester_id, face_registered FROM students WHERE user_id = %s", (session['user_id'],))
        student = cursor.fetchone()
        
        if student:
            face_registered = student.get('face_registered', 0)
            cursor.execute('''
                SELECT c.*, s.subject_name, s.subject_code 
                FROM classes c
                JOIN subjects s ON c.subject_id = s.subject_id
                WHERE s.course_id = %s AND s.semester_id = %s
                ORDER BY c.class_date DESC, c.start_time DESC
            ''', (student['course_id'], student['semester_id']))
            all_classes = cursor.fetchall()
            
            import datetime as dt
            today_date = dt.date.today()
            now = dt.datetime.now()
            current_time = now.time()
            
            for c in all_classes:
                c_date = c['class_date']
                s_time = (dt.datetime.min + c['start_time']).time()
                e_time = (dt.datetime.min + c['end_time']).time()
                
                c['class_date_str'] = c_date.strftime('%b %d, %Y')
                c['start_time_str'] = s_time.strftime('%I:%M %p')
                c['end_time_str'] = e_time.strftime('%I:%M %p')
                
                if c_date < today_date:
                    past_classes.append(c)
                elif c_date > today_date:
                    upcoming_classes.append(c)
                else:
                    if current_time > e_time:
                        past_classes.append(c)
                    elif current_time < s_time:
                        upcoming_classes.append(c)
                    else:
                        s_dt = dt.datetime.combine(today_date, s_time)
                        if c['attendance_started'] == 1 or now >= (s_dt + dt.timedelta(minutes=10)):
                            c['is_attendance_open'] = True
                            cursor.execute("SELECT * FROM attendance WHERE student_id = %s AND class_id = %s", (student['student_id'], c['class_id']))
                            c['already_marked'] = bool(cursor.fetchone())
                        else:
                            c['is_attendance_open'] = False
                        live_classes.append(c)
                        
        cursor.close()
        conn.close()
        
    return render_template('student_classes.html', 
                           live_classes=live_classes,
                           upcoming_classes=upcoming_classes,
                           past_classes=past_classes,
                           face_registered=face_registered)

@app.route('/student_attendance')
def student_attendance():
    if not session.get('user_id') or session.get('role_id') != 3:
        return redirect('/login')
        
    attendances, subject_stats = [], []
    
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT student_id, course_id, semester_id FROM students WHERE user_id = %s", (session['user_id'],))
        student = cursor.fetchone()
        
        if student:
            cursor.execute('''
                SELECT a.*, s.subject_name, s.subject_code, c.class_date 
                FROM attendance a
                JOIN classes c ON a.class_id = c.class_id
                JOIN subjects s ON c.subject_id = s.subject_id
                WHERE a.student_id = %s
                ORDER BY a.attendance_time DESC
            ''', (student['student_id'],))
            attendances = cursor.fetchall()
            
            cursor.execute('''
                SELECT s.subject_name, s.subject_code, s.subject_id
                FROM subjects s
                WHERE s.course_id = %s AND s.semester_id = %s
            ''', (student['course_id'], student['semester_id']))
            subjects = cursor.fetchall()
            
            for sub in subjects:
                cursor.execute("SELECT COUNT(*) as cnt FROM classes WHERE subject_id = %s AND class_date <= CURDATE()", (sub['subject_id'],))
                total = cursor.fetchone()['cnt']
                
                cursor.execute('''
                    SELECT COUNT(*) as cnt FROM attendance a 
                    JOIN classes c ON a.class_id = c.class_id
                    WHERE a.student_id = %s AND c.subject_id = %s AND a.status = 'Present'
                ''', (student['student_id'], sub['subject_id']))
                attended = cursor.fetchone()['cnt']
                
                percent = round((attended / total * 100) if total > 0 else 100)
                sub['total'] = total
                sub['attended'] = attended
                sub['percent'] = percent
                subject_stats.append(sub)
                
        cursor.close()
        conn.close()
        
    return render_template('student_attendance.html', attendances=attendances, subject_stats=subject_stats)

@app.route('/student_profile')
def student_profile():
    if not session.get('user_id') or session.get('role_id') != 3:
        return redirect('/login')
        
    student_info = {}
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT s.*, c.course_name, sem.semester_name 
            FROM students s
            JOIN courses c ON s.course_id = c.course_id
            JOIN semesters sem ON s.semester_id = sem.semester_id
            WHERE s.user_id = %s
        ''', (session['user_id'],))
        student_info = cursor.fetchone()
        cursor.close()
        conn.close()
        
    return render_template('student_profile.html', info=student_info)

@app.route('/student_profile_update', methods=['POST'])
def student_profile_update():
    if not session.get('user_id') or session.get('role_id') != 3:
        return redirect('/login')
        
    full_name = request.form.get('full_name')
    profile_img = request.files.get('profile_img')
    
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        if full_name:
            cursor.execute("UPDATE users SET full_name = %s WHERE user_id = %s", (full_name, session['user_id']))
            session['full_name'] = full_name
            
        if profile_img and profile_img.filename:
            from werkzeug.utils import secure_filename
            import os
            filename = secure_filename(profile_img.filename)
            img_dir = os.path.join(app.root_path, 'assets', 'img', 'Users', 'Student')
            os.makedirs(img_dir, exist_ok=True)
            file_path = os.path.join(img_dir, f"{session['user_id']}_{filename}")
            profile_img.save(file_path)
            
            img_url = f"/assets/img/Users/Student/{session['user_id']}_{filename}"
            cursor.execute("UPDATE users SET profile_img = %s WHERE user_id = %s", (img_url, session['user_id']))
            session['profile_img'] = img_url
            
        conn.commit()
        cursor.close()
        conn.close()
        flash("Profile updated successfully!", "success")
        
    return redirect(url_for('student_profile'))

@app.route('/student_mark_attendance/<int:class_id>')
def student_mark_attendance(class_id):
    if not session.get('user_id') or session.get('role_id') != 3:
        return redirect('/login')
        
    conn = get_connection()
    cls = None
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Verify face is registered
        cursor.execute("SELECT face_registered FROM students WHERE user_id = %s", (session['user_id'],))
        student = cursor.fetchone()
        if not student or not student.get('face_registered'):
            cursor.close()
            conn.close()
            flash("You must register your face first before marking attendance.", "danger")
            return redirect(url_for('student_profile'))
            
        cursor.execute('''
            SELECT c.*, s.subject_name, s.subject_code 
            FROM classes c
            JOIN subjects s ON c.subject_id = s.subject_id
            WHERE c.class_id = %s
        ''', (class_id,))
        cls = cursor.fetchone()
        cursor.close()
        conn.close()
        
    if not cls:
        flash("Class not found.", "danger")
        return redirect(url_for('student_classes'))
        
    return render_template('mark_attendance.html', cls=cls)

if __name__ == '__main__':
    # Run the app in debug mode on port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
