import streamlit as st
import requests
import json
from datetime import datetime, date
import pandas as pd
import os

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5001/api")

# Page configuration
st.set_page_config(
    page_title="Movie Management System",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header { 
        font-size: 3rem; 
        color: #1f77b4; 
        text-align: center; 
        margin-bottom: 2rem; 
    }
    .movie-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f9f9f9;
    }
    .success-message {
        color: #28a745;
        font-weight: bold;
    }
    .error-message {
        color: #dc3545;
        font-weight: bold;
    }
    .rating-high {
        background-color: #28a745;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
    }
    .rating-medium {
        background-color: #ffc107;
        color: black;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
    }
    .rating-low {
        background-color: #dc3545;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def make_request(method, endpoint, data=None):
    """Make HTTP request to Flask API"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)

        return response.json(), response.status_code
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to the server. Make sure Flask API is running."}, 500
    except Exception as e:
        return {"error": str(e)}, 500


def get_rating_class(rating):
    """Get CSS class based on rating"""
    try:
        rating = float(rating)
        if rating >= 7:
            return "rating-high"
        elif rating >= 5:
            return "rating-medium"
        else:
            return "rating-low"
    except (ValueError, TypeError):
        return "rating-low"


def search_movies():
    """Advanced search functionality"""
    st.subheader("🔍 Advanced Movie Search")

    # --- Search form ---
    with st.form("search_form"):
        col1, col2 = st.columns(2)
        with col1:
            search_query = st.text_input("Search Query", placeholder="Search by title, description, genre, or director")
            min_rating = st.slider("Minimum Rating", 0.0, 10.0, 0.0, 0.1)
        with col2:
            min_year = st.number_input("From Year", min_value=1800, max_value=datetime.now().year, value=1900)
            max_year = st.number_input("To Year", min_value=1800, max_value=datetime.now().year + 5, value=datetime.now().year)
        submitted = st.form_submit_button("🔍 Search")

    # --- Only run search if form submitted or query present ---
    if submitted or search_query:
        response, status_code = make_request("GET", "/movies")
        if status_code == 200:
            movies = response.get("movies", [])
            filtered_movies = []
            for movie in movies:
                # Text search
                if search_query:
                    search_fields = [
                        movie.get('title', '').lower(),
                        movie.get('description', '').lower(),
                        movie.get('genre', '').lower(),
                        movie.get('director', '').lower()
                    ]
                    if not any(search_query.lower() in field for field in search_fields):
                        continue
                # Rating filter
                if movie.get('rating', 0) < min_rating:
                    continue
                # Year filter
                year = movie.get('release_year', 0)
                if year < min_year or year > max_year:
                    continue
                filtered_movies.append(movie)

            st.write(f"**Found {len(filtered_movies)} movies**")

            if filtered_movies:
                for movie in filtered_movies:
                    display_movie_card(movie)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"✏️ Edit", key=f"search_edit_{movie['_id']}"):
                            st.session_state.edit_movie_id = movie['_id']
                            st.session_state.show_edit_form = True
                    with col2:
                        if st.button(f"🗑️ Delete", key=f"search_delete_{movie['_id']}"):
                            delete_response, delete_status = make_request("DELETE", f"/movies/{movie['_id']}")
                            if delete_status == 200:
                                st.success("Movie deleted successfully!")
                                st.rerun()
                            else:
                                st.error(f"Error deleting movie: {delete_response.get('error')}")
                    with col3:
                        movie_json = json.dumps(movie, indent=2, default=str)
                        st.download_button(
                            "📥 Export",
                            data=movie_json,
                            file_name=f"movie_{movie['_id']}.json",
                            mime="application/json",
                            key=f"search_download_{movie['_id']}"
                        )
            else:
                st.info("No movies match your search criteria.")
        else:
            st.error(f"❌ Error searching movies: {response.get('error', 'Unknown error')}")

def display_movie_card(movie):
    """Display movie in a clean, Streamlit-friendly card format"""
    with st.container():
        st.markdown(
            f"""
            <div style="
                background-color: #23272f;
                border: 1px solid #2c2c3a;
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                border-left: 4px solid #667eea;
            ">
                <h3 style="
                    color: #f1f5f9;
                    margin: 0 0 1rem 0;
                    font-size: 1.5rem;
                    font-weight: 600;
                ">🎬 {movie['title']}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📅 Release Year:**")
            st.info(f"{movie['release_year']}")

            st.markdown("**🎭 Genre:**")
            st.info(f"{movie['genre']}")

        with col2:
            st.markdown("**🎬 Director:**")
            st.info(f"{movie.get('director', 'N/A')}")

            rating_class = get_rating_class(movie['rating'])
            st.markdown("**⭐ Rating:**")
            st.markdown(f'<span class="{rating_class}">{movie["rating"]}/10</span>', unsafe_allow_html=True)

        st.markdown("**📝 Description:**")
        st.success(f"{movie['description']}")

        st.markdown("---")

