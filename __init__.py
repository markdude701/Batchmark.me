from flask import Flask, render_template, flash, url_for, redirect, request, session, make_response
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
from functools import wraps
from content_management import Content
from db_connect import connection
from datetime import datetime, timedelta

APP_CONTENT = Content()

app = Flask(__name__)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Please login.")
            return redirect(url_for('login_page'))

    return wrap

@app.route("/", methods = ["GET", "POST"])
def main():
    error = ''
    try:
        c, conn = connection()
        if request.method == "POST":

            data = c.execute("SELECT * FROM users WHERE username = ('{0}')".format(thwart(request.form['username'])))

            data = c.fetchone()[2]

            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['username'] = request.form['username']

                flash("You are now logged in")
                return redirect(url_for("dashboard"))

            else:
                error = "Invalid credentials, try again."

        gc.collect()
        return render_template("main.html", error = error)

    except Exception as e:
        flash(e)
        error = "Invalid credentials, try again."
        return render_template("main.html", error = error)

@app.route("/dashboard/", methods = ["GET", "POST"])
@login_required
def dashboard():
    return render_template("dashboard.html", APP_CONTENT = APP_CONTENT)

@login_required
@app.route('/introduction-to-site/', methods=['GET'])
def introapp():
    try:
        #PUT FANCY PYTHON HERE YO
        output = ['digit is good', 'python is cool.','<p><strong>Hello World</strong></p>', '43', 2]
        
        
        return render_template("templating_demo.html", output = output)
    except Exception as e:
        return(str(e))


@app.route("/about/")
def about_page():
    return render_template("about.html", APP_CONTENT = APP_CONTENT)

@app.route('/login/', methods=["GET","POST"])
def login_page():
    error = ''
    try:
        c, conn = connection()
        if request.method == "POST":
            data = c.execute("SELECT * FROM users WHERE username = ('{0}')".format(thwart(request.form['username'])))

            data = c.fetchone()[2]

            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['username'] = request.form['username']

                flash("You are now logged in")
                return redirect(url_for("dashboard"))

            else:
                error = "Invalid credentials, try again."

        gc.collect()

        return render_template("login.html", error = error)

    except Exception as e:
        #flash(e)
        error = "Invalid credentials, try again."
        return render_template("login.html", error = error)


class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice', [validators.Required()])

@app.route('/register/', methods=["GET","POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username  = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            c, conn = connection()

            x = c.execute("SELECT * FROM users WHERE username = ('{0}')".format(thwart(username)))

            if int(x) > 0:
                flash("That username is already taken, please choose another.")
                return render_template('register.html', form = form)

            else:
                c.execute("INSERT INTO users (username, password, email, tracking) VALUES ('{0}','{1}','{2}','{3}')".format(thwart(username), thwart(password), thwart(email), thwart("/dashboard/")))

                conn.commit()
                flash("Thanks for registering!")
                c.close()
                conn.close()
                gc.collect()

                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for('dashboard'))

        return render_template("register.html", form = form)

    except Exception as e:
        return(str(e))

@app.route("/logout/")
@login_required
def logout():
    session.clear()
    gc.collect()
    return redirect(url_for('main'))


@app.route('/sitemap.xml/', methods=['GET'])
def sitemap():
    try:
        pages = []
        week = (datetime.now() - timedelta(days = 7)).date().isoformat()
        for rule in app.url_map.iter_rules():
            if "GET" in rule.methods and len(rule.arguments)==0:
                pages.append(
                    ["http://138.197.167.225/"+str(rule.rule),week]
                )
        sitemap_xml = render_template('sitemap_template.xml', pages = pages)
        response = make_response(sitemap_xml)
        response.headers["Content-Type"] = "application/xml"
        return response
    except Exception as e:
        return(str(e))

@app.route("/robots.txt/")
def robots():
    #return("User-agent: *\nDisallow /") #Disallows all robot traffic
    return("User-agent: *\nDisallow: /register/\nDisallow: /login/") #Disallows robot traffic to sensitive urls


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(405)
def page_not_found(e):
    return render_template("405.html")

@app.errorhandler(500)
def int_server_error(e):
    return render_template("500.html", error = e)

if __name__ == "__main__":
	app.run()