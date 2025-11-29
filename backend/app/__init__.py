from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from .config import Config
from flask_mail import Mail
db = SQLAlchemy()
jwt = JWTManager()
cache = Cache()
mail = Mail()
def create_app():
    app = Flask(__name__)
    from flask_cors import CORS
    CORS(app)
    app.config.from_object(Config)
    
    # Ensure export path exists
    import os
    if not os.path.exists(app.config['EXPORT_PATH']):
        os.makedirs(app.config['EXPORT_PATH'])

    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    mail.init_app(app)
    # register blueprints
    from .routes.auth import bp as auth_bp
    from .routes.admin import bp as admin_bp
    from .routes.doctor import bp as doctor_bp
    from .routes.patient import bp as patient_bp
    from .routes.appointments import bp as appt_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
    app.register_blueprint(patient_bp, url_prefix='/api/patient')
    app.register_blueprint(appt_bp, url_prefix='/api/appointments')
    @app.route('/api/health')
    def health():
        return {'status':'ok'}
    return app
