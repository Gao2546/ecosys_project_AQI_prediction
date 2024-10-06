from flask import Blueprint, render_template, redirect , url_for

module = Blueprint("site", __name__)


@module.route("/")
def index():
    return redirect(url_for('schematic.home'))
