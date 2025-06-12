import os
from datetime import timedelta


class Config:

    # MongoDB Configuration
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/moviedb')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'moviedb')

    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-secret-key')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # CORS Configuration
    CORS_ORIGINS = ["*"]

    # Other configurations
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/moviedb')


class ProductionConfig(Config):
    DEBUG = False
    MONGO_URI = os.getenv('MONGO_URI')


class TestingConfig(Config):
    TESTING = True
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/moviedb_test')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
