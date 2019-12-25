from lind import app
from flask_login import UserMixin, LoginManager, AnonymousUserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    time = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.String(64), nullable=False)
    text = db.Column(db.Text, unique=False, nullable=False)
    author = db.relationship('User', backref=db.backref('articles'))
    path = db.Column(db.String(128), unique=True, nullable=False)
    type = db.Column(db.String(16), default=False, nullable=False)
    tags = db.relationship('Tag', backref=db.backref('article'))

    def __init__(self, title, text):
        self.title = title
        self.text = text

    def __repr__(self):
        return '<Entries %r>' % self.title


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    @staticmethod
    def insert_admin(email, username, password):
        user = User(email=email, username=username, password=password)
        db.session.add(user)
        db.session.commit()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True

    def is_active(self):
        return True

    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

    def get_id(self):
        return self.id

    """这里是否可以考虑使用其他网站的 api 头像"""


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_uer(user_id):
    return User.query.filter_by(id=user_id).first()


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_name = db.Column(db.String(20), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)

    @staticmethod
    def del_by_name(name):
        tags = Tag.query.filter_by(tag_name=name)
        for tag in tags:
            db.session.delete(tag)
        db.session.commit()


class LoginInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer, nullable=True)
    ip_addr = db.Column(db.String(15), nullable=False)
    time = db.Column(db.DateTime)
    is_correct_passwd = db.Column(db.Boolean, nullable=False)


class BlackList(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.DateTime)
    ip_addr = db.Column(db.String(15), nullable=False)
