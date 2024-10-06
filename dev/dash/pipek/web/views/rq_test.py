from flask import Blueprint, render_template, redirect, request, jsonify, flash, session, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField ,EmailField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from .. import redis_rq
from pipek.jobs import hello_rq, Schematics_predict
import os
from datetime import datetime
from ... import models
import pickle

module = Blueprint("rq-test", __name__, url_prefix="/rq-test")
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

job_id = 0

# Route for job testing (existing route)
@module.route("/")
def index():
    global job_id
    job_id += 1
    job = redis_rq.redis_queue.queue.enqueue(
        hello_rq.say_hello_rq,
        args=(f"thanathip - {job_id}",),
        job_id=f"hello-{job_id}",
        timeout=600,
        job_timeout=600,
    )
    return f"Hello world {job.id}"

@module.route("/state")
def check_job_state():
    job = redis_rq.redis_queue.get_job(f"hello-{job_id}")
    return f"Hello world {job.id} {job.result}"

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
    # form_reg = RegisterForm()
    form_log = LoginForm()
    print("testtttttttt")
    # if form_reg.validate_on_submit():
    #     username = form_reg.username.data
    #     password = form_reg.password.data
    #     email = form_reg.email.data

    #     db = models.db
    #     Register = models.User( id = 1,
    #                             username = username,
    #                             password = password,
    #                             email = email)
    #     print(Register.username)
    #     print(Register.email)
    #     # Register.username = username
    #     # Register.password = password
    #     # Register.email = email

    #     db.session.add(Register)
    #     db.session.commit()
        
    #     # Add the new user to in-memory dictionary
    #     # users[username] = password
    #     flash(f'Account created for {username}!', 'success')
    #     return redirect(url_for('rq-test.login'))
    if request.method == "POST":
        if form_log.username.data != None:
            username = form_log.username.data
            password = form_log.password.data

            db = models.db
            User = db.session.execute(
            db.select(models.User).where(models.User.username == username)
            ).scalars().fetchall()

            # Check credentials
            if (username == User[0].username) and (User[0].password == password):
                session['username'] = username  # Store user in session
                flash(f'Welcome, {username}!', 'success')
                return redirect(url_for('rq-test.home'))  # Redirect to home
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
                db.session.add(Register)
                db.session.commit()
                # Add the new user to in-memory dictionary
                users[username] = password
                flash(f'Account created for {username}!', 'success')
                return redirect(url_for('rq-test.login'))
        
    # if form_log.validate_on_submit():
    #     username = form_log.username.data
    #     password = form_log.password.data

    #     db = models.db
    #     User = db.session.execute(
    #     db.select(models.users.User).order_by(models.users.User.id)
    #     ).scalars()

    #     # Check credentials
    #     if (username == User.username) and (User.password == password):
    #         session['username'] = username  # Store user in session
    #         flash(f'Welcome, {username}!', 'success')
    #         return redirect(url_for('rq-test.home'))  # Redirect to home
    #     else:
    #         flash('Invalid username or password', 'danger')

    return render_template('register.html',form_reg=form_reg )

# Home route (requires login)
@module.route("/home")
def home():
    if 'username' not in session:
        return redirect(url_for('rq-test.login'))
    db = models.db
    history_data = db.session.execute(
        db.select(models.Output).where(models.Output.username == session['username']).order_by(models.Output.created_date)
    ).scalars().fetchall()
    return render_template("home.html",history_data = history_data)

@module.route('/delete/<int:id>', methods=['POST'])
def delete_record(id):
    if 'username' not in session:
        return redirect(url_for('rq-test.login'))
    
    db = models.db
    record_to_delete = db.session.get(models.Output, id)
    if record_to_delete:
        db.session.delete(record_to_delete)
        db.session.commit()
        flash("Record deleted successfully", "success")
    else:
        flash("Record not found", "danger")

    return redirect(url_for('rq-test.home'))


# Route to logout
@module.route("/logout")
def logout():
    session.pop('username', None)  # Clear session
    flash('You have been logged out.', 'info')
    return redirect(url_for('rq-test.login'))

@module.route('/success', methods=['POST'])   
def success():
    global custom_format  
    if 'username' not in session:
        return redirect(url_for('rq-test.login'))
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
        return redirect(url_for('rq-test.login'))
    return render_template("dashboard.html")

@module.route("/model")
def model():
    if 'username' not in session:
        return redirect(url_for('rq-test.login'))
    return render_template("model.html",display = False,paths = None)

@module.route("/result/<int:id>",methods=['GET','POST'])
def result(id):
    if 'username' not in session:
        return redirect(url_for('rq-test.login'))
    db = models.db
    record_to_data = db.session.get(models.Output, id)
    # if len(record_to_data.filename) > 0:
    path = [p.replace("./pipek/web/static","").strip('"') for p in record_to_data.filename.strip('{}').split(",")]
    # else:
    #     path = [record_to_data.filename.strip('{}').strip('"'),]
    # output_files = [os.path.join(output_path, imgpath) for imgpath in os.listdir(record_to_data.path) if imgpath.endswith(('.png', '.jpg', '.jpeg'))]
    return render_template("result.html",list_of_image_path = path,list_of_image_info = record_to_data.results)