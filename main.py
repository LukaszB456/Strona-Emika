from flask import Flask, session, redirect, url_for, request, render_template, flash, current_app
from flask_login import LoginManager, UserMixin, \
                                login_required, login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta, datetime
import random
import smtplib  # lub inna biblioteka do maili
import os


app = Flask(__name__)
app.secret_key = 'SECRETKEY'
app.permanent_session_lifetime = timedelta(minutes=2)  # auto logout po 30 minutach
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'  # jeśli niezalogowany -> przekierowanie do login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_folder = db.Column(db.String(255), nullable=True)
    is_visible = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

@app.route("/our-work")
def our_work():
    posts = (
        Post.query
        .filter_by(is_visible=True)
        .order_by(Post.created_at.desc())
        .all()
    )

    for post in posts:
        images = []
        if post.image_folder:
            folder_path = os.path.join(
                current_app.static_folder,
                "uploads",
                post.image_folder
            )

            if os.path.exists(folder_path):
                images = os.listdir(folder_path)

        post.images = images  # dynamiczne pole tylko do szablonu

    return render_template("our_work.html", posts=posts)

@app.route("/add-post", methods=["POST"])
@login_required
def add_post():
    title = request.form.get("title")
    content = request.form.get("content")
    images = request.files.getlist("images")  # wiele plików

    if not title or not content:
        flash("Tytuł i treść są wymagane!", "danger")
        return redirect(url_for("our_work"))

    # utwórz folder dla posta
    post_folder = f"post_{int(datetime.utcnow().timestamp())}"
    upload_path = os.path.join(app.static_folder, "uploads", post_folder)
    os.makedirs(upload_path, exist_ok=True)

    # zapisz pliki
    for img in images:
        if img.filename != "":
            filename = secure_filename(img.filename)
            img.save(os.path.join(upload_path, filename))

    # dodaj wpis do bazy
    post = Post(
        title=title,
        content=content,
        image_folder=post_folder,
        is_visible=True
    )

    db.session.add(post)
    db.session.commit()

    flash("Dodano wpis!", "success")
    return redirect(url_for("our_work"))


if __name__ == "__main__":
    app.run(debug=True)
