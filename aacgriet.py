from flask import Flask, render_template,redirect,url_for,session,request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField
from wtforms.validators import DataRequired,Email,EqualTo,ValidationError
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import ocrspace
import os




app = Flask(__name__)

app.secret_key=os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/news'
app.config['SECRET_KEY'] = "mysecretkey"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)



login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model,UserMixin):
    id= db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True ,nullable=False)
    username = db.Column(db.String, unique=True ,nullable=False)
    password = db.Column(db.String ,nullable=False)
    bio = db.Column(db.String, unique=False ,nullable=True)

class Group_chat(db.Model):
    chatno= db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True ,nullable=False)
    content = db.Column(db.String ,nullable=False)


class RegistrationForm(FlaskForm):
    username = StringField('username', validators =[DataRequired()])
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self,username):
        exists_username=User.query.filter_by(username=username.data).first()
        if exists_username:
            raise ValidationError("Username already exists")
        
class LoginForm(FlaskForm):
    username = StringField('username', validators =[DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
    submit = SubmitField('Submit')







@app.route("/")
def home():
    return render_template('index.html',logged="user_id" in session)


@app.route("/home")
def home1():
    if "user_id" in session:
        return render_template("index.html",logged="user_id" in session)
    else:
        return render_template("index.html")
    




@app.route("/group",methods=['GET','POST'])
def group():

    if request.method == "POST":
        new_user=Group_chat(username=session['user'],content= request.form.get("msg"))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('group'))
    
    chats = Group_chat.query.all()
    return render_template("group.html",logged="user_id" in session,chats=chats,user=session['user'])


@app.route("/news",methods=['GET','POST'])
def news():
    users = User.query.all()
    return render_template("news.html",logged="user_id" in session,users=users)


@app.route("/profile/<user>",methods=['GET','POST'])
def sepprofiles(user):
    user1 = User.query.filter_by(username=user).first()
    return render_template("admins.html",logged="user_id" in session,user1=user1,realme=session['user'])

#for ocr
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 
@app.route("/img2txt",methods=['GET','POST'])
def img2text():
    if request.method == 'POST':
        uploaded_img = request.files['uploaded-file']
        img_filename = secure_filename(uploaded_img.filename)
        uploaded_img.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
        session['uploaded_img_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
        img_file_path = session.get('uploaded_img_file_path', None)
        api = ocrspace.API()
        txt=api.ocr_file(img_file_path)
        return render_template('img2txt.html', txt=txt)
    
       
    return render_template("img2txt.html")
###

@app.route("/admins",methods=['GET','POST'])
def admins():
    if request.method == "POST":
        newbio = request.form.get("newbio")
        user = User.query.filter_by(username=session['user']).first()
        user.bio=newbio
        db.session.commit()

    user1 = User.query.filter_by(username=session['user']).first()
    return render_template("admins.html",logged="user_id" in session,user1=user1,realme=session['user'])

@app.route("/logout",methods=['GET','POST'])
#@login_required
def logout():
    #load_user()
    session.pop("user_id")
    session.pop('user')

    return redirect(url_for('login'))

@app.route("/login",methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password,form.password.data):
                load_user(user)
                session['user_id']=user.id
                session['user'] = form.username.data

                return redirect(url_for('home1'))
    return render_template("login.html",form=form)

@app.route("/register",methods=['GET','POST'])
def register():
    form=RegistrationForm()

    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data)
        new_user=User(username=form.username.data,email=form.email.data,password=hashed_password,bio="")
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))


    return render_template("register.html",form=form)




app.run(debug=True)

