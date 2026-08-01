# import glob
# import re

# css_link = '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/faculty.css\') }}">\n</head>'

# files = glob.glob('d:/Smart_Attendance_System/templates/faculty_*.html') + ['d:/Smart_Attendance_System/templates/take_attendance.html']

# for f in files:
#     with open(f, 'r') as file:
#         content = file.read()
#     if 'css/faculty.css' not in content:
#         content = re.sub(r'</head>', css_link, content, count=1, flags=re.IGNORECASE)
#         with open(f, 'w') as file:
#             file.write(content)
#         print(f"Updated {f}")
