from flask import Blueprint, render_template, redirect

module = Blueprint("site", __name__)


@module.route("/")
def index():
    return "Hello world"
