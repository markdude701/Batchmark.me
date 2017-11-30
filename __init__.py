
from flask import Flask, render_template, flash, url_for, redirect, request, session, make_response, send_file, send_from_directory, jsonify
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from datetime import datetime, timedelta
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
import os
from werkzeug.utils import secure_filename
from functools import wraps
from content_management import Content
from db_connect import connection
from library import library

APP_CONTENT = Content()

UPLOAD_FOLDER = '/var/www/FlaskApp/FlaskApp/uploads'
WATERMARK_FOLDER = '/var/www/FlaskApp/FlaskApp/uploads/wm'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__, instance_path='/var/www/FlaskApp/FlaskApp/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['WATERMARK_FOLDER'] = WATERMARK_FOLDER

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Please login.")
            return redirect(url_for('login_page'))

    return wrap

# Upload file checker: "Never Trust User Input"
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    #Returns file extensions - Only if it is in allowed extensions

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

@app.route('/background_process/')
def background_process():
	try:
		lang = request.args.get('proglang', 0, type=str)
		if lang.lower() == 'python':
			return jsonify(result='You are wise')
		else:
			return jsonify(result='Try again.')
	except Exception as e:
    
		return str(e)

@login_required
@app.route('/introduction-to-app/', methods=['GET'])
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

@app.route('/uppercase/', methods=['GET', 'POST'])
def library_test():
    try:
        uppered = ''
        if request.method == "POST":
            lower = request.form['upper']
            uppered = library(lower)
            return render_template("uppercase.html", uppered = uppered)
        return render_template("uppercase.html", uppered = uppered)
    except Exception as e:
        return str(e)
    
    
    

    
@app.route("/watermark/", methods=["GET","POST"])    
def watermark_upload():#Watermark Upload Function
    waterMark = ""
    try:
        if request.method == 'POST':
            # check if the post request has the file part
            if 'wmfile' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['wmfile']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                waterMark = secure_filename(file.filename)
                file.save(os.path.join(app.config['WATERMARK_FOLDER'], waterMark))
                flash('Watermark File upload successful')
                #return redirect(url_for('watermark_upload'))
                return render_template('upload.html', waterMark = waterMark) 
        return render_template('wmupload.html')
    except Exception as e:
        flash("Please upload a valid file")
        flash(e)
        return render_template('wmupload.html')    

    

@app.route("/upload/", methods=["GET","POST"])
def photo_upload():#Photo Upload
    photo[] = ""
    try:
        if request.method == 'POST':
            # check if the post request has the file part
            if 'images[]' not in request.files:
                flash('File Not in Requested Filess: Server Error: Try again')
                #return redirect(request.url)
                return redirect('/upload/')
            file = request.files['images[]']
            # if user does not select file, browser also
            # submit a empty part without filename
            try:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    flash('Photo File upload successful')
                    return render_template('placement.html', filename = filename)
            except:
                if file.filename == '':
                    flash('No selected file')
                    return redirect(request.url)
                else:
                    flash("Except Else Error in Upload")
                    return redirect(request.url)
            
        return render_template('upload.html')
    except:
        flash("Please upload a valid file")
        return render_template('upload.html')


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

@app.route('/uploads/', methods=['GET', 'POST'])
@login_required
def upload_file():
    try:
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('File upload successful')
                return render_template('uploads.html', filename = filename)
        return render_template('uploads.html')
    except:
        flash("Please upload a valid file")
        return render_template('uploads.html')

@app.route('/download/')
@login_required
def download():
	try:
		return send_file('/var/www/FlaskApp/FlaskApp/uploads/screencap.png', attachment_filename='screencap.png')
	except Exception as e:
		return str(e)
    
    
@app.route('/jquery/')
def jquery():
	try:
		return render_template('jquery.html')
	except Exception as e:
		return str(e)

@app.route('/jsonify/', methods=['GET', 'POST'])
def json_stuff():
	try:
		return render_template('jsonify.html')
	except Exception as e:
		return str(e)
    
    
    
@app.route('/downloader/', methods=['GET', 'POST'])
@login_required
def downloader():
    error = ''
    try:
        if request.method == "POST":
            filename = request.form['filename']
            return send_file('/var/www/FlaskApp/FlaskApp/uploads/' + filename, attachment_filename='download')

        else:
            return render_template('downloader.html', error = error)
        error = "Please enter a valid file name"
        return render_template('downloader.html',error = error)

    except:
        error = "Please enter a valid file name"
        return render_template('downloader.html',error = error)

class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice', [validators.Required()])

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