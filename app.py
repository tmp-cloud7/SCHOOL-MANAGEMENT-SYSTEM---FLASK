from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from datetime import date
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secure secret key

# Database connection
def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='flask_sms',
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# ================= AUTH ====================

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        # cursor = get_db().cursor()
        # cursor.execute('SELECT * FROM sms_user WHERE status="active" AND email = %s', (email,))
        # user = cursor.fetchone()
        cursor = get_db().cursor()
        cursor.execute('SELECT * FROM sms_user WHERE status="active" AND email = %s', (email,))
        user = cursor.fetchone()

        print("User fetched from DB:", user)

        if user:
            print("Password from form:", password)
            print("Password in DB:", user['password'])
            print("Password match:", check_password_hash(user['password'], password))

        if user and user['password'] == password:

            session['loggedin'] = True
            session['userid'] = user['id']
            session['name'] = user['first_name']
            session['email'] = user['email']
            session['role'] = user['type']
            flash('Logged in successfully!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template("dashboard.html")
    return redirect(url_for('login'))

# ================= TEACHER ====================

@app.route("/teacher")
def teacher():
    if 'loggedin' in session:
        cursor = get_db().cursor()
        cursor.execute('SELECT t.teacher_id, t.teacher, s.subject FROM sms_teacher t LEFT JOIN sms_subjects s ON s.subject_id = t.subject_id')
        teachers = cursor.fetchall()
        cursor.execute('SELECT * FROM sms_subjects')
        subjects = cursor.fetchall()
        return render_template("teacher.html", teachers=teachers, subjects=subjects)
    return redirect(url_for('login'))

@app.route("/edit_teacher", methods =['GET'])
def edit_teacher():
    if 'loggedin' in session:
        teacher_id = request.args.get('teacher_id') 
        cursor = cursor = get_db().cursor()
        cursor.execute('SELECT t.teacher_id, t.teacher, s.subject FROM sms_teacher t LEFT JOIN sms_subjects s ON s.subject_id = t.subject_id WHERE t.teacher_id = %s', (teacher_id,))
        teachers = cursor.fetchall() 
        
        cursor.execute('SELECT * FROM sms_subjects')
        subjects = cursor.fetchall()  
        
        return render_template("edit_teacher.html", teachers = teachers, subjects = subjects)
    return redirect(url_for('login'))  

@app.route("/save_teacher", methods =['GET', 'POST'])
def save_teacher():
    if 'loggedin' in session:    
        cursor =cursor = get_db().cursor()       
        if request.method == 'POST' and 'techer_name' in request.form and 'specialization' in request.form:
            techer_name = request.form['techer_name'] 
            specialization = request.form['specialization']             
            action = request.form['action']             
            
            if action == 'updateTeacher':
                teacherid = request.form['teacherid'] 
                cursor.execute('UPDATE sms_teacher SET teacher = %s, subject_id = %s WHERE teacher_id = %s', (techer_name, specialization, (teacherid, ), ))
                get_db().commit()        
            else: 
                cursor.execute('INSERT INTO sms_teacher (`teacher`, `subject_id`) VALUES (%s, %s)', (techer_name, specialization))
                get_db().commit()        
            return redirect(url_for('teacher'))        
        elif request.method == 'POST':
            msg = 'Please fill out the form field !'        
        return redirect(url_for('teacher'))        
    return redirect(url_for('login')) 

@app.route("/delete_teacher")
def delete_teacher():
    if 'loggedin' in session:
        teacher_id = request.args.get('teacher_id')
        cursor = get_db().cursor()
        cursor.execute('DELETE FROM sms_teacher WHERE teacher_id = %s', (teacher_id,))
        get_db().commit()
        flash('Teacher deleted successfully.')
        return redirect(url_for('teacher'))
    return redirect(url_for('login'))

# ================= SUBJECT ====================

@app.route("/subject")
def subject():
    if 'loggedin' in session:
        cursor = get_db().cursor()
        cursor.execute('SELECT * FROM sms_subjects')
        subjects = cursor.fetchall()
        return render_template("subject.html", subjects=subjects)
    return redirect(url_for('login'))

@app.route("/save_subject", methods=['POST'])
def save_subject():
    if 'loggedin' in session:
        subject = request.form['subject']
        s_type = request.form['s_type']
        code = request.form['code']
        action = request.form['action']
        cursor = get_db().cursor()
        if action == 'updateSubject':
            subjectid = request.form['subjectid']
            cursor.execute('UPDATE sms_subjects SET subject = %s, type = %s, code = %s WHERE subject_id = %s',
                           (subject, s_type, code, subjectid))
        else:
            cursor.execute('INSERT INTO sms_subjects (subject, type, code) VALUES (%s, %s, %s)',
                           (subject, s_type, code))
        get_db().commit()
        flash('Subject saved successfully.')
        return redirect(url_for('subject'))
    return redirect(url_for('login'))

@app.route("/edit_subject", methods =['GET'])
def edit_subject():
    if 'loggedin' in session:
        subject_id = request.args.get('subject_id') 
        cursor =  get_db().cursor()
        cursor.execute('SELECT subject_id, subject, type, code FROM sms_subjects WHERE subject_id = %s', (subject_id,))
        subjects = cursor.fetchall() 
        return render_template("edit_subject.html", subjects = subjects)
    return redirect(url_for('login'))    

@app.route("/delete_subject")
def delete_subject():
    if 'loggedin' in session:
        subject_id = request.args.get('subject_id')
        cursor = get_db().cursor()
        cursor.execute('DELETE FROM sms_subjects WHERE subject_id = %s', (subject_id,))
        get_db().commit()
        flash('Subject deleted.')
        return redirect(url_for('subject'))
    return redirect(url_for('login'))

################################ Classes  #######################################

@app.route("/classes", methods =['GET', 'POST'])
def classes():
    if 'loggedin' in session:  
        cursor = get_db().cursor()
        cursor.execute('SELECT c.id, c.name, s.section, t.teacher FROM sms_classes c LEFT JOIN sms_section s ON s.section_id = c.section LEFT JOIN sms_teacher t ON t.teacher_id = c.teacher_id')
        classes = cursor.fetchall() 
           
        cursor.execute('SELECT * FROM sms_section')
        sections = cursor.fetchall() 
        
        cursor.execute('SELECT * FROM sms_teacher')
        teachers = cursor.fetchall()
        
        return render_template("class.html", classes = classes, sections = sections, teachers = teachers)
    return redirect(url_for('login'))

@app.route("/edit_class", methods =['GET'])
def edit_class():
    if 'loggedin' in session:
        class_id = request.args.get('class_id') 
        cursor = get_db().cursor()
        cursor.execute('SELECT c.id, c.name, s.section, t.teacher FROM sms_classes c LEFT JOIN sms_section s ON s.section_id = c.section LEFT JOIN sms_teacher t ON t.teacher_id = c.teacher_id WHERE c.id = %s', (class_id,))
        classes = cursor.fetchall() 
        
        cursor.execute('SELECT * FROM sms_section')
        sections = cursor.fetchall() 
        
        cursor.execute('SELECT * FROM sms_teacher')
        teachers = cursor.fetchall()
        
        return render_template("edit_class.html", classes = classes, sections = sections, teachers = teachers)
    return redirect(url_for('login'))  

@app.route("/save_class", methods =['GET', 'POST'])
def save_class():
    if 'loggedin' in session:    
        cursor = get_db().cursor()        
        if request.method == 'POST' and 'cname' in request.form:
            cname = request.form['cname'] 
            sectionid = request.form['sectionid']
            teacherid = request.form['teacherid']            
            action = request.form['action']             
            
            if action == 'updateClass':
                class_id = request.form['classid'] 
                cursor.execute('UPDATE sms_classes SET name = %s, section = %s, teacher_id = %s WHERE id  =%s', (cname, sectionid, teacherid, (class_id, ), ))
                get_db().commit()        
            else: 
                cursor.execute('INSERT INTO sms_classes (`name`, `section`, `teacher_id`) VALUES (%s, %s, %s)', (cname, sectionid, teacherid))
                get_db().commit()        
            return redirect(url_for('classes'))        
        elif request.method == 'POST':
            msg = 'Please fill out the form field !'        
        return redirect(url_for('classes'))        
    return redirect(url_for('login'))
    

@app.route("/delete_class", methods =['GET'])
def delete_class():
    if 'loggedin' in session:
        class_id = request.args.get('class_id') 
        cursor = get_db().cursor()
        cursor.execute('DELETE FROM sms_classes WHERE id = % s', (class_id, ))
        get_db().commit()   
        return redirect(url_for('classes'))
    return redirect(url_for('login'))     

########################### SECTIONS ##################################

@app.route("/sections", methods =['GET', 'POST'])
def sections():
    if 'loggedin' in session:      
        cursor = get_db().cursor()
        cursor.execute('SELECT * FROM sms_section')
        sections = cursor.fetchall()          
        return render_template("sections.html", sections = sections)
    return redirect(url_for('login')) 
    
@app.route("/edit_sections", methods =['GET'])
def edit_sections():
    if 'loggedin' in session:
        section_id = request.args.get('section_id') 
        cursor =get_db().cursor()
        cursor.execute('SELECT * FROM sms_section WHERE section_id = %s', (section_id,))
        sections = cursor.fetchall() 
        return render_template("edit_section.html", sections = sections)
    return redirect(url_for('login'))    
    
@app.route("/save_sections", methods =['GET', 'POST'])
def save_sections():
    if 'loggedin' in session:    
        cursor = get_db().cursor()     
        if request.method == 'POST' and 'section_name' in request.form:
            section_name = request.form['section_name']                         
            action = request.form['action']             
            
            if action == 'updateSection':
                section_id = request.form['sectionid'] 
                cursor.execute('UPDATE sms_section SET section = %s WHERE section_id  =%s', (section_name, (section_id, ), ))
                get_db().commit()        
            else: 
                cursor.execute('INSERT INTO sms_section (`section`) VALUES (%s)', (section_name, ))
                get_db().commit()        
            return redirect(url_for('sections'))        
        elif request.method == 'POST':
            msg = 'Please fill out the form field !'        
        return redirect(url_for('sections'))        
    return redirect(url_for('login')) 
    
@app.route("/delete_sections", methods =['GET'])
def delete_sections():
    if 'loggedin' in session:
        section_id = request.args.get('section_id') 
        cursor = get_db().cursor()
        cursor.execute('DELETE FROM sms_section WHERE section_id = % s', (section_id, ))
        get_db().commit()   
        return redirect(url_for('sections'))
    return redirect(url_for('login'))  

# ================= STUDENT ====================

@app.route("/student")
def student():
    if 'loggedin' in session:
        cursor = get_db().cursor()
        cursor.execute('''
            SELECT s.id, s.admission_no, s.roll_no, s.name, s.father_name, s.photo, 
                   c.name AS class, sec.section 
            FROM sms_students s 
            LEFT JOIN sms_section sec ON sec.section_id = s.section 
            LEFT JOIN sms_classes c ON c.id = s.class
        ''')
        students = cursor.fetchall()

        cursor.execute('SELECT * FROM sms_classes')
        classes = cursor.fetchall()

        cursor.execute('SELECT * FROM sms_section')
        sections = cursor.fetchall()

        return render_template("student.html", students=students, classes=classes, sections=sections)
    return redirect(url_for('login'))

@app.route('/create_student', methods=['GET'])
def create_student():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()

    # Fetch class list
    cursor.execute("SELECT * FROM sms_classes")
    classes = cursor.fetchall()

    # Fetch section list if table exists
    cursor.execute("SELECT * FROM sms_section")
    sections = cursor.fetchall()
    
    return render_template('create_student.html', classes=classes, sections=sections)

@app.route('/sc_student', methods=['POST'])
def sc_student():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    data = request.form
    file = request.files.get('photo')
    photo_filename = None

    if file and file.filename != '':
        os.makedirs('static/uploads/students', exist_ok=True) 
        photo_filename = secure_filename(file.filename)
        file.save(os.path.join('static/uploads/students', photo_filename))

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO sms_students (
            name, gender, dob, photo, mobile, email, current_address, permanent_address,
            father_name, father_mobile, father_occupation, mother_name, mother_mobile,
            admission_no, roll_no, class, section, stream, hostel, admission_date,
            category, academic_year
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data['name'], data['gender'], data['dob'], photo_filename,
        data['mobile'], data['email'], data['current_address'], data['permanent_address'],
        data['father_name'], data['father_mobile'], data['father_occupation'],
        data['mother_name'], data['mother_mobile'], data['admission_no'], data['roll_no'],
        data['class'], data['section'], data.get('stream'), data.get('hostel'),
        data['admission_date'], data.get('category'), data['academic_year']
    ))

    db.commit()

    flash("Student created successfully!", "success")
    return redirect(url_for('student'))



