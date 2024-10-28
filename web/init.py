from flask import Flask
from web import routes

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'
    app.config['UPLOAD_FOLDER'] = 'uploads'
    
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    routes.init_app(app)
    
    return app