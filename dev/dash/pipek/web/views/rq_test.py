from flask import Blueprint, render_template, redirect, request, jsonify, flash, session, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField ,EmailField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from .. import redis_rq
from pipek.jobs import hello_rq, Schematics_predict
import os
from datetime import datetime
import time
from ... import models
import pickle
import shutil

module = Blueprint("schematic", __name__, url_prefix="/schematic")
custom_format = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

# In-memory mock user data for login/register (use a database in real-world cases)
users = {'admin': 'password123'}

# Forms for login and registration
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    # confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    email = EmailField("Email",validators=[DataRequired()])
    submit = SubmitField('Register')

    # Simulate user validation in the in-memory storage
    def validate_username(self, username):
        if username.data in users:
            raise ValidationError('Username already exists. Please choose another.')
def force_remove_readonly(func, path, excinfo):
    # This function handles the case where some files are read-only
    os.chmod(path, 0o777)  # Change the permission to writable
    func(path)

def after_session_timeout(name):
    # Your callback function to be called after session timeout
    db = models.db
    User = db.session.execute(
    db.select(models.User).where(models.User.username == name)
    ).scalars().fetchall()
    User[0].status = 0
    db.session.commit()
    print("Session has expired, performing cleanup...")
    # For example, logging out the user, clearing data, etc.
exp_time = 10

@module.before_request
def check_session_timeout():
    session.permanent = True  # Make the session permanent to apply timeout
    now = time.time()
    if "last_active" in session:
        # session.clear()
        last_active = session["last_active"] 
        # Check if the session has expired
        if (now - last_active) > exp_time:
            # Session expired, run the callback\
            if 'username' not in session:
                form_log = LoginForm()
                session["last_active"] = now
                return render_template('login.html', form_log=form_log )
            after_session_timeout(session["username"])
            # Optionally clear the session
            session.clear()
            flash("Session has timed out.")
            return redirect(url_for("schematic.login"))  # Redirect to login or any other page
    if request.endpoint in ('schematic.get_user_count','schematic.login', 'static'):  # Add any endpoint you want to ignore
        return # Skip session timeout check for these endpoints
    session["last_active"] = now  # Update last active time on each request
    flash("pass")


# Route for job testing (existing route)
@module.route("/")
def index():
    return redirect(url_for('schematic.home'))

# @module.route("/state")
# def check_job_state():
#     job = redis_rq.redis_queue.get_job(f"hello-{job_id}")
#     return f"Hello world {job.id} {job.result}"

@module.route('/user_count', methods=['GET'])
def get_user_count():
    try:
        # Read the user count from the text file
        with open('/trans/user_count.txt', 'r') as file:
            count = file.read().strip()
        print(count)
        return jsonify({'count': count})
    except FileNotFoundError:
        # If the file doesn't exist, return 0 as the default count
        return jsonify({'count': "0"})

# Login route
@module.route("/login", methods=["GET", "POST"])
def login():
    form_log = LoginForm()
    if request.method == "POST":
        if form_log.username.data != None:
            username = form_log.username.data
            password = form_log.password.data

            db = models.db
            User = db.session.execute(
            db.select(models.User).where(models.User.username == username)
            ).scalars().fetchall()

            # Check credentials
            if len(User) > 0:
                if (username == User[0].username) and (User[0].password == password):
                    session['username'] = username  # Store user in session
                    User[0].status = 1
                    db.session.commit()
                    flash(f'Welcome, {username}!', 'success')
                    return redirect(url_for('schematic.home'))  # Redirect to home
                else:
                    flash('Invalid username or password', 'danger')
    return render_template('login.html', form_log=form_log )

# Register route
@module.route("/register", methods=["GET", "POST"])
def register():
    form_reg = RegisterForm()
    # form_log = LoginForm()
    if request.method == "POST":
        print("testttttttttsss")
        if form_reg.username.data != None:
            username = form_reg.username.data
            password = form_reg.password.data
            email = form_reg.email.data
            db = models.db
            data_exit1 = db.session.execute(
                db.select(models.User).where(models.User.username == username)
            ).scalars().fetchall()
            data_exit2 = db.session.execute(
                db.select(models.User).where(models.User.email == email)
            ).scalars().fetchall()
            if (len(data_exit1) <= 0) and (len(data_exit2) <= 0):
                Register = models.User()
                Register.username = username
                Register.password = password
                Register.email = email
                Register.status = 0
                db.session.add(Register)
                db.session.commit()
                # Add the new user to in-memory dictionary
                users[username] = password
                flash(f'Account created for {username}!', 'success')
                return redirect(url_for('schematic.login'))

    return render_template('register.html',form_reg=form_reg )

# Home route (requires login)
@module.route("/home")
def home():
    # module.logger.info('Info message: Home route was accessed.')
    if 'username' not in session:
        return redirect(url_for('schematic.login'))
    db = models.db
    history_data = db.session.execute(
        db.select(models.Output).where(models.Output.username == session['username']).order_by(models.Output.created_date)
    ).scalars().fetchall()
    return render_template("home.html",history_data = history_data)

