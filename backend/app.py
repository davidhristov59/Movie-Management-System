from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from config import Config
from models import Movie

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# MongoDB connection
# mongo_host = os.getenv('MONGO_HOST', 'localhost')
# mongo_port = os.getenv('MONGO_PORT', '27017')
# mongo_username = os.getenv('MONGO_ROOT_USERNAME')
# mongo_password = os.getenv('MONGO_ROOT_PASSWORD')
# database_name = os.getenv('DATABASE_NAME', 'moviedb')

client = MongoClient(app.config['MONGO_URI'])
db = client[app.config['DATABASE_NAME']]
movies_collection = db.movies

# mongo_uri = f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{database_name}?authSource=admin"


def serialize_movie(movie):
    """Convert MongoDB document to JSON serializable format"""
    if movie:
        movie['_id'] = str(movie['_id'])
        return movie
    return None


@app.route('/api/movies', methods=['POST'])
def create_movie():
    try:
        data = request.get_json()
        movie = Movie.from_dict(data)
        errors = movie.validate()

        if errors:
            return jsonify({'errors': errors}), 400

        movie_dict = movie.to_dict()
        result = movies_collection.insert_one(movie_dict)
        movie_dict['_id'] = str(result.inserted_id)

        return jsonify({'message': 'Movie added successfully', 'movie': serialize_movie(movie_dict)}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/movies', methods=['GET'])
def get_all_movies():
    try:
        movies = list(movies_collection.find().sort('created_at', -1))
        return jsonify({'movies': [serialize_movie(m) for m in movies]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/movies/<movie_id>', methods=['GET'])
def get_movie(movie_id):
    try:
        if not ObjectId.is_valid(movie_id):
            return jsonify({'error': 'Invalid movie ID'}), 400

        movie = movies_collection.find_one({'_id': ObjectId(movie_id)})
        if not movie:
            return jsonify({'error': 'Movie not found'}), 404

        return jsonify({'movie': serialize_movie(movie)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/movies/<movie_id>', methods=['PUT'])
def update_movie(movie_id):
    try:
        if not ObjectId.is_valid(movie_id):
            return jsonify({'error': 'Invalid movie ID'}), 400

        data = request.get_json()
        update_data = {}
        allowed_fields = ['title', 'description', 'release_year', 'genre', 'director', 'rating']

        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400

        update_data['updated_at'] = datetime.utcnow()

        result = movies_collection.update_one({'_id': ObjectId(movie_id)}, {'$set': update_data})

        if result.matched_count == 0:
            return jsonify({'error': 'Movie not found'}), 404

        updated_movie = movies_collection.find_one({'_id': ObjectId(movie_id)})
        return jsonify({'message': 'Movie updated', 'movie': serialize_movie(updated_movie)}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/movies/<movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    try:
        if not ObjectId.is_valid(movie_id):
            return jsonify({'error': 'Invalid movie ID'}), 400

        result = movies_collection.delete_one({'_id': ObjectId(movie_id)})
        if result.deleted_count == 0:
            return jsonify({'error': 'Movie not found'}), 404

        return jsonify({'message': 'Movie deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/movies/search', methods=['GET'])
def search_movies():
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'movies': []}), 200

        search_filter = {
            '$or': [
                {'title': {'$regex': query, '$options': 'i'}},
                {'description': {'$regex': query, '$options': 'i'}},
                {'genre': {'$regex': query, '$options': 'i'}},
                {'director': {'$regex': query, '$options': 'i'}}
            ]
        }

        movies = list(movies_collection.find(search_filter).sort('created_at', -1))
        return jsonify({'movies': [serialize_movie(m) for m in movies]}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow()}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
