# Smart Attendance System 🎓

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-lightgrey?style=for-the-badge&logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-Database-orange?style=for-the-badge&logo=mysql)
![OpenCV](https://img.shields.io/badge/OpenCV-Face%20AI-green?style=for-the-badge&logo=opencv)

A next-generation, AI-powered Smart Attendance System built with Python, Flask, and OpenCV. This application revolutionizes traditional classroom roll-calls by utilizing facial recognition technology to securely and accurately log student attendance in real-time.

## 🚀 Key Features

- **Live Face AI Verification**: Students mark their attendance using their device's webcam. The system uses deep-learning-based facial recognition to verify identity with anti-spoofing security.
- **Automated Class Tracking**: Faculty members can schedule classes. Attendance tracking automatically opens and strictly closes based on the scheduled timeframe. Missed classes are automatically marked as "Absent".
- **Dynamic Dashboards**: Dedicated, beautifully designed portals for Admins, Faculty, and Students featuring live metrics, interactive tables, and visual statistics.
- **Robust Administration**: Admins can manage students, faculty, subjects, and classes, while monitoring global attendance logs and system feedback.
- **Role-Based Access Control (RBAC)**: Secure multi-tier architecture ensuring data privacy across Admin, Faculty, and Student roles.

## 🛠️ Tech Stack

- **Backend**: Python, Flask, Flask-Session
- **Database**: MySQL (mysql-connector-python)
- **AI / Computer Vision**: `face_recognition` (dlib), OpenCV (`cv2`), NumPy
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Hardware Integration**: WebRTC for browser-based webcam capture

## 🧑‍💻 Role Breakdown

### 1. Admin
- Global overview of system metrics (Total Students, Active Classes, Pending Face Registrations).
- Manage Students (Add/Edit/Delete/Activate) and Faculty.
- Manage Curriculum (Subjects, Class Schedules).
- Approve and register student face biometric data.
- Track and filter all global attendance logs.

### 2. Faculty
- View assigned scheduled classes.
- Initiate live attendance tracking for their sessions.
- Monitor real-time statistics (Total Enrolled, Present Count, Attendance Percentage).
- View student rosters and individual attendance histories.

### 3. Student
- View their personal timetable and upcoming classes.
- Mark attendance securely via webcam during active class sessions.
- Track their personal attendance percentage and history for all enrolled subjects.
- Submit system feedback.

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL Server
- C++ Build Tools (required for compiling `dlib`)
- A webcam (for testing Face Verification)

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/smart-attendance-system.git
cd smart-attendance-system
```

### Step 2: Install Dependencies
Create a virtual environment (recommended) and install the required Python packages:
```bash
pip install -r requirements.txt
```
*(Note: If `dlib` fails to install, ensure you have CMake and C++ Build Tools installed on your system).*

### Step 3: Database Setup
1. Open MySQL and create a new database.
2. Execute the provided SQL schema file to generate the required tables (`users`, `students`, `faculty`, `classes`, `attendance`, etc.).
3. Update the `get_connection()` function in `app.py` or your `.env` file with your MySQL credentials:
   ```python
   host="localhost",
   user="root",
   password="your_password",
   database="your_database"
   ```

### Step 4: Run the Application
```bash
python app.py
```
The system will start on `http://127.0.0.1:5000/`.

## 🔒 Security Notes
- Passwords are conventionally hashed using standard cryptographic libraries before database insertion.
- Biometric data (face encodings) are securely generated and stored on the server file system; no raw images are publicly exposed during the verification pipeline.

## 📄 License
This project is licensed under the MIT License.
