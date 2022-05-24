from werkzeug.utils import secure_filename
from model_orm import User
import os
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask,render_template, request, flash, redirect, session, url_for
import pandas as pd

from model_orm import DataSet

app = Flask(__name__)
app.secret_key = 'thisisaverysecretkey'

def opendb():
    engine = create_engine("sqlite:///model.sqlite")
    Session = sessionmaker(bind=engine)
    return Session()

@app.route('/', methods=['GET','POST'])
def login ():
    # if session['isauth']:
    #     return redirect('/home')
    if request.method == 'POST':
        email = request.form.get('email')
        Password  = request.form.get('psw')
        print(email,Password)
        if not email or len(email) < 11:
            flash("Enter correct email", 'danger')
            return redirect('/')
        elif not Password:
            flash('Password is required', 'danger')
            return redirect('/')
        elif 'isauth' in session and session['isauth']:
            return redirect('/home')
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

# @app.route('/forgot ' ,methods=["GET","POST"])
# def forgot():
#     return render_template('forgot.html')

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
                elif db.query(User).filter(User.password==password).first() is not None:
                    flash('Please use a different password','danger')
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
            path = os.path.join(os.getcwd(),"static/uploads", filename)
            print(path)
            file.save(path)
            upload = DataSet(filename=filename,filepath =f"/static/uploads/{filename}", datatype = os.path.splitext(file.filename)[1],user_id=session.get('id',1))
            db.add(upload)
            db.commit()
            flash('file uploaded and saved','success')
            session['uploaded_file'] = f"/static/uploads/{filename}"
            return redirect(request.url)
        else:
            flash('wrong file selected, only csv, xlxs and json files allowed','danger')
            return redirect(request.url)
   
    return render_template('upload.html',title='upload new Image')


@app.route('/files')
def filelisting():
    db = opendb()
    filelist = db.query(DataSet).all()
    db.close()
    return render_template('files.html', filelist=filelist)

@app.route('/logout')
def logout():
    if "isauth" in session:
        session.pop('isauth')
    return redirect ("/")


@app.route('/path')
def path():
    return render_template('expression')

@app.route('/predict/<int:id>')
def predict(id):
    sess=opendb()
    data = sess.query(DataSet).filter(DataSet.id==id).first()
    sess.commit()
    print(data)
    df = pd.read_csv(data.filepath[1:])
    sess.close()
    columns = df.columns.tolist()
    return render_template('column_selector.html',data=data,df = df.head().to_html(),col1 = columns,col2=columns)

@app.route('/train',methods =['GET','POST'])
def train():
    if request.method == "POST":
        session['col1'] = request.form.get('col1')
        session['filepath'] = request.form.get('filepath')
        session['col2'] = request.form.get('col2')
        flash("columns selected",'success')
        return redirect('/train')
    
    return render_template('train.html')
    
@app.route('/train_timeseries')
def train_timeseries():
    return redirect('/train')

@app.route('/delete/<int:id>')
def delete(id):
    sess=opendb()
    try:
        sess.query(DataSet).filter(DataSet.id==id).delete()
        sess.commit()
        sess.close()
        return redirect('/files')
    except Exception as e:
        return f"There was a problem while deleting {e}"


if __name__ == '__main__':
  app.run(host='127.0.0.1', port=5000, debug=True)





 

