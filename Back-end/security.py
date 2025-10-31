from flask import Flask, render_template, send_from_directory, request, abort
from flask_talisman import Talisman
from functools import wraps
import os
import time
import ssl
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Konfigurasi keamanan yang lebih ketat
csp = {
    'default-src': "'self'",
    'script-src': "'self' 'unsafe-inline'",
    'style-src': "'self' 'unsafe-inline'",
    'img-src': "'self' data: https://github.com https://linkedin.com",
    'font-src': "'self'",
    'frame-ancestors': "'none'",
    'form-action': "'self'",
    'base-uri': "'self'",
    'connect-src': "'self' https://github.com https://linkedin.com",
    'navigate-to': "'self' https://github.com https://linkedin.com https://www.linkedin.com",
}

# Inisialisasi Talisman dengan konfigurasi keamanan yang ditingkatkan
Talisman(app,
         content_security_policy=csp,
         force_https=True,
         strict_transport_security=True,
         session_cookie_secure=True,
         session_cookie_http_only=True,
         feature_policy={
             'geolocation': "'none'",
             'midi': "'none'",
             'notifications': "'none'",
             'push': "'none'",
             'sync-xhr': "'none'",
             'microphone': "'none'",
             'camera': "'none'",
             'magnetometer': "'none'",
             'gyroscope': "'none'",
             'speaker': "'none'",
             'vibrate': "'none'",
             'fullscreen': "'none'",
             'payment': "'none'",
         })

# Rate limiting
request_history = {}
RATE_LIMIT = 30  # requests
RATE_LIMIT_WINDOW = 60  # seconds

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr
        current_time = time.time()
        
        # Cleanup old entries
        request_history[ip] = [t for t in request_history.get(ip, []) 
                             if current_time - t < RATE_LIMIT_WINDOW]
        
        # Check rate limit
        if len(request_history.get(ip, [])) >= RATE_LIMIT:
            abort(429, description="Too many requests")
        
        # Add current request
        if ip in request_history:
            request_history[ip].append(current_time)
        else:
            request_history[ip] = [current_time]
            
        return f(*args, **kwargs)
    return decorated_function

# Konfigurasi path untuk static files dengan validasi path
app.static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

@app.route('/')
@rate_limit
def index():
    try:
        # Validasi path
        if not os.path.exists(os.path.join(app.static_folder, 'index.html')):
            abort(404)
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        app.logger.error(f"Error serving index: {str(e)}")
        abort(500)

@app.route('/<path:path>')
@rate_limit
def serve_file(path):
    try:
        # Validasi path untuk mencegah path traversal
        requested_path = os.path.abspath(os.path.join(app.static_folder, path))
        if not requested_path.startswith(app.static_folder):
            abort(403)
        
        # Validasi ekstensi file
        allowed_extensions = {'.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.svg', '.woff', '.woff2', '.ttf', '.eot'}
        if not any(requested_path.endswith(ext) for ext in allowed_extensions):
            abort(403)
            
        if not os.path.exists(requested_path):
            abort(404)
            
        return send_from_directory(app.static_folder, path)
    except Exception as e:
        app.logger.error(f"Error serving file {path}: {str(e)}")
        abort(500)

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return "File not found", 404

@app.errorhandler(403)
def forbidden(e):
    return "Access forbidden", 403

@app.errorhandler(429)
def too_many_requests(e):
    return "Too many requests. Please try again later.", 429

@app.errorhandler(500)
def internal_error(e):
    return "Internal server error", 500

# Disable browser caching dan tambahan security headers
@app.after_request
def add_security_headers(response):
    # Prevent caching
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    # Additional security headers
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Permissions-Policy'] = 'geolocation=(), midi=(), notifications=(), push=(), sync-xhr=(), microphone=(), camera=(), magnetometer=(), gyroscope=(), speaker=(), vibrate=(), fullscreen=(), payment=()'
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Resource-Policy'] = 'same-origin'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Remove potentially dangerous headers
    response.headers.pop('Server', None)
    response.headers.pop('X-Powered-By', None)
    
    return response

# Konfigurasi logging
import logging
from logging.handlers import RotatingFileHandler

if not os.path.exists('logs'):
    os.mkdir('logs')

file_handler = RotatingFileHandler('logs/security.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Security system startup')

if __name__ == '__main__':
    # Konfigurasi SSL
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    try:
        ssl_context.load_cert_chain(
            certfile='certificate.pem',  # Ganti dengan path ke sertifikat SSL Anda
            keyfile='private_key.pem'    # Ganti dengan path ke private key Anda
        )
    except Exception as e:
        app.logger.warning("SSL certificate not found, using adhoc certificates")
        ssl_context = 'adhoc'

    app.run(
        host='0.0.0.0',
        port=5000,
        ssl_context=ssl_context,
        threaded=True
    )
