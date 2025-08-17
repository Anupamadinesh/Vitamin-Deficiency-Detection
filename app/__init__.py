from flask import Flask
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Initialize extensions
mysql = MySQL()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Secret Key
    app.config['SECRET_KEY'] = 'abc123'

    # MySQL Config
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = '1231'
    app.config['MYSQL_DB'] = 'userdb'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

    # Initialize extensions with app
    mysql.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Redirect users to login if not logged in
    login_manager.login_view = 'login'

    # ✅ Register Blueprints
    from app.routes import main
    from app.predict import predict_bp  # ✅ Import predict blueprint
    from app.tools import tools_bp  # ✅ Import tools blueprint
    app.register_blueprint(main)
    app.register_blueprint(predict_bp, url_prefix='/predict')  # ✅ Register predict_bp with prefix
    app.register_blueprint(tools_bp, url_prefix='/tools')  # ✅ Register tools_bp
    return app
