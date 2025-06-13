from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# MongoDB connection - simplified and fixed
mongo_host = os.getenv('MONGO_HOST', 'localhost')
mongo_port = os.getenv('MONGO_PORT', '27017')
mongo_username = os.getenv('MONGO_ROOT_USERNAME')
mongo_password = os.getenv('MONGO_ROOT_PASSWORD')
database_name = os.getenv('DATABASE_NAME', 'moviedb')

# Build MongoDB URI
if mongo_username and mongo_password:
    mongo_uri = f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{database_name}?authSource=admin"
else:
    mongo_uri = f"mongodb://{mongo_host}:{mongo_port}/{database_name}"

# Create single MongoDB connection
try:
    client = MongoClient(mongo_uri)
    db = client[database_name]
    movies_collection = db.movies
    # Test connection
    client.admin.command('ping')
    print(f"✅ Connected to MongoDB at {mongo_host}:{mongo_port}")
except Exception as e:
    print(f"❌ Failed to connect to MongoDB: {e}")
    exit(1)


def serialize_movie(movie):
    """Convert MongoDB document to JSON serializable format"""
    if movie:
        movie['_id'] = str(movie['_id'])
        return movie
    return None


def validate_movie_data(data):
    """Validate movie data"""
    errors = []
    required_fields = ['title', 'description', 'release_year', 'genre', 'rating']

    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"{field} is required")

    if 'rating' in data:
        try:
            rating = float(data['rating'])
            if rating < 0 or rating > 10:
                errors.append("Rating must be between 0 and 10")
        except (ValueError, TypeError):
            errors.append("Rating must be a valid number")

    if 'release_year' in data:
        try:
            year = int(data['release_year'])
            current_year = datetime.now().year
            if year < 1800 or year > current_year + 10:
                errors.append(f"Release year must be between 1800 and {current_year + 10}")
        except (ValueError, TypeError):
            errors.append("Release year must be a valid number")

    return errors


@app.route('/api/movies', methods=['POST'])
def create_movie():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate data
        errors = validate_movie_data(data)
        if errors:
            return jsonify({'errors': errors}), 400

        # Create movie document
        movie_dict = {
            'title': data['title'].strip(),
            'description': data['description'].strip(),
            'release_year': int(data['release_year']),
            'genre': data['genre'].strip(),
            'director': data.get('director', '').strip(),
            'rating': float(data['rating']),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        # Insert into database
        result = movies_collection.insert_one(movie_dict)
        movie_dict['_id'] = str(result.inserted_id)

        return jsonify({
            'message': 'Movie added successfully',
            'movie': serialize_movie(movie_dict)
        }), 201

    except Exception as e:
        print(f"Error creating movie: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/movies', methods=['GET'])
def get_all_movies():
    try:
        movies = list(movies_collection.find().sort('created_at', -1))
        return jsonify({'movies': [serialize_movie(m) for m in movies]}), 200
    except Exception as e:
        print(f"Error fetching movies: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


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
        print(f"Error fetching movie: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/movies/<movie_id>', methods=['PUT'])
def update_movie(movie_id):
    try:
        if not ObjectId.is_valid(movie_id):
            return jsonify({'error': 'Invalid movie ID'}), 400

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate data (partial validation for updates)
        update_data = {}
        allowed_fields = ['title', 'description', 'release_year', 'genre', 'director', 'rating']

        for field in allowed_fields:
            if field in data and data[field] is not None:
                if field in ['title', 'description', 'genre', 'director']:
                    update_data[field] = str(data[field]).strip()
                elif field == 'release_year':
                    update_data[field] = int(data[field])
                elif field == 'rating':
                    update_data[field] = float(data[field])

        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400

        update_data['updated_at'] = datetime.utcnow()

        result = movies_collection.update_one(
            {'_id': ObjectId(movie_id)},
            {'$set': update_data}
        )

        if result.matched_count == 0:
            return jsonify({'error': 'Movie not found'}), 404

        updated_movie = movies_collection.find_one({'_id': ObjectId(movie_id)})
        return jsonify({
            'message': 'Movie updated successfully',
            'movie': serialize_movie(updated_movie)
        }), 200

    except Exception as e:
        print(f"Error updating movie: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


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
        print(f"Error deleting movie: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/movies/search', methods=['GET'])
def search_movies():
    try:
        query = request.args.get('q', '').strip()
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
        print(f"Error searching movies: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        # Test database connection
        client.admin.command('ping')
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow(),
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow(),
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("🎬 Starting Movie Management API...")
    print(f"📊 Database: {database_name}")
    print(f"🔗 MongoDB URI: {mongo_uri.split('@')[0]}@***")
    app.run(debug=True, host='0.0.0.0', port=5001)