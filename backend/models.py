from datetime import datetime
from typing import Optional, Dict, Any

from pymongo import MongoClient
from bson import ObjectId
from config import Config

class Movie:
    def __init__(self, title: str, description: str, release_year: int, genre: str,
                 director: str = "", rating: float = 0.0, _id: Optional[str] = None):

        self._id = _id
        self.title = title
        self.description = description
        self.release_year = release_year
        self.genre = genre
        self.director = director
        self.rating = rating
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


    def to_dict(self) -> Dict[str, Any]:
        """Convert movie to dictionary format"""
        return {
            '_id': self._id,
            'title': self.title,
            'description': self.description,
            'release_year': self.release_year,
            'genre': self.genre,
            'director': self.director,
            'rating': self.rating,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Movie':
        """Create Movie instance from a dictionary (such as one loaded from a db or received as JSON"""
        return cls(
            title=data.get('title', ''),
            description=data.get('description', ''),
            release_year=data.get('release_year', 0),
            genre=data.get('genre', ''),
            director=data.get('director', ''),
            rating=float(data.get('rating', 0)),
            _id=str(data.get('_id', ''))
        )

    def validate(self) -> Dict[str, str]:
        """Validate movie data and return errors if any"""
        errors = {}

        if not self.title or len(self.title.strip()) == 0:
            errors['title'] = 'Title is required'

        if not self.description:
            errors['description'] = 'Description is required'

        if not isinstance(self.release_year, int) or self.release_year <= 1800:
            errors['release_year'] = 'Invalid release year'

        if not self.genre:
            errors['genre'] = 'Genre is required'

        if self.rating < 0 or self.rating > 10:
            errors['rating'] = 'Rating must be between 0 and 10'

        return errors