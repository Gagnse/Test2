from flask import Flask, render_template, request

app = Flask(__name__,
            static_folder='frontend/static',
            template_folder='frontend/templates')

@app.route('/')
def home():
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

if __name__ == '__main__':
    app.run(debug=True)