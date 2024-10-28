import os
from flask import Flask, render_template, request, redirect, url_for, session
from web.routes import init_app
from web import utils

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize routes
init_app(app)

if __name__ == '__main__':
    app.run(debug=True)