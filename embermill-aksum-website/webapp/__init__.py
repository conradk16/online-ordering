from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c0a5be15fe3cb64fbfba58ec0a74897c83511fc15f6c267b'


# welcome page
@app.route('/')
def homepage():
    return render_template('home.html')

# hours and location page
@app.route('/hours-and-location')
def hours_and_location():
    return render_template('hours-and-location.html')

# menu page
@app.route('/menu')
def menu():
    return render_template('menu.html')
