################## START IMPORTS ###########################################





from flask import Flask, render_template, flash, url_for, redirect, request, session, make_response, send_file, send_from_directory, jsonify
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from datetime import datetime, timedelta
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
import os, os.path
from werkzeug.utils import secure_filename
from functools import wraps
from content_management import Content
from db_connect import connection
from library import library
from images import savePrompt, firstResize, processTopLeft, processTopRight, processBottomLeft, processBottomRight
from pathlib import Path
import glob
import PIL
from PIL import Image





###################### END IMPORTS #######################################








###################### START GLOBAL VARS #################################


waterMark = ''
uploaded_photo = ''
optradio = ''
photo_local = ''
uploaded_photo =''
waterMark = ''
photoName = ''

####################### END GLOBAL VARS ################################









##################### START FANCY PYTHON ###############################

APP_CONTENT = Content()

app = Flask(__name__, instance_path='/var/www/FlaskApp/FlaskApp/uploads')

ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])#IMAGES

UPLOAD_FOLDER = '/var/www/FlaskApp/FlaskApp/uploads'
WATERMARK_FOLDER = '/var/www/FlaskApp/FlaskApp/uploads/wm'
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



  ##################### END FANCY PYTHON ########################  











####################### START WATERMARK ###########################
    
    
@app.route("/watermark/", methods=["GET","POST"])
def watermark_upload():#Watermark Upload Function
    global waterMark
    global uploaded_photo
    #waterMark_URL = ""
    try:
        if request.method == 'POST':
            # check if the post request has the file part
            if 'wmfile' not in request.files:
                flash('Not Seeing WMFILE variable')
                return redirect(request.url)
            file = request.files['wmfile']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                waterMark = secure_filename(file.filename) #Creates the path of the Watermark and sets it to WM
                file.save(os.path.join(app.config['WATERMARK_FOLDER'], waterMark)) #Save File
                #waterMark_URL = file.url()
                #flash("Created at " + waterMark_URL)

                flash('Watermark File upload successful')
                #return render_template("upload.html",waterMark = waterMark)
                return redirect(url_for('photo_upload',waterMark=waterMark)) #NEED THIS INSTEAD OF RENDER_TEMPLATE TO HAVE DIFFERENT, Interesting how this works, when we use Render_template in the other functions
                                                        #FUNCS/DEFS IN AN APPROUTE
        return render_template('wmupload.html')
    except Exception as e:
        flash("Please upload a Watermark file")
        flash(e)
        return render_template('wmupload.html')

@app.route("/photo_upload/", methods=["GET","POST"])
def photo_upload():
    uploaded_photo = ""
    images = ""
    global uploaded_photo
    global waterMark
    

    try:
        if request.method == 'POST':
            # check if the post request has the file part
            if 'images' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['images']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                uploaded_photo = secure_filename(file.filename) #Creates the path of the Watermark and sets it to WM
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], uploaded_photo)) #Save File
                flash('Photo File upload successful')
                #return redirect(url_for("placement")+"?uploaded_photo=" +uploaded_photo + "?waterMark="+waterMark) 
                return render_template("placement.html",uploaded_photo = uploaded_photo,waterMark = waterMark) #NEED THIS INSTEAD OF RENDER_TEMPLATE TO HAVE DIFFERENT
                                                        #FUNCS/DEFS IN AN APPROUTE
                #return render_template('upload.html', waterMark = waterMark)
        global uploaded_photo
        global waterMark
        return render_template('upload.html')
    except Exception as e:
        flash("Please upload a Watermark file")
        flash(e)
        return render_template('upload.html')


@app.route('/placement/', methods=['GET', 'POST'])
def placement():
    global uploaded_photo
    global waterMark
    global optradio
    try:
        if request.method == 'POST': #If the form method is post
            optradio = request.form['optradio'] #Radio Button Input
            #flash("POST - PRESSED THE SUBMIT BUTTON IN PROCESS")
            global optradio
            return render_template('photo_process.html',waterMark = waterMark, uploaded_photo = uploaded_photo, optradio = optradio) #Redirect to page with image functions
            
            #return redirect('photo_process.html',waterMark = waterMark, uploaded_photo = uploaded_photo, optradio = optradio)
        return render_template('placement.html')
    except Exception as e:
        return(str(e))
        flash("Please select an option!")
        return render_template('placement.html')


@app.route('/photo_process/', methods=['GET', 'POST'])
def photo_process():
    try:
        global uploaded_photo
        global waterMark
        global optradio
        global wm_local
        global photo_local
        flash("PHOTO PROCESSING :D")
             #Resizes, saves the image to work with Coord System
            #flash()
        wm = Image.open("/var/www/FlaskApp/FlaskApp/uploads/wm/" + waterMark)
        im = Image.open("/var/www/FlaskApp/FlaskApp/uploads/" + uploaded_photo)#Opens file in photo directory
        #waterMark = Image.open(wmDir) #Use Jinja to find the directory and variable
        wm_local = "/var/www/FlaskApp/FlaskApp/uploads/wm/" + waterMark
        photo_local = "/var/www/FlaskApp/FlaskApp/uploads/" + uploaded_photo
        
        firstResize(im, photo_local)
        #optradio = 1
        
        processTopLeft(wm, im, optradio, photo_local, wm_local)
        #if optradio == "1":
            #processTopLeft(wm, im, optradio, photo_local, wm_local)
        #elif optradio == "2":
            #processTopRight(wm, im, optradio, photo_local, wm_local)
        #elif optradio == "3":
            #processBottomLeft(wm, im, optradio, photo_local, wm_local)
        #elif optradio == "4":
            #processTopRight(wm, im, optradio, photo_local, wm_local)
        #else:
            #flash("Error in Radio Button Input")
            #return render_template('photo_process.html')
        
        
        
        
        
        
        return render_template('photo_process.html')
    except Exception as e:
        return(str(e))
        flash("That's not supposed to happen. Try Again!")
        return render_template('photo_process.html')
    
    
