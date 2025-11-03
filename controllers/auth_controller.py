from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.auth_service import AuthService
import os

auth_bp = Blueprint("auth", __name__)
smtp_user = os.getenv("EMAIL_USER")
smtp_pass = os.getenv("EMAIL_PASS")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = AuthService.verify_login(username, password)
        if user:
            session["user_id"] = user["id"]
            session["2fa_code"] = AuthService.generate_2fa_code()
            AuthService.send_2fa_email(user["email"], session["2fa_code"], smtp_user, smtp_pass)
            return redirect(url_for("auth.verify_2fa"))
        flash("Invalid username or password")
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        try:
            from repositories.user_repository import UserRepository
            UserRepository.create(username, email, password)
            flash("Account created! Please log in.")
            return redirect(url_for("auth.login"))
        except:
            flash("Username or email already exists")
    return render_template("register.html")

@auth_bp.route("/verify_2fa", methods=["GET", "POST"])
def verify_2fa():
    if request.method == "POST":
        code = request.form["code"]
        if code == session.get("2fa_code"):
            session.pop("2fa_code", None)
            return redirect(url_for("index"))
        flash("Invalid 2FA code")
    return render_template("verify_2fa.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