@app.route("/edit_student", methods=['GET'])
def edit_student():
    if 'loggedin' in session:
        student_id = request.args.get('student_id')
        cursor = get_db().cursor()

        cursor.execute('''
            SELECT s.id, s.admission_no, s.roll_no, s.name, s.photo,
                   s.gender, s.dob, s.email, s.mobile,
                   s.current_address, s.permanent_address,
                   s.father_name, s.father_mobile, s.father_occupation,
                   s.mother_name, s.mother_mobile,
                   s.academic_year, s.admission_date,
                   c.id AS class_id, sec.section_id
            FROM sms_students s
            LEFT JOIN sms_section sec ON sec.section_id = s.section
            LEFT JOIN sms_classes c ON c.id = s.class
            WHERE s.id = %s
        ''', (student_id,))
        student = cursor.fetchone()

        cursor.execute('SELECT * FROM sms_classes')
        classes = cursor.fetchall()

        cursor.execute('SELECT * FROM sms_section')
        sections = cursor.fetchall()

        return render_template(
            "edit_student.html",
            student=student,
            classes=classes,
            sections=sections
        )
    return redirect(url_for('login'))

@app.route("/save_student", methods=['POST'])
def save_student():
    if 'loggedin' in session:
        action = request.form.get('action')

        if action == 'updateStudent':
            student_id = request.form['studentid']
            admission_no = request.form['admission_no']
            roll_no = request.form['roll_no']
            academic_year = request.form['academic_year']
            admission_date = request.form['admission_date']
            class_id = request.form['class']
            section_id = request.form['section']
            name = request.form['name']
            gender = request.form['gender']
            dob = request.form['dob']
            email = request.form['email']
            mobile = request.form['mobile']
            current_address = request.form['current_address']
            permanent_address = request.form['permanent_address']
            father_name = request.form['father_name']
            father_mobile = request.form['father_mobile']
            father_occupation = request.form['father_occupation']
            mother_name = request.form['mother_name']
            mother_mobile = request.form['mother_mobile']

            photo = None
            if 'photo' in request.files and request.files['photo'].filename:
                photo_file = request.files['photo']
                photo = photo_file.filename
                photo_file.save(f"static/images/{photo}")

            cursor = get_db().cursor()
            if photo:
                cursor.execute('''
                    UPDATE sms_students
                    SET admission_no=%s, roll_no=%s, academic_year=%s, admission_date=%s,
                        class=%s, section=%s, name=%s, gender=%s, dob=%s, email=%s, mobile=%s,
                        current_address=%s, permanent_address=%s,
                        father_name=%s, father_mobile=%s, father_occupation=%s,
                        mother_name=%s, mother_mobile=%s, photo=%s
                    WHERE id=%s
                ''', (admission_no, roll_no, academic_year, admission_date, class_id, section_id,
                      name, gender, dob, email, mobile, current_address, permanent_address,
                      father_name, father_mobile, father_occupation,
                      mother_name, mother_mobile, photo, student_id))
            else:
                cursor.execute('''
                    UPDATE sms_students
                    SET admission_no=%s, roll_no=%s, academic_year=%s, admission_date=%s,
                        class=%s, section=%s, name=%s, gender=%s, dob=%s, email=%s, mobile=%s,
                        current_address=%s, permanent_address=%s,
                        father_name=%s, father_mobile=%s, father_occupation=%s,
                        mother_name=%s, mother_mobile=%s
                    WHERE id=%s
                ''', (admission_no, roll_no, academic_year, admission_date, class_id, section_id,
                      name, gender, dob, email, mobile, current_address, permanent_address,
                      father_name, father_mobile, father_occupation,
                      mother_name, mother_mobile, student_id))

            get_db().commit()
            return redirect(url_for('student'))

    return redirect(url_for('login'))
 
