from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import string, random, qrcode, os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Ensure QR code directory exists
os.makedirs('static/qrcodes', exist_ok=True)

# --------------------- Models ---------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500))
    short_id = db.Column(db.String(6), unique=True)
    clicks = db.Column(db.Integer, default=0)
    expiry_date = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# --------------------- QR Code Generator ---------------------
def generate_qr_code(short_url, filename):
    img = qrcode.make(short_url)
    img.save(f"static/qrcodes/{filename}.png")

# --------------------- Flask-Login Loader ---------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --------------------- Routes ---------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'warning')
            return redirect('/register')
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect('/')
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        url = request.form.get('url')
        expiry = request.form.get('expiry_date')

        # Generate short ID
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        while URL.query.filter_by(short_id=code).first():
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

        # Handle expiry date
        expiry_date = datetime.strptime(expiry, '%Y-%m-%dT%H:%M') if expiry else None

        short_url = request.host_url + code
        generate_qr_code(short_url, code)

        new_url = URL(
            original_url=url,
            short_id=code,
            expiry_date=expiry_date,
            user_id=current_user.id
        )
        db.session.add(new_url)
        db.session.commit()
        flash(f'Short URL created: {short_url}', 'success')

    urls = URL.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', urls=urls)

@app.route('/<short_id>')
def redirect_to_original(short_id):
    link = URL.query.filter_by(short_id=short_id).first()
    if not link:
        return "Link not found", 404
    if link.expiry_date and datetime.utcnow() > link.expiry_date:
        return "This link has expired.", 410
    link.clicks += 1
    db.session.commit()
    return redirect(link.original_url)

# --------------------- Main ---------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