@module.route('/delete/<int:id>', methods=['POST','GET','DELETE'])
def delete_record(id):
    if 'username' not in session:
        return jsonify({'message': 'User not logged in', 'status': 'error'}), 401
    
    db = models.db
    record_to_delete = db.session.get(models.Output, id)

    if record_to_delete:
        path_to_delete = record_to_delete.path.replace("output", "")
        try:
            shutil.rmtree(path_to_delete, onerror=force_remove_readonly)
        except Exception as e:
            return jsonify({'message': f'Error deleting files: {str(e)}', 'status': 'error'}), 500

        db.session.delete(record_to_delete)
        db.session.commit()

        return jsonify({'message': 'Record deleted successfully', 'status': 'success', 'id': id}), 200
    else:
        return jsonify({'message': 'Record not found', 'status': 'error'}), 404

# Route to logout
@module.route("/logout")
def logout():
    if 'username' not in session:
        return redirect(url_for('schematic.login'))
    db = models.db
    User = db.session.execute(
    db.select(models.User).where(models.User.username == session['username'])
    ).scalars().fetchall()
    User[0].status = 0
    db.session.commit()
    session.pop('username', None)  # Clear session
    flash('You have been logged out.', 'info')
    return redirect(url_for('schematic.login'))

@module.route('/success', methods=['POST'])   
def success():
    global custom_format  
    if 'username' not in session:
        return redirect(url_for('schematic.login'))
    if request.method == 'POST':  
        path = "./pipek/web/static/images"
        user = session['username']
        custom_format = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        if not os.path.exists(os.path.join(path, user)):
            os.makedirs(os.path.join(path, user))
        full_path = os.path.join(path, user, custom_format)
        os.makedirs(full_path)
        files = request.files.getlist("file") 
        full_path_input = os.path.join(full_path,"input")
        os.makedirs(full_path_input)
        full_path_output = os.path.join(full_path,"output")
        os.makedirs(full_path_output)
        for file in files: 
            file.save(os.path.join(full_path_input, file.filename))
        
        # Queue the job and return job ID to frontend
        job = redis_rq.redis_queue.queue.enqueue(
            Schematics_predict.prediction,
            args=(full_path_input, full_path_output,session['username']),
            job_id=f"predict-{custom_format}",
            timeout=600,
            job_timeout=600,
        )
        return jsonify({"job_id": job.id, "message": "Job started!"})
    
# Add route to check job status
@module.route('/job-status/<job_id>', methods=['GET'])
def job_status(job_id):
    job = redis_rq.redis_queue.get_job(job_id)
    if job:
        if job.is_finished:
            db = models.db
            # Return success and result paths
            output_path = os.path.join("images", session['username'], custom_format , "output")
            output_list_file = os.path.join("pipek","web","static",output_path)
            output_files = [os.path.join(output_path, imgpath) for imgpath in os.listdir(output_list_file) if imgpath.endswith(('.png', '.jpg', '.jpeg'))]
            with open(os.path.join(output_list_file,"list_data"),"rb") as f:
                list_output = pickle.load(f)
            username,output_image_path,images_path,images_class = list_output

            output_table = models.Output()
            output_table.username = username
            output_table.path = output_image_path
            output_table.filename = images_path
            output_table.results = images_class
            db.session.add(output_table)
            db.session.commit()

            print(images_class)

            # class_list = db.session.execute(
            # db.select(models.Output).where((models.Output.username == session['username']) and (models.Output.path == output_list_file))
            # ).scalars().fetchall()
            return jsonify({"status": "finished", "result": output_files , "result_summary" : images_class})
        elif job.is_failed:
            return jsonify({"status": "failed"})
        else:
            return jsonify({"status": "in-progress"})
    else:
        return jsonify({"status": "unknown"})

# Additional routes (dashboard and model)
@module.route("/dashboard")
def dashboard():
    if 'username' not in session:
        return redirect(url_for('schematic.login'))
    return render_template("dashboard.html")

@module.route("/model")
def model():
    if 'username' not in session:
        return redirect(url_for('schematic.login'))
    return render_template("model.html",display = False,paths = None)

@module.route("/result/<int:id>",methods=['GET','POST'])
def result(id):
    result_id = id
    if 'username' not in session:
        return redirect(url_for('schematic.login'))
    db = models.db
    record_to_data = db.session.get(models.Output, id)
    # if len(record_to_data.filename) > 0:
    path = [p.replace("./pipek/web/static","").strip('"') for p in record_to_data.filename.strip('{}').split(",")]
    # else:
    #     path = [record_to_data.filename.strip('{}').strip('"'),]
    # output_files = [os.path.join(output_path, imgpath) for imgpath in os.listdir(record_to_data.path) if imgpath.endswith(('.png', '.jpg', '.jpeg'))]
    return render_template("result.html",list_of_image_path = path,list_of_image_info = record_to_data.results , result_id = result_id)