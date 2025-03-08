from flask import Flask, render_template, request, session, redirect, url_for
import os
from datetime import timedelta

app = Flask(__name__,
            static_folder='frontend/static',
            template_folder='frontend/templates')

# Configure app
app.secret_key = os.environ.get('SECRET_KEY', 'spacelogic-dev-key')  # Change this in production!
app.permanent_session_lifetime = timedelta(days=1)

# Import blueprints
from server.routes.auth import auth_bp
from server.routes.workspace import workspace_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='')
app.register_blueprint(workspace_bp, url_prefix='/workspace')

@app.route('/')
def home():
    # If user is authenticated, redirect to workspace projects
    if 'user_id' in session:
        return redirect(url_for('workspace.projects'))
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy_policy.html')

@app.route('/terms')
def terms():
    return render_template('terms_of_service.html')

# Pass authentication state to all templates
@app.context_processor
def inject_auth_status():
    from server.services.auth import AuthService
    return {
        'is_authenticated': AuthService.is_authenticated(),
        'current_user_name': AuthService.get_current_user_name()
    }

if __name__ == '__main__':
    app.run(debug=True)