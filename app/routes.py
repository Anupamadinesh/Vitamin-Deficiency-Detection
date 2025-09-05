import os
from flask import Blueprint, render_template, redirect, url_for, flash, session, request, current_app
from flask_login import login_user, logout_user, login_required, current_user

from app.forms import RegistrationForm, LoginForm
from .models import User
from . import mysql, bcrypt

from openai import OpenAI

# ✅ OpenRouter API client setup
client = OpenAI(
    api_key="keys",
    base_url="https://openrouter.ai/api/v1"  # IMPORTANT for OpenRouter
)

from app.chatbot import get_vitaminbot_response


main = Blueprint('main', __name__)

# 🏠 Home Page
@main.route('/')
def home():
    return render_template('home.html')

# 📝 Signup Page
@main.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        cur = mysql.connection.cursor()
        # Check if email already exists
        cur.execute("SELECT * FROM users1 WHERE email = %s", (email,))
        existing_user = cur.fetchone()

        if existing_user:
            flash('Email already exists. Please login or use another email.', 'warning')
            return redirect(url_for('main.signup'))

        # Insert new user into DB
        cur.execute("INSERT INTO users1 (username, email, password) VALUES (%s, %s, %s)",
                    (username, email, password))
        mysql.connection.commit()
        cur.close()

        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('main.login'))

    return render_template('signup.html', form=form)

# 🔐 Login Page
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully!')   
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login failed. Check email and password.', 'danger')
    return render_template('login.html', form=form)

# 🚪 Logout Route
@main.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

# 🧠 Dashboard

@main.route('/dashboard')
@login_required
def dashboard():
 return render_template('dashboard.html', vitamin= "No prediction yet")
    


# 📄 About Us Page
@main.route('/about')
def about():
    return render_template('about.html')

# 📞 Contact Page
@main.route('/contact')
def contact():
    return render_template('contact.html')

# 💬 VitaminBot Chat Page
@main.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    response = ""
    if request.method == "POST":
        user_input = request.form["message"]
        response = get_vitaminbot_response(user_input)
    return render_template("chatbot.html", response=response)

