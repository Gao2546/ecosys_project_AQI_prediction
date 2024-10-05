from flask import Blueprint, render_template, redirect, request, jsonify, flash, session, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from .. import redis_rq
from pipek.jobs import hello_rq, Schematics_predict
import os
from datetime import datetime
from ... import models

module = Blueprint("rq-test", __name__, url_prefix="/rq-test")

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
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
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

# Login route
@module.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Check credentials
        if username in users and users[username] == password:
            session['username'] = username  # Store user in session
            flash(f'Welcome, {username}!', 'success')
            return redirect(url_for('rq-test.home'))  # Redirect to home
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

# Register route
@module.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Add the new user to in-memory dictionary
        users[username] = password
        flash(f'Account created for {username}!', 'success')
        return redirect(url_for('rq-test.login'))
    return render_template('register.html', form=form)

# Home route (requires login)
@module.route("/home")
def home():
    if 'username' not in session:
        return redirect(url_for('rq-test.login'))
    
    db = models.db
    return render_template("home.html")

# Route to logout
@module.route("/logout")
def logout():
    session.pop('username', None)  # Clear session
    flash('You have been logged out.', 'info')
    return redirect(url_for('rq-test.login'))

# Success route for file upload (existing)
@module.route('/success', methods=['POST'])   
def success():  
    if request.method == 'POST':  
        path = "./images" 
        user = "athip"
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
        job = redis_rq.redis_queue.queue.enqueue(
            Schematics_predict.prediction,
            args=(full_path_input,full_path_output,),
            job_id=f"predict-{custom_format}",
            timeout=600,
            job_timeout=600,
        )
    return redirect("home")

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
    return render_template("model.html")
