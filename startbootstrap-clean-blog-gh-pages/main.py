import smtplib

from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_ckeditor import CKEditorField, CKEditor
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, CSRFProtect
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from wtforms import StringField
from wtforms.fields.simple import PasswordField, EmailField
from wtforms.validators import InputRequired
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, UserMixin, logout_user, login_user, current_user, login_manager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
ckeditor = CKEditor(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///blog_post.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Blogs(UserMixin, db.Model):
    __tablename__ = 'blogs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False)
    subtitle = db.Column(db.String(255), unique=False, nullable=False)
    name = db.Column(db.String, unique=False, nullable=False)
    content = db.Column(db.Text, nullable=False)
    dates = db.Column(db.String(300), nullable=False)

    author_id = db.Column(db.Integer, ForeignKey('users.id'))
    author = relationship("Users", back_populates="posts")
    comments = relationship("Comment",back_populates="comment_blog")


class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(255), unique=True)
    user_password = db.Column(db.String(255))
    user_name = db.Column(db.String(255))
    posts = relationship("Blogs", back_populates="author")
    comments = relationship('Comment',back_populates='comment_author')
    def secure_password(self, password):
        self.user_password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)

class Comment(UserMixin,db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text(500))
    comment_author_id = db.Column(db.Integer,ForeignKey('users.id'))
    comment_author = relationship("Users",back_populates="comments")

    post_id  = db.Column(db.Integer,ForeignKey('blogs.id'))
    comment_blog = relationship("Blogs",back_populates="comments")

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


def admin_route(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return func(*args, **kwargs)

    return wrapper


def title_n():
    response = Blogs.query.all()
    return response


@app.route('/')
def start():
    title_name = title_n()
    return render_template("index.html", responses=title_name)


@app.route('/about')
@login_required
def about_me():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
@login_required
def contact_me():
    if request.method == "POST":
        data = request.form

        name = data['name']
        email = data['email']
        phone = data['phone']
        message = data['message']

        send_message(name, email, phone, message)

        return render_template('contact.html', msg=True)
    return render_template('contact.html', msg=False)


def send_message(name, email, phone, message):
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login("marshamark2020@gmail.com", "czck gvhv juvn uajz")
        connection.sendmail(
            from_addr="marshamark2020@gmail.com",
            to_addrs="marshamark2020@gmail.com",
            msg=f"Subject:New message\n\nName:{name}\nPhone NO:{phone}\nEmail:{email}\nMessage:{message}"
        )


class BlogpostForm(FlaskForm):
    blog_content = CKEditorField('Comment Below', validators=[InputRequired()])


@app.route('/blogpost/<blog_post_id>', methods=['GET', 'POST'])
@login_required
def blog_post(blog_post_id):
        form = BlogpostForm()
        # all_comments = db.session.query(Comment, Users.user_name, Users.user_email).join(Users).all()
        blog_selected = Blogs.query.filter_by(id=blog_post_id).first()
        comments = db.session.query(Comment, Users.user_name, Users.user_email)\
                        .join(Users)\
                        .filter(Comment.post_id == blog_selected.id)\
                        .all()
        
        if form.validate_on_submit():
            user_comment = form.blog_content.data
            user_insert_comment = Comment(
                text=user_comment,
                comment_author_id=current_user.id,
                post_id=blog_selected.id,
                )
            db.session.add(user_insert_comment)
            db.session.commit()
            return render_template('blog.html', comments=comments, form=form, response=blog_selected)

        return render_template('blog.html',comments=comments, form=form, response=blog_selected)


# make a make-post form
class MyForm(FlaskForm):
    blog_title = StringField('Title', validators=[InputRequired()])
    blog_sub_title = StringField('Sub title', validators=[InputRequired()])
    writer_name = StringField('Writers name', validators=[InputRequired()])
    blog_content = CKEditorField('Content', validators=[InputRequired()])


@app.route('/new-post', methods=['GET', 'POST'])
@login_required
@admin_route
def make_post():
    Form = MyForm()
    if Form.validate_on_submit():
        title = Form.blog_title.data
        subtitle = Form.blog_sub_title.data
        writer = Form.writer_name.data
        blog_content = Form.blog_content.data
        dates = datetime.now().strftime("%B %d, %Y")

        new_blog = Blogs(title=title, subtitle=subtitle, name=writer, content=blog_content, dates=dates)
        db.session.add(new_blog)
        db.session.commit()
        return redirect(url_for('start'))

    return render_template('make-post.html', form=Form)


# edit post
@app.route('/edit-post/<post_id>', methods=['GET', 'POST'])
@login_required
@admin_route
def edit_post(post_id):
    post_selected = Blogs.query.filter_by(id=post_id).first()
    edit_form = MyForm(
        blog_title=post_selected.title,
        blog_sub_title=post_selected.subtitle,
        writer_name=post_selected.name,
        blog_content=post_selected.content
    )
    if edit_form.validate_on_submit():
        post_selected.title = edit_form.blog_title.data
        post_selected.subtitle = edit_form.blog_sub_title.data
        post_selected.name = edit_form.writer_name.data
        post_selected.content = edit_form.blog_content.data

        db.session.commit()

        return redirect(url_for('blog_post', blog_post_id=post_id))

    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route('/<id>')
@login_required
@admin_route
def delete_post(id):
    post_selected = Blogs.query.filter_by(id=id).first()
    db.session.delete(post_selected)
    db.session.commit()
    return redirect(url_for('start'))


class RegisterForm(FlaskForm):
    email_address = EmailField("Email", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    username = StringField("User name", validators=[InputRequired()])


# route to register
@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        title_name = title_n()
        email = register_form.email_address.data
        password = register_form.password.data
        username = register_form.username.data

        user_selected = Users.query.filter_by(user_email=email).first()
        if user_selected:
            flash("The email already exists, please login", "danger")
            login_form = LoginForm()
            return render_template('login.html', form=login_form)

        user_registration = Users(user_email = email, user_name=username)
        user_registration.secure_password(password)
        db.session.add(user_registration)
        db.session.commit()
        login_user(user_registration)
        return render_template('index.html', responses=title_name)

    return render_template('register.html', form=register_form)


class LoginForm(FlaskForm):
    password = PasswordField("Password", validators=[InputRequired()])
    username = StringField("User name", validators=[InputRequired()])


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        i_username = login_form.username.data
        i_password = login_form.password.data

        user_selected = Users.query.filter_by(user_name=i_username).first()

        if user_selected:
            title_name = title_n()
            if check_password_hash(user_selected.user_password, i_password):
                login_user(user_selected)
                return render_template("index.html", responses=title_name)
            else:
                flash("Your Password is incorrect", "danger")
                return render_template("login.html", form=login_form)
        else:
            flash("You are not signed up,Please register", "danger")
            return render_template("login.html", form=login_form)

    return render_template('login.html', form=login_form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('start'))


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=3000)
