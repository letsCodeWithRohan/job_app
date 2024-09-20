from flask import Flask,render_template,url_for,flash,redirect,session,send_from_directory,request,jsonify
from flask_mysqldb import MySQL
import os

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = 'static/uploads/'
app.secret_key = "Top Secret"
app.config["MYSQL_HOST"] = 'localhost'
app.config["MYSQL_USER"] = 'root'
app.config["MYSQL_PASSWORD"] = ''
app.config["MYSQL_DB"] = 'Job_app'

mysql = MySQL(app)

@app.route("/",methods=["GET","POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        data = request.form["search"]
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id,title,(SELECT profile FROM companies WHERE id = company_id),requirement,location,salary,job_type,no_of_positions,description,created_date,(SELECT name FROM companies WHERE id = company_id) FROM jobs WHERE title LIKE %s ",('%' + data + '%',))
        jobs = cursor.fetchall()
        job_data = []
        for item in jobs:
            empty = {}
            empty["id"] = item[0]
            empty["role"] = item[1]
            empty["profile"] = item[2]
            empty["requirement"] = item[3]
            empty["location"] = item[4]
            empty["salary"] = item[5]
            empty["type"] = item[6]
            empty["positions"] = item[7]
            empty["description"] = item[8]
            empty["date"] = item[9]
            empty["name"] = item[10]
            job_data.append(empty)
        return render_template("browse.html",jobs=job_data)

# Done
@app.route("/jobs_filter",methods=["GET","POST"])
def job_filter():
    if request.method == "POST":
        data = request.form
        cursor = mysql.connection.cursor()
        query = '''SELECT id, 
        title, 
        (SELECT profile FROM companies WHERE companies.id = jobs.company_id) AS company_profile, 
        requirement, 
        location, 
        salary, 
        job_type, 
        no_of_positions, 
        description, 
        created_date, 
        (SELECT name FROM companies WHERE companies.id = jobs.company_id) AS company_name FROM jobs WHERE 1=1 '''

        # Adding conditions dynamically based on the data filters
        params = []

        if data["location"] != "all":
            query += " AND location = %s"
            params.append(data["location"])

        if data["salary"] == "under10":
            query += " AND salary < 10"
        elif data["salary"] == "10to50":
            query += " AND salary BETWEEN 10 AND 50"
        elif data["salary"] == "50plus":
            query += " AND salary > 50"

        if data["type"] != "all":
            query += " AND job_type = %s"
            params.append(data["type"])

        # Execute the query with parameters
        cursor.execute(query, tuple(params))
        data = cursor.fetchall()
        cursor.execute("SELECT DISTINCT location from jobs")
        locations = cursor.fetchall()
        cursor.execute("SELECT DISTINCT title from jobs")
        roles = cursor.fetchall()
        job_data = []
        for item in data:
            empty = {}
            empty["id"] = item[0]
            empty["role"] = item[1]
            empty["profile"] = item[2]
            empty["requirement"] = item[3]
            empty["location"] = item[4]
            empty["salary"] = item[5]
            empty["type"] = item[6]
            empty["positions"] = item[7]
            empty["description"] = item[8]
            empty["date"] = item[9]
            empty["name"] = item[10]
            job_data.append(empty)
        return render_template("job_filter.html",data=job_data,locations=locations,roles=roles)

@app.route("/edit_job/<int:id>",methods=["GET","POST"])
def edit_job(id):
    if request.method == "GET":
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id,name from companies WHERE recruiter_id = %s",(session['id'],))
        own_companies = cursor.fetchall()
        cursor.execute("SELECT id,title,requirement,location,salary,job_type,no_of_positions,description,created_date,experience FROM jobs WHERE id = %s",(id,))
        item = cursor.fetchone()
        empty = {}
        empty["id"] = item[0]
        empty["role"] = item[1]
        empty["requirement"] = item[2]
        empty["location"] = item[3]
        empty["salary"] = item[4]
        empty["type"] = item[5]
        empty["positions"] = item[6]
        empty["description"] = item[7]
        empty["date"] = item[8]
        empty["experience"] = item[9]
        cursor.close()
        return render_template("edit_job.html",data=empty,cdata=own_companies)
    else:
        data = request.form
        cursor = mysql.connection.cursor()
        query = "UPDATE jobs SET title=%s,company_id=%s,requirement=%s,location=%s,salary=%s,job_type=%s,no_of_positions=%s,description=%s,experience=%s WHERE id = %s"
        cursor.execute(query,(data["title"],data["com_id"],data["requirements"],data["location"],data["salary"],data["type"],data["positions"],data["description"],data["experience"],id))
        mysql.connection.commit()
        flash("Job Edited successfully")
        return redirect(url_for("admin_jobs"))

@app.route("/edit_company/<int:id>",methods=["GET","POST"])
def edit_company(id):
    if request.method == "GET":
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT name,profile,location,website,description,id FROM companies WHERE id =%s",(id,))
        data = cursor.fetchone()
        cursor.close()
        return render_template('edit_company.html',data=data)
    else:
        data = request.form
        profile=request.files["profile"]
        cursor = mysql.connection.cursor()
        if profile.filename == '':
            cursor.execute("UPDATE companies SET name=%s,location=%s,website=%s,description=%s WHERE id =%s",(data["name"],data['location'],data['website'],data['description'],id))
        else:
            cursor.execute("UPDATE companies SET name=%s,location=%s,website=%s,description=%s,profile=%s WHERE id =%s",(data["name"],data['location'],data['website'],data['description'],profile.filename,id))
            profile.save(os.path.join(app.config["UPLOAD_FOLDER"],profile.filename))
        mysql.connection.commit()
        cursor.close()
        flash("Company Edited Successfully.")
        return redirect(url_for("admin_companies"))

# Done
@app.route("/jobs")
def jobs():
    if "isStudent" not in session:
        flash("Please login to view jobs.")
        return redirect(url_for("login"))
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id,title,(SELECT profile FROM companies WHERE id = company_id),requirement,location,salary,job_type,no_of_positions,description,created_date,(SELECT name FROM companies WHERE id = company_id) FROM jobs")
        data = cursor.fetchall()
        cursor.execute("SELECT DISTINCT location from jobs")
        locations = cursor.fetchall()
        cursor.execute("SELECT DISTINCT title from jobs")
        roles = cursor.fetchall()
        cursor.close()
        job_data = []
        for item in data:
            empty = {}
            empty["id"] = item[0]
            empty["role"] = item[1]
            empty["profile"] = item[2]
            empty["requirement"] = item[3]
            empty["location"] = item[4]
            empty["salary"] = item[5]
            empty["type"] = item[6]
            empty["positions"] = item[7]
            empty["description"] = item[8]
            empty["date"] = item[9]
            empty["name"] = item[10]
            job_data.append(empty)
        return render_template("jobs.html",data=job_data,locations=locations,roles=roles)

@app.route("/edit_profile",methods=["GET","POST"])
def edit_profile():
    if request.method == "POST":
        data = request.form
        profile=request.files["profile"]
        resume=request.files["resume"]
        qry = "UPDATE students SET name=%s,password=%s,phone=%s,profile=%s,bio=%s,resume=%s WHERE id = %s"
        cursor=mysql.connection.cursor()
        if profile.filename == '' and resume.filename == '':
            cursor.execute("UPDATE students SET name=%s,password=%s,phone=%s,bio=%s WHERE id = %s",(data["name"],data['password'],data['phone'],data['bio'],session['id']))
        elif profile.filename != '' and resume.filename == '':
            cursor.execute("UPDATE students SET name=%s,password=%s,phone=%s,bio=%s,profile=%s WHERE id = %s",(data["name"],data['password'],data['phone'],data['bio'],profile.filename,session['id']))
            session["profile"] = profile.filename
            profile.save(os.path.join(app.config["UPLOAD_FOLDER"],profile.filename))
        elif profile.filename == '' and resume.filename != '':
            cursor.execute("UPDATE students SET name=%s,password=%s,phone=%s,bio=%s,resume=%s WHERE id = %s",(data["name"],data['password'],data['phone'],data['bio'],resume.filename,session['id']))
            resume.save(os.path.join(app.config["UPLOAD_FOLDER"],resume.filename))
        else:
            cursor.execute(qry,(data["name"],data['password'],data['phone'],profile.filename,data['bio'],resume.filename,session['id']))
            profile.save(os.path.join(app.config["UPLOAD_FOLDER"],profile.filename))
            session["profile"] = profile.filename
            resume.save(os.path.join(app.config["UPLOAD_FOLDER"],resume.filename))
        mysql.connection.commit()
        return redirect(url_for("profile"))

@app.route("/profile/")
def profile():
    if "isStudent" not in session:
        return redirect(url_for("login"))
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM students Where id = %s",(session["id"],))
        data = cursor.fetchone()
        cursor.execute("SELECT id,name FROM skills WHERE student_id = %s",(session["id"],))
        skills= cursor.fetchall()
        cursor.execute('''SELECT 
            applications.applied_date, 
            jobs.title, 
            companies.name AS company_name, 
            applications.status
        FROM 
            applications
        JOIN 
            jobs ON applications.job_id = jobs.id
        JOIN 
            companies ON jobs.company_id = companies.id
        WHERE 
            applications.student_id = %s;''',(session["id"],))
        applications = cursor.fetchall()
        user = {
            "id":data[0],
            "name":data[1],
            "email":data[2],
            "password":data[3],
            "phone":data[4],
            "profile":data[5],
            "bio":data[6],
            "resume":data[7],
            "date":data[8]
        }
        return render_template("profile.html",user=user,skills=skills,applications=applications)

@app.route('/uploads/<filename>')
def serve_image(filename):
    return send_from_directory('static/uploads', filename)

# Done
@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        data = request.form
        profile = request.files["profile"]
        if data["type"] == "Student":
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT COUNT(*) from students WHERE email = %s",(data["email"],))
            emailexist = cursor.fetchone()
            if emailexist[0] > 0 :
                flash("Email already used")
                return redirect(url_for("register"))
            else: 
                qry = "INSERT INTO students(name, email, password, phone, profile) VALUES (%s,%s,%s,%s,%s)"
                cursor.execute(qry,(data["name"],data["email"],data["password"],data["phone"],profile.filename))
                profile.save(os.path.join(app.config["UPLOAD_FOLDER"],profile.filename))
                mysql.connection.commit()
                cursor.close()
                flash("Registered Successfully.")
                return redirect(url_for("login"))
        else:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT COUNT(*) from students WHERE email = %s",(data["email"],))
            emailexist = cursor.fetchone()
            if emailexist[0] > 0 :
                flash("Email already used")
                return redirect(url_for("register"))
            else: 
                qry = "INSERT INTO recruiters(name, email, password, phone, profile) VALUES (%s,%s,%s,%s,%s)"
                cursor.execute(qry,(data["name"],data["email"],data["password"],data["phone"],profile.filename))
                profile.save(os.path.join(app.config["UPLOAD_FOLDER"],profile.filename))
                mysql.connection.commit()
                cursor.close()
                flash("Registered Successfully.")
                return redirect(url_for("login"))

# Done
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        data = request.form
        if data["type"] == "Student":
            cursor = mysql.connection.cursor()
            qry = "SELECT email,id,password,profile FROM students WHERE email = %s"
            cursor.execute(qry,(data["email"],))
            response = cursor.fetchone()
            if response == None :
                flash("No user found")
                return redirect(url_for("login"))
            else:
                if data["email"] == response[0] and data["password"] == response[2]:
                    session["id"] = response[1]
                    session["email"] = response[0]
                    session["profile"] = response[3]
                    session["isStudent"] = True
                    return redirect(url_for("index"))
                elif response[0] == data["email"] and response[2] != data["password"]:
                    flash("Password Wrong !")
                    return redirect(url_for("login"))
                else:
                    flash("Email and password Wrong !")
                    return redirect(url_for("login"))
        else:
            cursor = mysql.connection.cursor()
            qry = "SELECT email,id,password,profile FROM recruiters WHERE email = %s"
            cursor.execute(qry,(data["email"],))
            response = cursor.fetchone()
            if response == None :
                flash("No user found")
                return redirect(url_for("login"))
            else:
                if response[0] == data["email"] and response[2] == data["password"]:
                    session["id"] = response[1]
                    session["email"] = response[0]
                    session["profile"] = response[3]
                    session["isAdmin"] = True
                    return redirect(url_for("admin_companies"))
                elif response[0] == data["email"] and response[2] != data["password"]:
                    flash("Password Wrong !")
                    return redirect(url_for("login"))
                else:
                    flash("Email and password Wrong !")
                    return redirect(url_for("login"))

# Done
@app.route("/admin/")
def admin_companies():
    if "isAdmin" not in  session:
        return redirect(url_for("login"))
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id,profile,name,created_date from companies")
        data = cursor.fetchall()
        return render_template("admin_companies.html",data=data)

# Done
@app.route("/admin/jobs")
def admin_jobs():
    if "isAdmin" not in  session:
        return redirect(url_for("login"))
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id,title,created_date from jobs")
        data = cursor.fetchall()
        cursor.execute("SELECT id,name from companies WHERE recruiter_id = %s",(session['id'],))
        own_companies = cursor.fetchall()
        cursor.execute("SELECT jobs.id AS job_id, companies.name AS company_name, jobs.title AS job_title, jobs.created_date AS job_created_date FROM jobs JOIN companies ON jobs.company_id = companies.id WHERE companies.recruiter_id = %s",(session['id'],))
        job_data = cursor.fetchall()
        return render_template("admin_jobs.html",data=data,cdata=own_companies,job_data=job_data)

# Done
@app.route("/admin/profile",methods=["GET","POST"])
def admin_profile():
    if "isAdmin" not in  session:
        return redirect(url_for("login"))
    else:
        if request.method == "GET":
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT id,name,bio,profile,email,phone,password FROM recruiters WHERE id = %s",(session["id"],))
            data =  cursor.fetchone()
            userdata = {
                "id":data[0],
                "name":data[1],
                "bio":data[2],
                "profile":data[3],
                "email":data[4],
                "phone":data[5],
                "password":data[6]
            }
            return render_template("admin_profile.html",data=userdata)
        else:
            data = request.form
            profile = request.files["profile"]
            cursor = mysql.connection.cursor()
            if profile.filename == '':
                cursor.execute("UPDATE recruiters SET password=%s,phone=%s,bio=%s,name=%s WHERE id = %s",(data['password'],data['phone'],data['bio'],data['name'],session["id"]))
            else:
                cursor.execute("UPDATE recruiters SET password=%s,phone=%s,bio=%s,name=%s,profile=%s WHERE id = %s",(data['password'],data['phone'],data['bio'],data['name'],profile.filename,session["id"]))
                profile.save(os.path.join(app.config["UPLOAD_FOLDER"],profile.filename))
                session["profile"] = profile.filename
            mysql.connection.commit()
            return redirect(url_for("admin_profile"))

# Done
@app.route("/job_info/<int:id>")
def job_info(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id,title,(SELECT name FROM companies WHERE id = company_id),requirement,location,salary,job_type,no_of_positions,description,created_date,experience FROM jobs WHERE id = %s",(id,))
    data = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) AS total_applicants FROM applications WHERE job_id = %s",(id,))
    applicants = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) AS total_applicants FROM applications WHERE job_id = %s",(id,))
    applicants = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) AS is_applied FROM applications WHERE job_id= %s AND student_id = %s", (id, session["id"]))
    result = cursor.fetchone()
    if result[0] > 0:
        applied = True
    else:
        applied = False
    cursor.close()
    return render_template("job_info.html",data=data,applicants=applicants,applied=applied)

