import os
import sys
import logging
from flask import Flask, jsonify, render_template
from flask_login import LoginManager
from config import Config, ProductionConfig, DevelopmentConfig
from services import SupabaseService, UserProxy
from routes.auth import auth_bp
from routes.donor import donor_bp
from routes.ngo import ngo_bp
from routes.admin import admin_bp
from routes.chat import chat_bp


# ── Startup Validation ──────────────────────────────────

def validate_config(logger):
    required = ['SUPABASE_URL', 'SUPABASE_KEY', 'SUPABASE_SERVICE_ROLE_KEY', 'SECRET_KEY']
    missing = [v for v in required if not Config.__dict__.get(v) or 'your-project-id' in str(Config.__dict__.get(v, ''))]
    if missing:
        logger.warning('Missing or placeholder env vars: %s. App will start but DB calls will fail.', ', '.join(missing))
    else:
        logger.info('All required config variables present.')


# ── App Factory ─────────────────────────────────────────

def create_app():
    app = Flask(__name__)

    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    logging.basicConfig(level=logging.INFO)
    validate_config(app.logger)

    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except OSError:
        temp_upload = os.path.join('/tmp', 'uploads')
        os.makedirs(temp_upload, exist_ok=True)
        app.config['UPLOAD_FOLDER'] = temp_upload
        app.logger.warning('Using /tmp/uploads for file uploads (read-only fs detected)')

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    if env == 'production':
        gunicorn_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
    else:
        app.logger.info('Nourish Collective starting in %s mode', env)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            user_data = SupabaseService.get_user_by_id(int(user_id))
            return UserProxy(user_data) if user_data else None
        except Exception as e:
            app.logger.error('user_loader failed for id %s: %s', user_id, e)
            return None

    app.register_blueprint(auth_bp)
    app.register_blueprint(donor_bp)
    app.register_blueprint(ngo_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chat_bp)

    app.context_processor(lambda: {
        'now': __import__('datetime').datetime.utcnow(),
        'app_name': 'Nourish Collective',
    })

    # ── Health Check ──
    @app.route('/health')
    def health():
        supabase_url = app.config.get('SUPABASE_URL', '')
        return jsonify({
            'status': 'ok',
            'app': 'Nourish Collective',
            'env': env,
            'supabase_url_configured': bool(supabase_url and 'your-project-id' not in supabase_url),
            'supabase_url_prefix': supabase_url[:20] if supabase_url else 'MISSING',
        })

    # ── Error Handlers ──
    @app.errorhandler(404)
    def not_found(e):
        return render_template('index.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error('500: %s', e)
        return '<h1>500 — Internal Server Error</h1><p>Please try again later.</p>', 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        app.logger.error('Unhandled exception: %s', e, exc_info=True)
        return '<h1>500 — Unexpected Error</h1><p>Check server logs for details.</p>', 500

    return app


# ── Entry Point ─────────────────────────────────────────

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=(os.getenv('FLASK_ENV') != 'production'))
