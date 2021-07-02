from flask import Flask, render_template

application = Flask(__name__)

@application.route('/')
def index():
    return render_template("index.html")

@application.route('/favicon.ico')
def favicon():
    return application.send_static_file('favicon.ico')


if __name__ == "__main__":
    application.debug = True
    application.run()
