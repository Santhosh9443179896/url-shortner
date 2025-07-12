# 🔗 Flask URL Shortener

A simple and elegant Flask-based web application that lets users register, log in, shorten URLs, track clicks, and generate QR codes — all with expiry date support!

## 🚀 Features

- ✅ User Registration & Login (Secure with hashed passwords)
- 🔐 Dashboard for logged-in users
- ✂️ URL Shortening with random 6-character codes
- 📈 Click tracking for each URL
- 🗓️ Optional expiry date for shortened URLs
- 📷 QR code generation for each short URL
- 🎨 Beautiful Bootstrap-based UI

## 🧱 Tech Stack

- Python + Flask
- SQLite + SQLAlchemy
- Flask-Login (Authentication)
- Bootstrap 5 (UI)
- qrcode (QR image generation)

## 📦 Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/flask-url-shortener.git
cd flask-url-shortener

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
