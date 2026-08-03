import re

student_routes = """
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
        cursor.execute("SELECT student_id, course_id, semester_id FROM students WHERE user_id = %s", (session['user_id'],))
        student = cursor.fetchone()
        
        if student:
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
                           live_classes=live_classes)

@app.route('/student_classes')
def student_classes():
    if not session.get('user_id') or session.get('role_id') != 3:
        return redirect('/login')
        
    live_classes, upcoming_classes, past_classes = [], [], []
    
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT student_id, course_id, semester_id FROM students WHERE user_id = %s", (session['user_id'],))
        student = cursor.fetchone()
        
        if student:
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
                           past_classes=past_classes)

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
            img_dir = os.path.join(app.root_path, 'static', 'assets', 'img', 'Users', 'Student')
            os.makedirs(img_dir, exist_ok=True)
            file_path = os.path.join(img_dir, f"{session['user_id']}_{filename}")
            profile_img.save(file_path)
            
            img_url = f"/static/assets/img/Users/Student/{session['user_id']}_{filename}"
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

"""

with open('d:/Smart_Attendance_System/app.py', 'r') as f:
    content = f.read()

content = content.replace("if __name__ == '__main__':", student_routes + "\nif __name__ == '__main__':")

with open('d:/Smart_Attendance_System/app.py', 'w') as f:
    f.write(content)
