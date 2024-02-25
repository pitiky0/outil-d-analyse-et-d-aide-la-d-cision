import re
import math
import random
import string
from database import User, db
from passlib.context import CryptContext
from werkzeug.security import generate_password_hash
from flask import request, flash, redirect, url_for, render_template


def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        errors = []  # Store validation errors

        if not name:
            errors.append('Please enter your name.')
        if not email:
            errors.append('Please enter your email address.')
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            errors.append('Please enter a valid email address.')
        if not password:
            errors.append('Please enter a password.')
        if not confirm_password:
            errors.append('Please confirm your password.')
        if password != confirm_password and len(confirm_password) != 0:
            errors.append('Passwords do not match.')

        if errors:
            return render_template('auth/signup.html', errors=errors)

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already exists.', 'error')
            return redirect(url_for('signup'))

        # Create and save new user
        try:
            new_user = User(name, email, password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))  # Redirect to login page
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'error')
            return redirect(url_for('signup'))

    return render_template('auth/signup.html')


def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        errors = []  # Store validation errors

        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            errors.append('Please enter a valid email address.')
        if not password:
            errors.append('Please enter a password.')

        if errors:
            return render_template('auth/login.html', errors=errors)

        user = User.query.filter_by(email=email).first()
        if user and user.verify_password(password):
            # Implement session management here
            # flash('Login successful!', 'success')
            return redirect(url_for('index'))  # Redirect to dashboard or desired page
        else:
            flash('Invalid email or password', 'error')

    return render_template('auth/login.html')


def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        # Generate a random verification code
        verification_code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))

        # Implement user lookup logic here (replace with your actual logic)
        user = User.query.filter_by(email=email).first()
        if user:
            # Store verification code in user object or database (securely!)
            user.verification_code = verification_code
            db.session.commit()

            # Send verification email with code
            from app import send_verification_email

            send_verification_email(email, verification_code)

            flash('A verification code has been sent to your email address.', 'success')
            return redirect(url_for('verify_password_reset', email=email))  # Redirect to verification page
        else:
            flash('User not found.', 'error')

    return render_template('auth/forgot-password.html')


def verify_password_reset(email):
    # Locate the user with appropriate error handling
    user = User.query.filter_by(email=email).first()

    if not user:
        flash('User not found.', 'error')
        return render_template('auth/forgot-password.html', email=email)

    if request.method == 'POST':
        verification_code = request.form['verification_code']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        errors = []  # Store validation errors

        if not verification_code or len(verification_code) == 0:
            errors.append('Please enter a valid verification code.')
        if not new_password:
            errors.append('Please enter a password.')
        if not confirm_password:
            errors.append('Please confirm your password.')
        if new_password != confirm_password and len(confirm_password) != 0:
            errors.append('Passwords do not match.')

        if errors:
            return render_template('auth/login.html', errors=errors)

        if user.verification_code != verification_code:
            flash('Invalid verification code.', 'error')
            return render_template('auth/verify-password-reset.html', email=email)

        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/verify-password-reset.html', email=email)

        # Validate password strength (optional)
        # if not is_password_strong(new_password):
        #     flash('Password strength is not sufficient.', 'error')
        #     return render_template('auth/verify-password-reset.html', email=email)

        # Hash the new password securely
        user.password_hash = generate_password_hash(new_password)

        try:
            # Commit changes to the database
            db.session.commit()
            flash('Your password has been reset successfully. Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Error saving password: ' + str(e), 'error')
            db.session.rollback()  # Revert changes if commit fails
            return render_template('auth/verify-password-reset.html', email=email)
    else:
        return render_template('auth/verify-password-reset.html', email=email)


def is_password_strong(password):
    pwd_context = CryptContext(schemes=['bcrypt'])  # Use bcrypt for secure hashing

    # Length requirements
    min_length = 8  # Adjust based on your security policy
    if len(password) < min_length:
        return False

    # Character class requirements
    has_uppercase = any(char.isupper() for char in password)
    has_lowercase = any(char.islower() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_symbol = any(char not in string.ascii_letters + string.digits for char in password)

    # Common pattern checks
    common_patterns = [
        'qwertyuiop', 'asdfghjkl', 'zxcvbnm',  # Keyboard sequences
        '1234567890', '987654321',  # Numeric sequences
        'password', '123456', 'iloveyou',  # Common dictionary words
    ]
    pattern_matches = sum(pattern in password for pattern in common_patterns)

    # Password entropy estimation using Shannon entropy
    entropy = 0
    for char in set(password):
        char_prob = password.count(char) / len(password)
        entropy += char_prob * math.log2(char_prob)

    # Password strength evaluation and detailed feedback
    strength = len(
        password) >= min_length and has_uppercase and has_lowercase and has_digit and has_symbol and entropy >= 6  # Adjust criteria based on your security policy
    messages = []
    if not has_uppercase:
        messages.append("Include at least one uppercase letter.")
    if not has_lowercase:
        messages.append("Include at least one lowercase letter.")
    if not has_digit:
        messages.append("Include at least one digit.")
    if not has_symbol:
        messages.append("Include at least one symbol (e.g., !@#$%^&*).")
    if pattern_matches > 0:
        messages.append("Avoid using common patterns from the keyboard or dictionary.")
    if entropy < 6:
        messages.append("Increase the password entropy by using a wider variety of characters.")

    if messages:
        return False
    else:
        return True
