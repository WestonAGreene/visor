# everything here is almost verbatim examples from the web for "hello world flask" apps

from flask_nav.elements import Navbar, View, Subgroup
from flask_nav import Nav
from flask import Flask, render_template, flash
# from wtforms import Form, TextField
from flask_bootstrap import Bootstrap
import os

app = Flask(__name__)
Bootstrap(app)

nav = Nav()

@nav.navigation()
def mynavbar():
    return Navbar(
        'ViSOR',
        View(
            'Dashboard', 
            'home'
        ),
        Subgroup(
            'Schematic',
            View(
                'High Level', 
                'schematic',
                detail_level="high-level"
            ),
            View(
                'Low Level', 
                'schematic', 
                detail_level="low-level"
            ),
        ),
    )
nav.init_app(app)

@app.route('/health')  # necessary for the ReadinessProbe
def health():
    return "available", 000

@app.route('/')
def home():
    return render_template('home.html', branch=os.environ["OPENSHIFT_BUILD_REFERENCE"])  # BRANCH is set by jenkins when deciding which repo to clone. I can now use that same env variable to decide which grafana to reference

@app.route('/schematic')
@app.route('/schematic/')
@app.route('/schematic/<detail_level>')  # I pass as a parameter to allow for mistypes
def schematic(detail_level=None):
    return render_template('schematic.html', detail_level=detail_level)

if __name__ == "__main__":

    nav.init_app(app)

    # learned this syntax from https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https
    # app.run(ssl_context=('/opt/app-root/cert/tls.crt',  
    #                      '/opt/app-root/cert/tls.key'
    #                      ))
    app.run()
