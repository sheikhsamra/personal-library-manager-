import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Set page configuration
st.set_page_config(
    page_title="Personal Library Manager",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    body {
        background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
    }
    .main-header {
        font-size: 3rem !important;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.15);
    }
    .sub-header {
        font-size: 1.8rem !important;
        color: #3B82F6;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .success-message {
        padding: 1rem;
        background-color: #ECFDF5;
        border-left: 5px solid #10B981;
        border-radius: 0.375rem;
        margin-bottom: 1rem;
    }
    .warning-message {
        padding: 1rem;
        background-color: #FEF3C7;
        border-left: 5px solid #F59E0B;
        border-radius: 0.375rem;
        margin-bottom: 1rem;
    }
    .book-card {
        background-color: #ffffff;
        border-radius: 0.75rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 5px solid #3B82F6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .book-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0,0,0,0.15);
    }
    .read-badge {
        background-color: #10B981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .unread-badge {
        background-color: #F87171;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .action-button {
        margin-right: 0.5rem;
    }
    .stButton>button {
        border-radius: 0.5rem;
        background-color: #3B82F6;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1E40AF;
    }
</style>
""", unsafe_allow_html=True)

# Function to load lottie animations
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Initialize session state variables
if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None  # For editing book details

# Load library data from file if it exists
def load_library():
    try:
        if os.path.exists('library.json'):
            with open('library.json', 'r') as file:
                st.session_state.library = json.load(file)
            return True
        return False
    except Exception as e:
        st.error(f"Error loading library: {e}")
        return False

# Save library data to file
def save_library():
    try:
        with open('library.json', 'w') as file:
            json.dump(st.session_state.library, file)
        return True
    except Exception as e:
        st.error(f"Error saving library: {e}")
        return False

# Add a book to the library
def add_book(title, author, publication_year, genre, read_status):
    book = {
        'title': title,
        'author': author,
        'publication_year': publication_year,
        'genre': genre,
        'read_status': read_status,
        'added_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5)  # Slight delay for animation effect

# Edit a book in the library
def edit_book(index, title, author, publication_year, genre, read_status):
    if 0 <= index < len(st.session_state.library):
        st.session_state.library[index] = {
            'title': title,
            'author': author,
            'publication_year': publication_year,
            'genre': genre,
            'read_status': read_status,
            'added_date': st.session_state.library[index].get('added_date', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        }
        save_library()
        st.session_state.book_added = True  # Reuse flag to show update message
        time.sleep(0.5)

# Remove a book from the library
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        return True
    return False

# Search for books in the library
def search_books(search_term, search_by):
    search_term = search_term.lower()
    results = []
    for book in st.session_state.library:
        if search_by == "Title" and search_term in book['title'].lower():
            results.append(book)
        elif search_by == "Author" and search_term in book['author'].lower():
            results.append(book)
        elif search_by == "Genre" and search_term in book['genre'].lower():
            results.append(book)
    st.session_state.search_results = results

# Calculate library statistics
def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book['read_status'])
    percent_read = (read_books / total_books * 100) if total_books > 0 else 0
    genres = {}
    authors = {}
    decades = {}
    for book in st.session_state.library:
        genres[book['genre']] = genres.get(book['genre'], 0) + 1
        authors[book['author']] = authors.get(book['author'], 0) + 1
        decade = (book['publication_year'] // 10) * 10
        decades[decade] = decades.get(decade, 0) + 1
    genres = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))
    authors = dict(sorted(authors.items(), key=lambda x: x[1], reverse=True))
    decades = dict(sorted(decades.items(), key=lambda x: x[0]))
    return {
        'total_books': total_books,
        'read_books': read_books,
        'percent_read': percent_read,
        'genres': genres,
        'authors': authors,
        'decades': decades
    }

# Function to create visualizations
def create_visualizations(stats):
    if stats['total_books'] > 0:
        # Pie chart for Read vs Unread
        fig_read_status = go.Figure(data=[go.Pie(
            labels=['Read', 'Unread'],
            values=[stats['read_books'], stats['total_books'] - stats['read_books']],
            hole=0.4,
            marker_colors=['#10B981', '#F87171']
        )])
        fig_read_status.update_layout(
            title_text="Read vs Unread Books",
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig_read_status, use_container_width=True)
        
        # Bar chart for Genres
        if stats['genres']:
            genres_df = pd.DataFrame({
                'Genre': list(stats['genres'].keys()),
                'Count': list(stats['genres'].values())
            })
            fig_genres = px.bar(
                genres_df,
                x='Genre',
                y='Count',
                color='Count',
                color_continuous_scale=px.colors.sequential.Blues
            )
            fig_genres.update_layout(
                title_text="Books by Genre",
                xaxis_title="Genre",
                yaxis_title="Number of Books",
                height=400
            )
            st.plotly_chart(fig_genres, use_container_width=True)
        
        # Line chart for Publication Decades
        if stats['decades']:
            decades_df = pd.DataFrame({
                'Decade': [f"{decade}s" for decade in stats['decades'].keys()],
                'Count': list(stats['decades'].values())
            })
            fig_decades = px.line(
                decades_df,
                x='Decade',
                y='Count',
                markers=True,
                line_shape="spline"
            )
            fig_decades.update_layout(
                title_text="Books by Publication Decade",
                xaxis_title="Decade",
                yaxis_title="Number of Books",
                height=400
            )
            st.plotly_chart(fig_decades, use_container_width=True)

# Load library data on app start
load_library()

# Sidebar navigation and lottie animation
st.sidebar.markdown("<h1 style='text-align: center;'>📚 Navigation</h1>", unsafe_allow_html=True)
lottie_book = load_lottieurl("https://assets9.lottiefiles.com/temp/lf20_aKAfIn.json")
if lottie_book:
    with st.sidebar:
        st_lottie(lottie_book, height=200, key="book_animation")

# Navigation options
nav_options = st.sidebar.radio(
    "Choose an option:",
    ["View Library", "Add Book", "Search Books", "Library Statistics"]
)
if nav_options == "View Library":
    st.session_state.current_view = "library"
elif nav_options == "Add Book":
    st.session_state.current_view = "add"
elif nav_options == "Search Books":
    st.session_state.current_view = "search"
elif nav_options == "Library Statistics":
    st.session_state.current_view = "stats"

# Application header
st.markdown("<h1 class='main-header'>📚 Personal Library Manager</h1>", unsafe_allow_html=True)

# ---------------- Add Book / Edit Book View ---------------- #
if st.session_state.current_view == "add":
    # اگر edit_index سیٹ ہو تو Edit mode
    if st.session_state.edit_index is not None:
        st.markdown("<h2 class='sub-header'>✏️ Edit Book Details</h2>", unsafe_allow_html=True)
        book_to_edit = st.session_state.library[st.session_state.edit_index]
    else:
        st.markdown("<h2 class='sub-header'>📝 Add a New Book</h2>", unsafe_allow_html=True)
    
    with st.form(key='add_book_form'):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Book Title", max_chars=100, value=book_to_edit['title'] if st.session_state.edit_index is not None else "")
            author = st.text_input("Author", max_chars=100, value=book_to_edit['author'] if st.session_state.edit_index is not None else "")
            publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, step=1, value=book_to_edit['publication_year'] if st.session_state.edit_index is not None else 2023)
        with col2:
            genre = st.selectbox("Genre", [
                "Fiction", "Non-Fiction", "Science Fiction", "Fantasy", 
                "Mystery", "Romance", "Thriller", "Biography", 
                "History", "Self-Help", "Poetry", "Science", 
                "Philosophy", "Religion", "Art", "Other"
            ], index=(0 if st.session_state.edit_index is None else 0))
            read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True, index=(0 if st.session_state.edit_index is None or book_to_edit['read_status'] else 1))
            read_bool = read_status == "Read"
        
        submit_button = st.form_submit_button(label="Update Book" if st.session_state.edit_index is not None else "Add Book")
        
        if submit_button and title and author:
            if st.session_state.edit_index is not None:
                edit_book(st.session_state.edit_index, title, author, publication_year, genre, read_bool)
                st.session_state.edit_index = None  # Reset edit mode
            else:
                add_book(title, author, publication_year, genre, read_bool)
    
    if st.session_state.book_added:
        st.markdown("<div class='success-message'>Book details saved successfully!</div>", unsafe_allow_html=True)
        st.balloons()
        st.session_state.book_added = False

# ---------------- View Library ---------------- #
elif st.session_state.current_view == "library":
    st.markdown("<h2 class='sub-header'>📖 Your Library</h2>", unsafe_allow_html=True)
    
    # Sorting options
    sort_by = st.selectbox("Sort by:", ["Title", "Publication Year"], index=0)
    sorted_library = st.session_state.library.copy()
    if sort_by == "Title":
        sorted_library.sort(key=lambda x: x['title'])
    elif sort_by == "Publication Year":
        sorted_library.sort(key=lambda x: x['publication_year'], reverse=True)
    
    if not sorted_library:
        st.markdown("<div class='warning-message'>Your library is empty. Add some books to get started!</div>", unsafe_allow_html=True)
    else:
        cols = st.columns(2)
        for i, book in enumerate(sorted_library):
            with cols[i % 2]:
                st.markdown(f"""
                <div class='book-card'>
                    <h3>{book['title']}</h3>
                    <p><strong>Author:</strong> {book['author']}</p>
                    <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                    <p><strong>Genre:</strong> {book['genre']}</p>
                    <p><span class='{"read-badge" if book["read_status"] else "unread-badge"}'>{"Read" if book["read_status"] else "Unread"}</span></p>
                </div>
                """, unsafe_allow_html=True)
                # Action buttons: Remove, Edit, Toggle Read Status
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                with btn_col1:
                    if st.button("Remove", key=f"remove_{i}", use_container_width=True):
                        if remove_book(i):
                            st.experimental_rerun()
                with btn_col2:
                    if st.button("Edit", key=f"edit_{i}", use_container_width=True):
                        # Set current view to add/edit and store index
                        st.session_state.edit_index = i
                        st.session_state.current_view = "add"
                        st.experimental_rerun()
                with btn_col3:
                    new_status = not book['read_status']
                    status_label = "Mark as Read" if not book['read_status'] else "Mark as Unread"
                    if st.button(status_label, key=f"status_{i}", use_container_width=True):
                        book['read_status'] = new_status
                        save_library()
                        st.experimental_rerun()
    
    if st.session_state.book_removed:
        st.markdown("<div class='success-message'>Book removed successfully!</div>", unsafe_allow_html=True)
        st.session_state.book_removed = False

# ---------------- Search Books ---------------- #
elif st.session_state.current_view == "search":
    st.markdown("<h2 class='sub-header'>🔍 Search Books</h2>", unsafe_allow_html=True)
    search_by = st.selectbox("Search by:", ["Title", "Author", "Genre"])
    search_term = st.text_input("Enter search term:")
    col_search = st.columns([2,1])
    with col_search[0]:
        if st.button("Search", use_container_width=True):
            if search_term:
                with st.spinner('Searching...'):
                    time.sleep(0.5)
                    search_books(search_term, search_by)
    with col_search[1]:
        if st.button("Clear Search", use_container_width=True):
            st.session_state.search_results = []
            st.experimental_rerun()
    
    if st.session_state.search_results:
        st.markdown(f"<h3>Found {len(st.session_state.search_results)} results:</h3>", unsafe_allow_html=True)
        for i, book in enumerate(st.session_state.search_results):
            st.markdown(f"""
            <div class='book-card'>
                <h3>{book['title']}</h3>
                <p><strong>Author:</strong> {book['author']}</p>
                <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                <p><strong>Genre:</strong> {book['genre']}</p>
                <p><span class='{"read-badge" if book["read_status"] else "unread-badge"}'>{"Read" if book["read_status"] else "Unread"}</span></p>
            </div>
            """, unsafe_allow_html=True)
    elif search_term:
        st.markdown("<div class='warning-message'>No books found matching your search criteria.</div>", unsafe_allow_html=True)

# ---------------- Library Statistics ---------------- #
elif st.session_state.current_view == "stats":
    st.markdown("<h2 class='sub-header'>📊 Library Statistics</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.markdown("<div class='warning-message'>Your library is empty. Add some books to see statistics!</div>", unsafe_allow_html=True)
    else:
        stats = get_library_stats()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Books", stats['total_books'])
        with col2:
            st.metric("Books Read", stats['read_books'])
        with col3:
            st.metric("Percentage Read", f"{stats['percent_read']:.1f}%")
        create_visualizations(stats)
        if stats['authors']:
            st.markdown("<h3>Top Authors</h3>", unsafe_allow_html=True)
            top_authors = dict(list(stats['authors'].items())[:5])
            for author, count in top_authors.items():
                st.markdown(f"**{author}**: {count} book{'s' if count > 1 else ''}")

# Footer
st.markdown("---")
st.markdown("© 2025 Samra Moinuddin Personal Library Manager | Created with Love and Streamlit", unsafe_allow_html=True)
