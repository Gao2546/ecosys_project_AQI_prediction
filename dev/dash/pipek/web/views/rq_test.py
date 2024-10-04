from flask import Blueprint, render_template, redirect , request , jsonify ,flash

from .. import redis_rq

from pipek.jobs import hello_rq
import os

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
        f = request.files['file']
        if not f:
            error_message = "Please choose a picture first."
            return render_template("model.html", error=error_message)
        f.save(os.path.join("./images",f.filename)) 

    return render_template("model.html")


@module.route("/dashboard")
def dashboard():
    return render_template("page2.html")

@module.route("/model")
def model():
    return render_template("model.html")