@app.route('/wmdownloader/', methods=['GET', 'POST'])
def wmdownloader():
    error = ''
    e = ''
    try:
        global uploaded_photo
        global waterMark
        global optradio
        global wm_local
        global photo_local
        global photoName
        photoName = photo_local + "Watermark.JPG"
        flash(photoName)
        try:
            #return render_template('final.html', photoName = photoName)
            return redirect(url_for('finale',photoName = photoName))
            #return send_file(photo_local + 'Watermark.JPG')

        except exception as e:
            flash(e)
            error = e
            return render_template('downloader.html',error = error + ' , Exception as e' )

    except:
        error = "Exception: Please enter a valid file name"
        return render_template('downloader.html',error = error + ' , ' + e)
    #return render_template('final.html')
    
@app.route('/final/', methods=["GET","POST"])
def finale():
    global photoName
    return render_template("final.html", photoName = photoName)
 
    
    
################### END WATERMARK STUFF #############################










################### START LESSONS #################################
    
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
        
        output = ['digit is good', 'python is cool.','<p><strong>Hello World</strong></p>', '43', 2]


        return render_template("templating_demo.html", output = output)
    except Exception as e:
        return(str(e))



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

@app.route("/logout/")
@login_required
def logout():
    session.clear()
    gc.collect()
    return redirect(url_for('main'))
    
    
    
    
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
		return send_file('/var/www/FlaskApp/FlaskApp/uploads/screencap.png', attachment_filename='screencap.png') #Client will save this and then create a file with the filename of screencap.png
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

    
    
    
    ################### END LESSONS ########################
    
    
    
    
    
    
    
    
    
    
    
    
    #################### REGISTER PAGES ######################
    
    
    
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
    
    
    
 ######################## END REGISTER PAGES ############################












    #################### START GOOGLE STUFF ####################



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

######################## END GOOGLE STUFF ###########################











######################### START PERSONAL PAGES ##########################


    
@app.route('/resume/', methods=['GET'])
def resume():
    try:
        return render_template("resume.html")
    except Exception as e:
        return(str(e))    

@app.route('/personal_projects/', methods=['GET'])
def personal_projects():
    try:
        return render_template("personal_projects.html")
    except Exception as e:
        return(str(e))      


@app.route('/contact/', methods=['GET'])
def contact():
    try:
        return render_template("contact.html")
    except Exception as e:
        return(str(e))
    
@app.route('/personal/', methods=['GET'])
def personal():
    try:
        return render_template("personal_main.html")
    except Exception as e:
        return(str(e))
@app.route("/writing/")
def writing():
    try:
        return render_template("personal_writing.html")
    except Exception as e:
        return(str(e))
@app.route("/drawing/")
def drawing():
    try:
        return render_template("personal_drawing.html")
    except Exception as e:
        return(str(e))
@app.route("/bus/")
def bus():
    try:
        return render_template("personal_bus.html")
    except Exception as e:
        return(str(e))
@app.route("/production/")
def production():
    try:
        return render_template("personal_production.html")
    except Exception as e:
        return(str(e))
    
@app.route("/photography/")
def photography():
    try:
        return render_template("personal_photo.html")
    except Exception as e:
        return(str(e))
    
@app.route("/web_design/")
def web_design():
    try:
        return render_template("personal_web_design.html")
    except Exception as e:
        return(str(e))

@app.route("/about/")
def about_page():
    return render_template("about.html", APP_CONTENT = APP_CONTENT)

@app.route("/journey/")
def journey():
    return render_template("personal_journey.html", APP_CONTENT = APP_CONTENT)

@app.route("/grot/")
def grot():
    return render_template("personal_grot.html", APP_CONTENT = APP_CONTENT)

@app.route("/obj/")
def obj():
    return render_template("personal_obj.html", APP_CONTENT = APP_CONTENT)


@app.route("/story/")
def story():
    return render_template("personal_story.html", APP_CONTENT = APP_CONTENT)

@app.route("/sol/")
def sol():
    return render_template("personal_sol.html", APP_CONTENT = APP_CONTENT)

@app.route("/personal_about/")
def about():
    return render_template("personal_about.html", APP_CONTENT = APP_CONTENT)

@app.route("/personal_computer/")
def computer():
    return render_template("personal_computer.html", APP_CONTENT = APP_CONTENT)

@app.route("/geekSquad/")
def geekSquad():
    return render_template("personal_geekSquad.html", APP_CONTENT = APP_CONTENT)

@app.route("/triangle/")
def triangle():
    return render_template("personal_triangle.html", APP_CONTENT = APP_CONTENT)
    
    
    
 ######################## - END PERSONAL SECTION - ########################3   

########################## - ERROR HANDLERS - ##############################

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(405)
def page_not_found(e):
    return render_template("405.html")

@app.errorhandler(500)
def int_server_error(e):
    return render_template("500.html", error = e)

######################### - END ERROR HANDLERS - ########################








########################### RUN APP ####################################

if __name__ == "__main__":
	app.run()

