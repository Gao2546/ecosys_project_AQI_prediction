from flask import Blueprint, render_template, redirect
from flask import Blueprint, render_template, redirect , request

from .. import redis_rq

from pipek.jobs import hello_rq , Schematics_predict
import os
from datetime import datetime

module = Blueprint("rq-test", __name__, url_prefix="/rq-test")

job_id = 0


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

# @module.route("/page1")
# def page1():
#     return render_template("page1.html")

@module.route("/home")
def home():
    return render_template("home.html")

@module.route('/success', methods = ['POST'])   
def success():  
    if request.method == 'POST':  
        path = "./images" 
        user = "athip"
        custom_format = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        if not os.path.exists(os.path.join(path,user)):
            os.makedirs(os.path.join(path,user))
        full_path = os.path.join(path,user,custom_format)
        os.makedirs(full_path)
        files = request.files.getlist("file") 
        for file in files: 
            file.save(os.path.join(full_path,file.filename))
        job = redis_rq.redis_queue.queue.enqueue(
        Schematics_predict.prediction,
        args=(full_path,),
        job_id=f"predict-{custom_format}",
        timeout=600,
        job_timeout=600,
        )
    
    return redirect("home")

@module.route("/dashboard")
def dashboard():
    return render_template("page2.html")