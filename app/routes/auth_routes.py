from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User
from ..db import db
from ..forms import RegisterForm, LoginForm

auth = Blueprint("auth", __name__)

@auth.route('/admin', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Logged in successfully!", "success")
            if user.is_admin:
                return redirect(url_for("admin.dashboard"))
            else:
                return redirect(url_for("user.dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html", form=form)



@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash("Username already exists. Try a different one.", "danger")
            return redirect(url_for("auth.register"))
        new_user = User(
            username=form.username.data,
            password=generate_password_hash(form.password.data),
            is_admin=False
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Logged in successfully!", "success")
            if user.is_admin:
                return redirect(url_for("admin.dashboard"))
            else:
                return redirect(url_for("user.dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
