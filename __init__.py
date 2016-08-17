from flask import Flask, render_template, redirect, \
    url_for, request, session, flash, g, make_response, send_file
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from functools import wraps
import MySQLdb
from MySQLdb import escape_string as thwart
import json
import datetime
from datetime import datetime,timedelta
from time import mktime
import os
import time
import urllib2
from wtforms import Form, BooleanField, TextField, PasswordField, IntegerField, validators
from passlib.hash import sha256_crypt
from dbconnect import connection
import gc
from flask.ext.uploads import UploadSet, configure_uploads, IMAGES, UploadNotAllowed
import smtplib
from flask_mail import Mail, Message


FAC_USERNAME = 'faculty'
FAC_PASSWORD = 'secret'
FAC_PASSWORD_ENC = sha256_crypt.encrypt(FAC_PASSWORD)
photos = UploadSet('photos', IMAGES)







app = Flask(__name__)

app.secret_key = os.urandom(24)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.session_protection = "strong"
login_manager.setup_app(app)


app.config['UPLOADED_PHOTOS_DEST'] = 'static/images'
configure_uploads(app, photos)


class RegiationForm(Form):
    username = TextField('Regiation ID', [validators.Length(min=4, max=20)])
    fname = TextField('First Name', [validators.Length(min=2, max=50)])
    lname = TextField('Last Name', [validators.Length(min=2, max=50)])
    sem = TextField('Semester')
    department = TextField('Department', [validators.Length(min=2, max=50)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the <a href="/about/tos" target="blank">Terms of Service</a> \
        and <a href="/about/privacy-policy" target="blank">Privacy Notice</a> ', [validators.Required()])


class Faculty_login(Form):
    username = TextField('User ID', [validators.Required()])
    password = PasswordField('Password',[validators.Required()])


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


def login_required_faculty(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' and 'faculty' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


@app.route('/logout/')
@login_required
def logout():
	session.pop('logged_in', None)
	session.clear()
	flash('You have been logged out.')
	gc.collect()
	return redirect(url_for('main'))

@app.route('/logout/')
@login_required
@login_required_faculty
def logoutfaculty():
    session.pop('logged_in', None)
    session.pop('faculty', None)
    session.clear()
    flash('You have been logged out.')
    gc.collect()
    return redirect(url_for('freglog'))




@app.route('/faculty/', methods=['GET', 'POST'])


def faculty_login():
    
    
    if request.method == 'POST' :
        #render_template('facultylogin.html', form = form)

    
        try:
            if request.form['username'] == FAC_USERNAME and request.form['password'] == FAC_PASSWORD:
                session['logged_in']  = True

                

                session['faculty'] = True

                return redirect(url_for('freglog'))
            else:
                flash("Try again")
                return redirect(url_for('faculty_login'))
        except Exception, e:
            flash(str(e))
    else:
        return render_template('facultylogin.html')



@app.route('/freglog/register', methods = ['GET', 'POST'])
@login_required
@login_required_faculty
def freglog():
    
    
    if request.method == 'POST' :
        
        username = request.form['username_r']
        fname = request.form['fname']
        lname = request.form['lname']
        
        department = request.form['department']
        password = sha256_crypt.encrypt(((request.form['password_r'])))
        c, conn = connection()
        x = c.execute("SELECT * FROM faculti WHERE username = (%s)", (username,))
        if int(x) > 0:
            flash("That username is already taken")
            return render_template('facultyloginprofile.html' )
        else:
            c.execute("INSERT INTO faculti (username, fname, lname, department, passwd) VALUES(%s, %s, %s, %s, %s)",
                (username, fname, lname, department, password,))
            conn.commit()
            flash("Thanks for registering")
            c.close()
            conn.close()
            gc.collect()
            session['logged_in'] = True
            session['username'] = username
            session['faculty'] = True 
            return redirect(url_for('dashboardfaculty', username = (username)))
        
    else:
        return render_template('facultyloginprofile.html')

        
@app.route('/freglog/login', methods = ['GET', 'POST'])
@login_required
@login_required_faculty
def facultylogin():
    if request.method == 'POST':


        username = request.form['username_l']
        c,conn = connection()
        if request.method == 'POST':
            data = c.execute("SELECT * FROM faculti WHERE username = (%s)",(username,))
            password = c.fetchone()[1]
            #password = x[1]
            if  sha256_crypt.verify(request.form['password_l'], password) :
                session['username'] = username
                session['logged_in'] = True
                session['faculty'] =  True
                c.close()
                conn.close()
                gc.collect()
                return redirect(url_for('dashboardfaculty', username = username))
            else:
                flash('Invaid Credentials')
                return redirect(url_for('freglog'))
        else:
            return render_template('facultyloginprofile.html')
    else:
        flash('Login  Here')
        return render_template('facultyloginprofile.html')





@app.route('/fhome/<username>/', methods = ['GET', 'POST'])
@login_required
@login_required_faculty
def dashboardfaculty(username):
    c,conn = connection()
    
    data = c.execute("SELECT * FROM faculti WHERE username = (%s)",(username,))
    x = c.fetchone()
    fname = x[2]
    lname = x[3]
    
    department = x[6]
    
    c.close()
    conn.close()
    gc.collect()


    return  render_template('facultyloggedin.html', username = username, fname = fname, lname = lname, department = department )

@app.route('/', methods=['GET', 'POST'])
def main():
    form = RegiationForm(request.form)

    try:
        c,conn = connection()
        error = None
        if request.method == 'POST':
            try:
                data = c.execute("SELECT * FROM Stud WHERE username = (%s)",
                        thwart(request.form['username']))
                data = c.fetchone()[3]

                if sha256_crypt.verify(request.form['password'], data):
                    session['logged_in'] = True
                    session['username'] = request.form['username']
                    flash('You are now logged in.')
                    return redirect(url_for('dashboard', username = (c.fetchone()[0])))
            except Exception, e:
                flash("What are you doing?")


            try:
                
                if request.method == 'POST' and form.validate():
                	username = form.username.data
                	fname = form.fname.data
                	lname = form.lname.data
                	sem = form.sem.data
                	department = form.department.data
                	password = sha256_crypt.encrypt(((form.password.data)))
                	c, conn = connection()
                	x = c.execute("SELECT * FROM Stud WHERE username = (%s)", (username,))
                	if int(x) > 0:
                		flash("That username is already taken")
                		return render_template('homepage.html', form = form)
                	else:
                		c.execute("INSERT INTO Stud (username, fname, lname, sem, department, passwd) VALUES(%s, %s, %s, %s, %s, %s)",
                			(username, fname, lname, sem, department, password,))
                		conn.commit()
                		flash("Thanks for registering")
                		c.close()
                		conn.close()
                		gc.collect()
                		session['logged_in'] = True
                		session['username'] = username
                		return redirect(url_for('dashboard', username = (username)))
                else:
                    flash('Fields required')
                    return render_template('homepage.html', form = form)


					

            except Exception as e:
                return((e))
  
            else:
                flash('Invalid credentials. Try again')
        c.close()
        conn.close()
        gc.collect()
        return render_template("homepage.html", error=error, form=form, page_type = "main")
    except Exception, e:
        return((e))



@app.route('/register/', methods=['GET', 'POST'])
def register():

    try:
        form = RegiationForm(request.form)
        if request.method == 'POST' and form.validate():
            flash("register attempted")

            username = form.username.data
            fname = form.fname.data
            lname = form.lname.data
            sem = form.sem.data
            department = form.department.data


            password = sha256_crypt.encrypt(((form.password.data)))
            c,conn = connection()

            x = c.execute("SELECT * FROM Stud WHERE username = (%s)",
                (username,))

            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template('homepage.html', form=form)

            else:
                c.execute("INSERT INTO Stud (username, fname, lname, sem, department, passwd) VALUES (%s, %s, %s, %s, %s, %s)",
                    (username, fname, lname, sem, department, password,))
                conn.commit()
                #flash('Thanks for registering')
                c.close()
                conn.close()
                gc.collect()
                session['logged_in'] = True
                session['username'] = username

                #flash("hi there.")
                return redirect(url_for('dashboard', username = (username)))
        #gc.collect()
        flash("Fields required")
        return render_template('homepage.html', form = form)
    			#return render_template('register.html', form=form)
    except Exception as e:
        return((e))




@app.route('/dashboard/<username>/', methods=['GET', 'POST'])
#@login_required
def dashboard(username):
    photo = username
    allowed_ext = ['jpeg', 'jpg', ]
    photo = photos.url('loggedin.jpeg')
    
    
    c,conn = connection()
	
    data = c.execute("SELECT * FROM Stud WHERE username = (%s)",(username,))
    x = c.fetchone()
    fname = x[0]
    lname = x[1]
    department = x[6]
    sem = x[5]
    c.close()
    conn.close()
    gc.collect()


    return render_template('studentspage.html', username = username, fname = fname, lname = lname, department = department, sem =  sem, photo = photo)




@app.route('/login/', methods=['GET','POST'])
def login():
    error = ''
    c, conn = connection()
    if request.method == 'POST':
        data = c.execute("SELECT * FROM Stud WHERE username = (%s)",(request.form['username'],))
        datap = c.fetchone()[3]

        if sha256_crypt.verify(request.form['password'], str(datap)):
            session['logged_in'] = True
            session['username'] = request.form['username']
            c.close()
            conn.close()
            gc.collect()
            return redirect(url_for('dashboard', username = (request.form['username'])))
        else:
            flash("Wrong Credentials")
            gc.collect()
            return redirect(url_for('main'))
    else:
        
        c.close()
        conn.close()
        gc.collect	
        return redirect(url_for('main'))
    
@app.route('/edit/<username>/', methods=['GET', 'POST'])
@login_required
def editstudentprofile(username):
    if username == session['username']:
        return render_template('editstudentprofile.html', username = username)
    else:
        return "Go edit your own"


@app.route('/edit/<username>/', methods=['GET', 'POST'])
@login_required
@login_required_faculty
def edit(username):
    if username == session['username']:
        return render_template('editstudentprofile.html', username = username)
    else:
        return "Go edit your own"

@app.route('/edit/<username>/', methods=['GET', 'POST'])
@login_required
def editstudentsProfile(username):
	return "hello"

    


if __name__ == "__main__":
    app.run(
    		debug = True)