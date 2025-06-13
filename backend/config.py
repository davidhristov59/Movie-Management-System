import os


class Config:
    """Application configuration"""

    # MongoDB configuration
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = os.getenv('MONGO_PORT', '27017')
    MONGO_USERNAME = os.getenv('MONGO_ROOT_USERNAME')
    MONGO_PASSWORD = os.getenv('MONGO_ROOT_PASSWORD')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'moviedb')

    # Build MongoDB URI
    if MONGO_USERNAME and MONGO_PASSWORD:
        MONGO_URI = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{DATABASE_NAME}?authSource=admin"
    else:
        MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{DATABASE_NAME}"

    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    # CORS configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')