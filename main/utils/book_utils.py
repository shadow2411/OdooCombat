import requests
from datetime import datetime
from main.models import Book

GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

def fetch_books_from_api(query, max_results=1):
    params = {
        "q": query,
        "maxResults": max_results,
    }
    response = requests.get(GOOGLE_BOOKS_API_URL, params=params)
    print(response.url)
    return response.json()

def save_book_to_db(book_data):
    volume_info = book_data.get('volumeInfo', {})
    
    # Extract ISBN
    isbn = ""
    for identifier in volume_info.get('industryIdentifiers', []):
        if identifier['type'] in ['ISBN_13', 'ISBN_10']:
            isbn = identifier['identifier']
            break
    
    # Check if the book already exists
    existing_book = Book.objects.filter(isbn=isbn).first()
    if existing_book:
        return existing_book

    # Create a new book
    book = Book(
        title=volume_info.get('title', ''),
        authors=", ".join(volume_info.get('authors', [])),
        isbn=isbn,
        published_date=parse_date(volume_info.get('publishedDate')),
        description=volume_info.get('description', ''),
        page_count=volume_info.get('pageCount'),
        categories=", ".join(volume_info.get('categories', [])),
        thumbnail_url=volume_info.get('imageLinks', {}).get('thumbnail', ''),
        language=volume_info.get('language', '')
    )
    book.save()
    return book

def parse_date(date_string):
    if not date_string:
        return None
    
    formats = ['%Y-%m-%d', '%Y-%m', '%Y']
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt).date()
        except ValueError:
            pass
    return None

def populate_books_from_api(query, max_results=1):
    api_data = fetch_books_from_api(query, max_results)
    saved_books = []
    
    for item in api_data.get('items', []):
        book = save_book_to_db(item)
        saved_books.append(book)
    
    return saved_books