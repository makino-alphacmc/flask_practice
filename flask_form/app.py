from flask import Flask, render_template, url_for, redirect, session, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from pytz import timezone
from sqlalchemy.engine import Engine
from sqlalchemy import event


# Flaskアプリケーションの初期化
app = Flask(__name__)

# セキュリティのため、SECRET_KEYは環境変数などから取得することが推奨。
app.config['SECRET_KEY'] = 'mysecretkey'

# データベースの設定
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemyとMigrateの初期化
db = SQLAlchemy(app)
Migrate(app, db)

#foriegn keyを有効にするためのコード
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# モデルの定義

# ユーザーモデル
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    administrator = db.Column(db.String(1))
    post = db.relationship('BlogPost', backref='author', lazy='dynamic')

    def __init__(self, email, username, password_hash, administrator):
        self.email = email
        self.username = username
        self.password_hash = password_hash
        self.administrator = administrator

    def __repr__(self):
        return f"Username: {self.username}"

# ブログポストモデル
class BlogPost(db.Model):
    __tablename__ = 'blog_post'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.DateTime, default=datetime.now(timezone('Asia/Tokyo')))
    title = db.Column(db.String(140))
    text = db.Column(db.Text)
    summary = db.Column(db.String(140))
    featured_image = db.Column(db.String(140))

    def __init__(self, title, text, featured_image, user_id, summary):
        self.title = title
        self.text = text
        self.featured_image = featured_image
        self.user_id = user_id
        self.summary = summary

    def __repr__(self):
        return f"PostID: {self.id}, Title: {self.title}, Author:{self.author} \n"

# フォームの定義
class RegistrationForm(FlaskForm):
    email = StringField('メールアドレス', validators=[DataRequired(), Email(message='有効なメールアドレスを入力してください')])
    username = StringField('ユーザー名', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired(), EqualTo('pass_confirm', message='パスワードが一致しません')])
    pass_confirm = PasswordField('パスワード(確認)', validators=[DataRequired()])
    submit = SubmitField('登録')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('このユーザー名は既に使用されています。')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('このメールアドレスは既に使用されています。')

# ルートの定義
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password_hash=form.password.data, administrator='0')
        db.session.add(user)
        db.session.commit()

        flash('ユーザー登録が完了しました！')
        return redirect(url_for('user_maintenance'))
    return render_template('register.html', form=form)

# ユーザー管理画面のルート1
@app.route('/user_maintenance')
def user_maintenance():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.id.desc()).paginate(page=page, per_page=10)
    return render_template('user_maintenance.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)