# Done
@app.route("/apply/<int:id>")
def apply(id):
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO applications (job_id,student_id) VALUES (%s,%s)",(id,session["id"]))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for("job_info",id=id))

# Done
@app.route("/admin/company/create",methods=["POST"])
def add_company():
    if request.method == "POST":
        data = request.form
        profile = request.files["profile"]
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO companies(recruiter_id, name, profile, website, location, description) VALUES (%s,%s,%s,%s,%s,%s)",(session["id"],data["name"],profile.filename,data["website"],data["location"],data["description"]))
        profile.save(os.path.join(app.config["UPLOAD_FOLDER"],profile.filename))
        mysql.connection.commit()
        flash("Company Successfully Added")
        return redirect(url_for("admin_companies"))

# Done
@app.route("/admin/job/create",methods=["POST"])
def add_job():
    if request.method == "POST":
        data = request.form
        cursor = mysql.connection.cursor()
        query = "INSERT INTO jobs(title, company_id, requirement, location, salary, job_type, no_of_positions, description, experience) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(query,(data["title"],data["com_id"],data["requirements"],data["location"],data["salary"],data["type"],data["positions"],data["description"],data["experience"]))
        mysql.connection.commit()
        flash("Job added successfully")
        return redirect(url_for("admin_jobs"))
    
