import os
import secrets
from functools import wraps
from pathlib import Path
from flask import Flask, render_template, request, redirect, session, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv

db = SQLAlchemy()
csrf = CSRFProtect()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('user_id'):
            return redirect('/login')
        return view(*args, **kwargs)
    return wrapped

def make_app(title, description, config=None):
    load_dotenv()
    app = Flask(__name__)
    Path(app.instance_path).mkdir(exist_ok=True)
    key = os.getenv('SECRET_KEY')
    if not key:
        key_file = Path(app.instance_path) / 'session.key'
        if not key_file.exists():
            key_file.write_text(secrets.token_hex(32), encoding='utf-8')
        key = key_file.read_text(encoding='utf-8').strip()
    database = os.getenv('DATABASE_URL', 'sqlite:///project.db')
    if database.startswith('postgresql://'):
        database = database.replace('postgresql://', 'postgresql+psycopg://', 1)
    app.config.update(SECRET_KEY=key, SQLALCHEMY_DATABASE_URI=database,
        SQLALCHEMY_TRACK_MODIFICATIONS=False, SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax', MAX_CONTENT_LENGTH=1024*1024,
        APP_TITLE=title, APP_DESCRIPTION=description, HAS_AUTH=True)
    if config:
        app.config.update(config)
    db.init_app(app)
    csrf.init_app(app)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username', '').strip().lower()
            password = request.form.get('password', '')
            if not (3 <= len(username) <= 40) or not username.replace('_','').isalnum() or not (8 <= len(password) <= 128):
                flash('Use a 3–40 character username and an 8–128 character password.')
                return render_template('auth.html', title='Register', register=True), 400
            user = User(username=username, password_hash=generate_password_hash(password))
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash('That username is already taken.')
                return render_template('auth.html', title='Register', register=True), 400
            session.clear()
            session['user_id'] = user.id
            return redirect('/')
        return render_template('auth.html', title='Register', register=True)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username', '').strip().lower()
            password = request.form.get('password', '')
            user = db.session.scalar(db.select(User).where(User.username == username))
            if len(password) > 128 or not user or not check_password_hash(user.password_hash, password):
                flash('Incorrect username or password.')
                return render_template('auth.html', title='Log in', register=False), 400
            session.clear()
            session['user_id'] = user.id
            return redirect('/')
        return render_template('auth.html', title='Log in', register=False)

    @app.post('/logout')
    def logout():
        session.clear()
        return redirect('/login')

    @app.errorhandler(404)
    def missing(error):
        return render_template('error.html', title='Not found', message='That item was not found.'), 404

    return app
