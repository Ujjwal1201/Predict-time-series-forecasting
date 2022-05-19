from requests import Session
from werkzeug.utils import secure_filename
from model_orm import User
import os
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask, render_template, request, flash, redirect, session, url_for

from model_orm import DataSet

app = Flask(__name__)
app.secret_key = 'thisisaverysecretkey'

def opendb():
    engine = create_engine("sqlite:///model.sqlite")
    Session = sessionmaker(bind=engine)
    return Session()

@app.route('/', methods=['GET','POST'])
def login ():
    if request.method == 'POST':
        email = request.form.get('email')
        Password  = request.form.get('Password')
        if not email or len(email) < 11:
            flash("Enter correct email", 'danger')
            return redirect('/')
        elif not Password:
            flash('Password is required', 'danger')
            return redirect('/')
        # more like this
        else:
            db = opendb()
            query = db.query(User).filter(User.email == email).first()
            if query is not None and query.password == Password:        
                session['isauth'] = True
                session['id'] = True
                session['name'] = True
                flash('Login Successfull', 'success')
                return redirect('/uploads')
            else:
                flash('There was an error while Logging in.','danger')
    return render_template('login.html')


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        email = request.form.get('email')
        username = request.form.get('username')
        confirm_password = request.form.get('confirm_password')
        password = request.form.get('password')
        print(confirm_password, password, confirm_password==password)
        if username and password and confirm_password and email:
            if confirm_password != password:
                flash('Password do not match','danger')
                return redirect('/register')
            else:
                db =opendb()
                
                if db.query(User).filter(User.email==email).first() is not None:
                    flash('Please use a different email address','danger')
                    return redirect('/register')
                elif db.query(User).filter(User.username==username).first() is not None:
                    flash('Please use a different username','danger')
                    return redirect('/register')
                else:
                    user = User(username=username, email=email, password=password)  
                    db.add(user)
                    db.commit()
                    db.close()
                    flash('Congratulations, you are now a registered user!','success')
                    return redirect(url_for('login'))
                
        else:
            flash('Fill all the fields','danger')
            return redirect('/register')

    return render_template('register.html', title='Sign Up page')

@app.route('/home')
def home():
    return render_template('home.html')

def allowed_files(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {"csv","xlsx","json"}

@app.route('/uploads', methods=['GET','POST'])
def uploadImage():
    if request.method == 'POST':
        print(request.files)
        if 'file' not in request.files:
            flash('No file uploaded','danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('no file selected','danger')
            return redirect(request.url)
        if file and allowed_files(file.filename):
            print(file.filename)
            db = opendb()
            filename = secure_filename(file.filename)
            file.save(os.path.join("/static/uploads", filename ))
            upload = DataSet(img =f"/static/uploads/{filename}", imgtype = os.path.splitext(file.filename)[1],user_id=User.id)
            db.session.add(upload)
            db.session.commit()
            flash('file uploaded and saved','success')
            session['uploaded_file'] = f"/static/uploads/{filename}"
            return redirect(request.url)
        else:
            flash('wrong file selected, only csv, xlxs and json files allowed','danger')
            return redirect(request.url)
   
    return render_template('upload.html',title='upload new Image')


@app.route('/logout',methods=['GET','POST'])
def logout():
    if "isauth" in session:
        session.pop('isauth')
    return redirect ("/")

if __name__ == '__main__':
  app.run(debug=True)





 