# Done
@app.route("/delete_company/<int:id>")
def delete_company(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM companies WHERE id = %s",(id,))
    mysql.connection.commit()
    flash("Company Successfully Deleted")
    return redirect(url_for("admin_companies"))

@app.route("/delete_job/<int:id>")
def delete_job(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = %s",(id,))
    mysql.connection.commit()
    flash("Job Successfully Deleted")
    return redirect(url_for("admin_jobs"))

@app.route("/change_status/<int:id>",methods=["POST"])
def change_st(id):
    if request.method == "POST":
        data = request.form["status"]
        cursor=mysql.connection.cursor()
        cursor.execute("UPDATE applications SET status = %s WHERE id = %s",(data,id))
        mysql.connection.commit()
        return redirect(url_for("admin_jobs"))

@app.route("/applicants/<int:id>")
def applicants(id):
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT 
        applications.id AS application_id,
        students.profile, 
        students.resume, 
        students.name, 
        students.email, 
        students.phone, 
        applications.status, 
        applications.applied_date
    FROM 
        applications
    JOIN 
        students ON applications.student_id = students.id
    WHERE 
        applications.job_id = %s;
    ''',(id,))
    applicants = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM applications WHERE job_id = %s",(id,))
    counts = cursor.fetchone()
    cursor.close()
    return render_template("applicants.html",counts=counts,applicants=applicants)

# Done
@app.route("/add_skill",methods=["POST"])
def add_skill():
    if request.method == "POST":
        data = request.form
        cursor =mysql.connection.cursor()
        cursor.execute("INSERT INTO skills (student_id,name) VALUES (%s,%s)",(session["id"],data["name"]))
        mysql.connection.commit()
        return redirect(url_for("profile"))
    
# Done    
@app.route("/d_skill/<int:id>/")
def d_skill(id):
    cursor =mysql.connection.cursor()
    cursor.execute("DELETE FROM skills WHERE id = %s",(id,))
    mysql.connection.commit()
    return redirect(url_for("profile"))

@app.route("/logout")
def logout():
    session.pop("id",None)
    session.pop("email",None)
    session.pop("isStudent",None)
    session.pop("profile",None)
    return redirect(url_for("login"))

@app.route("/logout_admin")
def logout_admin():
    session.pop("id",None)
    session.pop("email",None)
    session.pop("isAdmin",None)
    session.pop("profile",None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')