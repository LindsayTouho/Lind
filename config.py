import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db/sqlite.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = b'tfCdBK9@sdZ42$vJBr#95Euiq!7a39'
    TIME_DELTA = 8
    BASE_URL = 'example.com'
    RESOURCE_PATH = os.path.join(basedir, 'resource')
    EMAIL_ADDRESS = 'notification@mail.com'    # sendGride 使用的发送邮箱
    ADMIN_ADDRESS = 'admin@mail.com'
    API_KEY = ''   # sendGrid api key
    SITE_NAME = 'Lind'
    MAIL_NOTIFICATION = True

    G_VERIFY_SITE_KEY = ''
    G_VERIFY_SECRET_KEY = ''

    @staticmethod
    def init_app(app):
        pass


class TestConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db/sqlite.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = b'4C|f62,73e9d_49C'
    TIME_DELTA = 8
    BASE_URL = 'localhost'
    RESOURCE_PATH = os.path.join(basedir, 'resource')
    EMAIL_ADDRESS = ''
    API_KEY = ''
    SITE_NAME = 'Blog-Test'
    MAIL_NOTIFICATION = False

    G_VERIFY_SITE_KEY = ''
    G_VERIFY_SECRET_KEY = ''

    @staticmethod
    def init_app(app):
        pass


config = TestConfig