@app.route("/delete_student")
def delete_student():
    if 'loggedin' in session:
        student_id = request.args.get('student_id')
        cursor = get_db().cursor()
        cursor.execute('DELETE FROM sms_students WHERE id = %s', (student_id,))
        get_db().commit()
        flash('Student deleted.')
        return redirect(url_for('student'))
    return redirect(url_for('login'))

# ================= ATTENDANCE ====================

@app.route("/attendance", methods=['GET', 'POST'])
def attendance():
    if 'loggedin' in session:
        cursor = get_db().cursor()
        cursor.execute('SELECT * FROM sms_classes')
        classes = cursor.fetchall()
        cursor.execute('SELECT * FROM sms_section')
        sections = cursor.fetchall()
        return render_template("attendance.html", classes=classes, sections=sections)
    return redirect(url_for('login'))

@app.route("/getClassAttendance", methods =['GET', 'POST'])
def getClassAttendance():
    if 'loggedin' in session:  
        if request.method == 'POST' and 'classid' in request.form and 'sectionid' in request.form:
        
            classid = request.form['classid']
            sectionid = request.form['sectionid']
            
            cursor = get_db().cursor()   
            
            cursor.execute('SELECT * FROM sms_classes')
            classes = cursor.fetchall() 
            
            cursor.execute('SELECT * FROM sms_section')
            sections = cursor.fetchall() 

            currentDate = date.today().strftime('%Y/%m/%d')
                     
            # cursor.execute('SELECT s.id, s.name, s.photo, s.gender, s.dob, s.mobile, s.email, s.current_address, s.father_name, s.mother_name,s.admission_no, s.roll_no, s.admission_date, s.academic_year, a.attendance_status, a.attendance_date FROM sms_students as s LEFT JOIN sms_attendance as a ON s.id = a.student_id WHERE s.class = '+classid+' AND s.section = '+sectionid)  
            cursor.execute(
                                '''
                                SELECT s.id, s.name, s.photo, s.gender, s.dob, s.mobile, s.email, 
                                    s.current_address, s.father_name, s.mother_name, 
                                    s.admission_no, s.roll_no, s.admission_date, 
                                    s.academic_year, a.attendance_status, a.attendance_date 
                                FROM sms_students AS s 
                                LEFT JOIN sms_attendance AS a 
                                    ON s.id = a.student_id 
                                WHERE s.class = %s AND s.section = %s
                                ''', 
                                (classid, sectionid)
                            )
            
            students = cursor.fetchall()   
                      
            return render_template("attendance.html", classes = classes, sections = sections, students = students, classId = classid, sectionId = sectionid)        
        elif request.method == 'POST':
            msg = 'Please fill out the form field !'        
        return redirect(url_for('attendance'))        
    return redirect(url_for('login')) 
    

@app.route("/report", methods =['GET', 'POST'])
def report():
    if 'loggedin' in session:  
        cursor = get_db().cursor()
        
        cursor.execute('SELECT * FROM sms_classes')
        classes = cursor.fetchall() 
        
        cursor.execute('SELECT * FROM sms_section')
        sections = cursor.fetchall()
        
        return render_template("report.html", classes = classes, sections = sections)
    return redirect(url_for('login'))     

# ================= 404 Error Handler ====================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# ================= MAIN ====================

if __name__ == "__main__":
    app.run(debug=True)

