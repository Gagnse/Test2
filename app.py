from flask import Flask, render_template

app = Flask(__name__,
            static_folder='frontend/static',
            template_folder='frontend/templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')  # à créer

@app.route('/services')
def services():
    return render_template('services.html')  # à créer

@app.route('/contact')
def contact():
    return render_template('contact.html')  # à créer

if __name__ == '__main__':
    app.run(debug=True)