from flask import Flask, session, redirect, url_for, request, render_template, flash
from flask_login import LoginManager, UserMixin, \
                                login_required, login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta, datetime
import random
import smtplib  # lub inna biblioteka do maili

app = Flask(__name__)
app.secret_key = 'SECRETKEY'
app.permanent_session_lifetime = timedelta(minutes=2)  # auto logout po 30 minutach
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # jeśli niezalogowany -> przekierowanie do login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

with app.app_context():
    db.create_all() 
    if not User.query.filter_by(email="test@abc.pl").first():
        user1 = User(
            email = "test@abc.pl",
            password = "haslo"
        )
        db.session.add(user1)
        db.session.commit()
        print(User.query.filter_by(email="test@abc.pl").first())


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")  # Możesz zmienić na 'about.html', jeśli chcesz osobny plik

@app.route("/contact")
def contact():
    return render_template("contact.html")  # lub inny szablon, np. 'contact.html'

@app.route("/login", methods=["GET", "POST"])
def login():
    print("logowanko")
    if request.method == 'POST':
        print("wchodzimty do posta")
        email = request.form.get("emailInput")
        password = request.form.get("passwordInput")
        
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            print("sex")
            login_user(user)
            print("zalogowano, sex!")
            return redirect(url_for("about"))
        else:
            print("gowno dupa")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