def create_movie_form():
    """Create movie form"""
    st.subheader("🎬 Add New Movie")

    with st.form("create_movie_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Movie Title*", placeholder="Enter movie title")
            release_year = st.number_input("Release Year*", min_value=1800, max_value=datetime.now().year + 5,
                                           value=2023)
            genre = st.text_input("Genre*", placeholder="e.g., Action, Comedy, Drama")

        with col2:
            director = st.text_input("Director", placeholder="Director name (optional)")
            rating = st.number_input("Rating (0-10)*", min_value=0.0, max_value=10.0, value=5.0, step=0.1)

        description = st.text_area("Description*", placeholder="Movie description", height=100)

        submitted = st.form_submit_button("Add Movie", type="primary")

        if submitted:
            if not all([title, description, genre]):
                st.error("Please fill in all required fields (marked with *)")
            else:
                movie_data = {
                    "title": title,
                    "description": description,
                    "release_year": int(release_year),
                    "genre": genre,
                    "director": director if director else "",
                    "rating": float(rating)
                }

                response, status_code = make_request("POST", "/movies", movie_data)

                if status_code == 201:
                    st.success("✅ Movie added successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {response.get('error', 'Unknown error')}")


def display_all_movies():
    """Display all movies"""
    st.subheader("🎬 All Movies")

    response, status_code = make_request("GET", "/movies")

    if status_code == 200:
        movies = response.get("movies", [])

        if not movies:
            st.info("No movies found. Add your first movie!")
        else:
            # Search functionality
            search_query = st.text_input("🔍 Search movies",
                                         placeholder="Search by title, description, genre, or director")

            if search_query:
                search_response, search_status = make_request("GET", f"/movies/search?q={search_query}")
                if search_status == 200:
                    movies = search_response.get("movies", [])

            # Filter by genre
            all_genres = list(set([movie['genre'] for movie in movies]))
            selected_genre = st.selectbox("🎭 Filter by Genre", ["All Genres"] + sorted(all_genres))

            if selected_genre != "All Genres":
                movies = [movie for movie in movies if movie['genre'] == selected_genre]

            # Sort options
            sort_option = st.selectbox("🔄 Sort by", ["Title", "Release Year", "Rating", "Recently Added"])

            if sort_option == "Title":
                movies = sorted(movies, key=lambda x: x['title'])
            elif sort_option == "Release Year":
                movies = sorted(movies, key=lambda x: x['release_year'], reverse=True)
            elif sort_option == "Rating":
                movies = sorted(movies, key=lambda x: x['rating'], reverse=True)

            st.write(f"**Showing {len(movies)} movies**")

            # Display movies in a grid
            cols = st.columns(2)
            for i, movie in enumerate(movies):
                with cols[i % 2]:
                    display_movie_card(movie)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"✏️ Edit", key=f"edit_{movie['_id']}"):
                            st.session_state.edit_movie_id = movie['_id']
                            st.session_state.show_edit_form = True

                    with col2:
                        if st.button(f"🗑️ Delete", key=f"delete_{movie['_id']}"):
                            if st.session_state.get(f"confirm_delete_{movie['_id']}"):
                                delete_response, delete_status = make_request("DELETE", f"/movies/{movie['_id']}")
                                if delete_status == 200:
                                    st.success("Movie deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"Error deleting movie: {delete_response.get('error')}")
                            else:
                                st.session_state[f"confirm_delete_{movie['_id']}"] = True
                                st.warning("Click delete again to confirm")

                    with col3:
                        # Download movie as JSON
                        movie_json = json.dumps(movie, indent=2, default=str)
                        st.download_button(
                            "📥 Export",
                            data=movie_json,
                            file_name=f"movie_{movie['_id']}.json",
                            mime="application/json",
                            key=f"download_{movie['_id']}"
                        )
    else:
        st.error(f"❌ Error loading movies: {response.get('error', 'Unknown error')}")


def edit_movie_form():
    """Edit movie form"""
    if not st.session_state.get('edit_movie_id'):
        return

    movie_id = st.session_state.edit_movie_id

    # Get movie details
    response, status_code = make_request("GET", f"/movies/{movie_id}")

    if status_code != 200:
        st.error("Movie not found")
        return

    movie = response['movie']

    st.subheader("✏️ Edit Movie")

    with st.form("edit_movie_form"):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Movie Title*", value=movie['title'])
            release_year = st.number_input("Release Year*", min_value=1800, max_value=datetime.now().year + 5,
                                           value=movie['release_year'])
            genre = st.text_input("Genre*", value=movie['genre'])

        with col2:
            director = st.text_input("Director", value=movie.get('director', ''))
            rating = st.number_input("Rating (0-10)*", min_value=0.0, max_value=10.0, value=movie['rating'], step=0.1)

        description = st.text_area("Description*", value=movie['description'], height=100)

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Update Movie", type="primary")
        with col2:
            cancelled = st.form_submit_button("Cancel")

        if cancelled:
            st.session_state.show_edit_form = False
            st.session_state.edit_movie_id = None
            st.rerun()

        if submitted:
            if not all([title, description, genre]):
                st.error("Please fill in all required fields (marked with *)")
            else:
                movie_data = {
                    "title": title,
                    "description": description,
                    "release_year": int(release_year),
                    "genre": genre,
                    "director": director,
                    "rating": float(rating)
                }

                response, status_code = make_request("PUT", f"/movies/{movie_id}", movie_data)

                if status_code == 200:
                    st.success("✅ Movie updated successfully!")
                    st.session_state.show_edit_form = False
                    st.session_state.edit_movie_id = None
                    st.rerun()
                else:
                    st.error(f"❌ Error: {response.get('error', 'Unknown error')}")


def analytics_dashboard():
    """Display analytics dashboard"""
    st.subheader("📊 Movie Analytics Dashboard")

    response, status_code = make_request("GET", "/movies")

    if status_code == 200:
        movies = response.get("movies", [])

        if not movies:
            st.info("No movies available for analytics.")
            return

        # Convert to DataFrame for analysis
        df = pd.DataFrame(movies)

        # Basic metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Movies", len(movies))

        with col2:
            avg_rating = df['rating'].mean()
            st.metric("Average Rating", f"{avg_rating:.1f}/10")

        with col3:
            total_genres = df['genre'].nunique()
            st.metric("Total Genres", total_genres)

        with col4:
            latest_year = df['release_year'].max()
            st.metric("Latest Release", latest_year)

        # Rating distribution
        st.subheader("⭐ Rating Distribution")
        col1, col2 = st.columns(2)

        with col1:
            rating_bins = pd.cut(df['rating'], bins=[0, 3, 5, 7, 10],
                                 labels=['Poor (0-3)', 'Fair (3-5)', 'Good (5-7)', 'Excellent (7-10)'])
            rating_counts = rating_bins.value_counts()
            st.bar_chart(rating_counts)

        with col2:
            st.write("**Rating Statistics:**")
            st.write(f"- Highest Rated: {df['rating'].max()}/10")
            st.write(f"- Lowest Rated: {df['rating'].min()}/10")
            st.write(f"- Median Rating: {df['rating'].median()}/10")

        # Genre analysis
        st.subheader("🎭 Genre Analysis")
        col1, col2 = st.columns(2)

        with col1:
            genre_counts = df['genre'].value_counts()
            st.bar_chart(genre_counts)
            st.caption("Movies by Genre")

        with col2:
            # Top genres by average rating
            genre_ratings = df.groupby('genre')['rating'].mean().sort_values(ascending=False)
            st.bar_chart(genre_ratings)
            st.caption("Average Rating by Genre")

        # Release year trends
        st.subheader("📅 Release Year Trends")
        year_counts = df['release_year'].value_counts().sort_index()
        st.line_chart(year_counts)

        # Top movies tables
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🏆 Top Rated Movies")
            top_movies = df.nlargest(10, 'rating')[['title', 'rating', 'genre', 'release_year']]
            st.dataframe(top_movies, use_container_width=True)

        with col2:
            st.subheader("📅 Recent Movies")
            recent_movies = df.nlargest(10, 'release_year')[['title', 'release_year', 'rating', 'genre']]
            st.dataframe(recent_movies, use_container_width=True)

        # Director analysis (if directors are available)
        directors_with_movies = df[df['director'].notna() & (df['director'] != '')]
        if not directors_with_movies.empty:
            st.subheader("🎬 Director Analysis")
            director_stats = directors_with_movies.groupby('director').agg({
                'title': 'count',
                'rating': 'mean'
            }).rename(columns={'title': 'movie_count', 'rating': 'avg_rating'})
            director_stats = director_stats[director_stats['movie_count'] >= 2]  # Only directors with 2+ movies

            if not director_stats.empty:
                director_stats = director_stats.sort_values('avg_rating', ascending=False)
                st.dataframe(director_stats, use_container_width=True)

    else:
        st.error(f"❌ Error loading analytics: {response.get('error', 'Unknown error')}")


def main():
    """Main application"""
    # Initialize session state
    if 'show_edit_form' not in st.session_state:
        st.session_state.show_edit_form = False
    if 'edit_movie_id' not in st.session_state:
        st.session_state.edit_movie_id = None

    # Header
    st.markdown('<h1 class="main-header">🎬 Movie Management System</h1>', unsafe_allow_html=True)

    # Check API connection
    health_response, health_status = make_request("GET", "/health")
    if health_status != 200:
        st.error(
            "⚠️ Cannot connect to the backend API. Please ensure the Flask server is running on http://localhost:5001")
        st.stop()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["🎬 Add Movie", "📽️ View Movies", "🔍 Search Movies", "📊 Analytics"]
    )

    # API status
    st.sidebar.success("✅ API Connected")
    st.sidebar.info(f"Status: {health_response.get('status', 'Connected')}")

    # Main content
    if st.session_state.show_edit_form:
        edit_movie_form()
    elif page == "🎬 Add Movie":
        create_movie_form()
    elif page == "📽️ View Movies":
        display_all_movies()
    elif page == "🔍 Search Movies":
        search_movies()
    elif page == "📊 Analytics":
        analytics_dashboard()


if __name__ == "__main__":
    main()