🏫 SCHOOL MANAGEMENT SYSTEM — FLASK

A full-featured School Management System built with Flask and MySQL, designed to simplify and automate school operations such as managing students, teachers, classes, subjects, attendance, and reports.

This project was developed as part of my portfolio and demonstrated in my video presentation.

🚀 Features

👩‍🏫 Admin Panel

Secure login and session management

Dashboard overview after login

Role-based access ready (can be extended for teachers/students)

📚 Core Modules

Teacher Management — Add, edit, delete, and assign subjects

Subject Management — Manage subject names, types, and codes

Class Management — Manage classes, sections, and teacher assignments

Section Management — Create and organize student sections

Student Management — Add, edit, and delete student records with photo upload

Attendance Management — Record and update daily attendance per class and section

Attendance Reports — View attendance summaries and reports by date and class

🛠️ Technologies Used

Layer	Technology

Backend	Python (Flask Framework)

Database	MySQL (via PyMySQL)

Frontend	HTML, CSS, Jinja Templates

Security	Werkzeug for password hashing

Server	Flask built-in development server

⚙️ Installation Guide

1️⃣ Clone the Repository

git clone https://github.com/tmp-cloud7/SCHOOL-MANAGEMENT-SYSTEM---FLASK.git
cd SCHOOL-MANAGEMENT-SYSTEM---FLASK

2️⃣ Create and Activate a Virtual Environment

venv\Scripts\activate       # On Windows

# or

source venv/bin/activate    # On macOS/Linux

3️⃣ Install Dependencies

pip install -r requirements.txt

4️⃣ Set Up the Database

Create a MySQL database (e.g., flask_sms)

Import the provided SQL file (named something like Database.sql) into MySQL:

mysql -u root -p flask_sms < Database.sql


Update your database credentials in app.py if necessary:

g.db = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    db='flask_sms',
    cursorclass=pymysql.cursors.DictCursor
)

5️⃣ Run the Application
python app.py


Visit the app in your browser at:
👉 http://127.0.0.1:5000

🔒 Default Login

You can register users directly in your database table sms_user

Example entry:

INSERT INTO sms_user (first_name, email, password, type, status)
VALUES ('Admin', 'admin@example.com', 'admin123', 'admin', 'active');


(You can later hash passwords using generate_password_hash() for production.)

🎥 Video Demonstration

🎬 Project Presentation: Featured on my portfolio as

“SCHOOL MANAGEMENT SYSTEM — FLASK”

💡 Future Improvements

Role-based dashboards (Admin / Teacher / Student)

Automated grading system

PDF export for reports

Enhanced UI with Bootstrap 5 or React frontend

🧑‍💻 Author

Tayo Popoola
💼 Full - Stack Developer | 🌐 https://lucent-gnome-a196b3.netlify.app
