// MongoDB Initialization Script for Movie Recommender
// This script runs when MongoDB container starts for the first time

// Switch to the moviedb database
db = db.getSiblingDB('moviedb');

// Create collections
db.createCollection('movies');

// Create indexes for movies collection
db.movies.createIndex({ "title": 1 });
db.movies.createIndex({ "genre": 1 });
db.movies.createIndex({ "year": 1 });
db.movies.createIndex({ "imdb_rating": -1 });
db.movies.createIndex({ "title": "text", "description": "text" }); // For text search


print('🎬 Inserting sample movie data...');

// Insert sample movies
db.movies.insertMany([
    {
        "title": "The Shawshank Redemption",
        "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        "release_year": 1994,
        "genre": "Drama",
        "director": "Frank Darabont",
        "rating": 9.3,
        "created_at": new Date(),
        "updated_at": new Date()
    },
   {
        "title": "The Godfather",
        "description": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
        "release_year": 1972,
        "genre": "Crime, Drama",
        "director": "Francis Ford Coppola",
        "rating": 9.2,
        "created_at": new Date(),
        "updated_at": new Date()
    },
    {
        "title": "The Dark Knight",
        "description": "When the menace known as The Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests.",
        "release_year": 2008,
        "genre": "Action, Crime, Drama",
        "director": "Christopher Nolan",
        "rating": 9.0,
        "created_at": new Date(),
        "updated_at": new Date()
    },
    {
        "title": "Pulp Fiction",
        "description": "The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.",
        "release_year": 1994,
        "genre": "Crime, Drama",
        "director": "Quentin Tarantino",
        "rating": 8.9,
        "created_at": new Date(),
        "updated_at": new Date()
    },
    {
        "title": "Inception",
        "description": "A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea.",
        "release_year": 2010,
        "genre": "Action, Sci-Fi, Thriller",
        "director": "Christopher Nolan",
        "rating": 8.8,
        "created_at": new Date(),
        "updated_at": new Date()
    },
    {
        "title": "The Matrix",
        "description": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
        "release_year": 1999,
        "genre": "Action, Sci-Fi",
        "director": "Lana Wachowski",
        "rating": 8.7,
        "created_at": new Date(),
        "updated_at": new Date()
    }
]);


// Print collection counts
print('📋 Database initialization complete!');

print('📊 Collection counts:');
print('   Movies:', db.movies.countDocuments());


print('🎉 MongoDB initialization finished successfully!');