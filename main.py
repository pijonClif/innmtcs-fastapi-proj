import math
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()

# Q1
@app.get("/")
def read_root():
    return {'message': 'Welcome to City Public Library'}

books = [
    {"id": 1, "title": "Tale of Aruko", "author": "Anharo", "genre": "Fiction", "is_available": True},
    {"id": 2, "title": "A Brief History of Time", "author": "Stephen Hawking", "genre": "Science", "is_available": False},
    {"id": 3, "title": "Sapiens", "author": "Yuval Noah Harari", "genre": "History", "is_available": True},
    {"id": 4, "title": "Clean Code", "author": "Robert C. Martin", "genre": "Tech", "is_available": True},
    {"id": 5, "title": "Something within my heart", "author": "Anish Sharma", "genre": "Fiction", "is_available": False},
    {"id": 6, "title": "The Selfish Gene", "author": "Richard Dawkins", "genre": "Science", "is_available": True},
]

# Q2
@app.get("/books")
def get_books():
    return {
        "books": books,
        "total_books": len(books),
        "available_books": len([book for book in books if book["is_available"]])
    }


borrow_records = []
record_counter = 1
def find_book(book_id):
    for book in books:
        if book["id"] == book_id:
            return book
    return None

def is_book_borrowed(book_id):
    for record in borrow_records:
        if record["book_id"] == book_id and record["return_date"] is None:
            return True
    return False

def calculate_due_date(days, member_type="regular"):
    if member_type == "premium":
        days= min(days,60)
    else:
        days= min(days,30)
    return f"Return by {days} days from today"

def filter_books(genre=None, author=None, is_available=None):
    filtered_books = []
    for book in books:
        if genre is not None and book["genre"].lower() != genre.lower():
            continue
        if author is not None and author.lower() not in book["author"].lower():
            continue
        if is_available is not None and book["is_available"] != is_available:
            continue
        filtered_books.append(book)

    return filtered_books

def get_books_by_genre():
    book_by_genre = {}
    for book in books:
        genre = book["genre"]
        book_by_genre[genre] = book_by_genre.get(genre, 0) + 1

    return book_by_genre

# Q4
@app.get("/books/{book_id}/borrow")
def get_borrow(book_id: int):
    book = find_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not book["is_available"]:
        raise HTTPException(status_code=400, detail="Book already borrowed")
    return {
        "message": "Book is available for borrowing",
        "book": book
    }

# Q5
@app.get("/books/summary")
def get_books_summary():
    total_books = len(books)
    available_books = len([book for book in books if book["is_available"]])
    book_by_genre = get_books_by_genre()
    return {
        "total_books": total_books,
        "available_books": available_books,
        "borrowed_books": total_books - available_books,
        "books_by_genre": book_by_genre
    }

class BorrowRequest(BaseModel):
    member_name: str = Field(..., min_length=2)
    member_id: str = Field(..., min_length=4)
    book_id: int = Field(..., gt=0)
    borrow_days: int = Field(..., gt=0, le=60)
    member_type: str = "regular"

# Q8
@app.post("/borrow")
def borrow_book(request: BorrowRequest):
    book = find_book(request.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not book["is_available"]:
        raise HTTPException(status_code=400, detail="Book already borrowed")
    book["is_available"] = False
    due_date = calculate_due_date(request.borrow_days, request.member_type)
    record = {
        "record_id": len(borrow_records) + 1,
        "member_name": request.member_name,
        "member_id": request.member_id,
        "book_id": request.book_id,
        "member_type": request.member_type,
        "borrow_days": request.borrow_days,
        "due_date": due_date
    }
    borrow_records.append(record)
    return {
        "message": "Book borrowed successfully",
        "record": record
    }

# 10
@app.get("/books/filter")
def filter(
    genre: Optional[str] = None,
    author: Optional[str] = None,
    is_available: Optional[bool] = None
):
    result=filter_books(genre, author, is_available)
    return {
        "count": len(result),
        "books": result
    }
class NewBook(BaseModel):
    title: str = Field(..., min_length=2)
    author: str = Field(..., min_length=2)
    genre: str = Field(..., min_length=2)
    is_available: bool = True

# Q11
@app.post("/books", status_code=status.HTTP_201_CREATED)
def add_book(new_book: NewBook):
    for book in books:
        if book["title"].lower() == new_book.title.lower():
            raise HTTPException(
                status_code=400,
                detail="Book with this title already exists"
            )
    new_id = len(books) + 1
    book_dict = {
        "id": new_id,
        "title": new_book.title,
        "author": new_book.author,
        "genre": new_book.genre,
        "is_available": new_book.is_available
    }
    books.append(book_dict)
    
    return book_dict

# Q12
@app.put("/books/{book_id}")
def update_book(
    book_id: int,
    genre: Optional[str] = None,
    is_available: Optional[bool] = None
):
    book = find_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if genre is not None:
        book["genre"] = genre
    if is_available is not None:
        book["is_available"] = is_available
    
    return book

# Q13
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    for index, book in enumerate(books):
        if book["id"] == book_id:
            deleted_title = book["title"]
            books.pop(index)
            return {
                "message": f"Book '{deleted_title}' deleted successfully"
            }
    raise HTTPException(status_code=404, detail="Book not found")

# Q14
queue = []
@app.post("/queue/add")
def add_to_queue(member_name: str, book_id: int):
    book = find_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book["is_available"]:
        raise HTTPException(
            status_code=400,
            detail="Book is available, no need to join queue"
        )
    entry = {
        "queue_id": len(queue) + 1,
        "member_name": member_name,
        "book_id": book_id
    }
    queue.append(entry)
    return {
        "message": "Added to queue",
        "entry": entry
    }

@app.get("/queue")
def get_queue():
    return {
        "count": len(queue),
        "queue": queue
    }

# Q15 
@app.post("/return/{book_id}")
def return_book(book_id: int):
    book = find_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book["is_available"] = True
    for index, entry in enumerate(queue):
        if entry["book_id"] == book_id:
            member_name = entry["member_name"]
            queue.pop(index)
            book["is_available"] = False
            record = {
                "record_id": len(borrow_records) + 1,
                "member_name": member_name,
                "book_id": book_id,
                "borrow_days": 7,  
                "due_date": calculate_due_date(7)
            }
            borrow_records.append(record)
            return {
                "message": "Book returned and reassigned",
                "assigned_to": member_name,
                "record": record
            }
    return {
        "message": "Book returned and available"
    }

# Q16
def search_books_logic(keyword):
    keyword = keyword.lower()
    results = []
    for book in books:
        if (
            keyword in book["title"].lower()
            or keyword in book["author"].lower()
        ):
            results.append(book)
    return results

@app.get("/books/search")
def search_books(keyword: str):
    if not keyword.strip():
        raise HTTPException(status_code=400, detail="Keyword cannot be empty")
    results = search_books_logic(keyword)
    return {
        "total_found": len(results),
        "results": results
    }

# Q17

@app.get("/books/sort")
def sort_books(
    sort_by: str = "title",
    order: str = "asc"
):
    valid_sort_fields = ["title", "author", "genre"]
    valid_orders = ["asc", "desc"]
    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by. Allowed: {valid_sort_fields}"
        )
    if order not in valid_orders:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid order. Allowed: {valid_orders}"
        )
    reverse = True if order == "desc" else False
    sorted_books = sorted(
        books,
        key=lambda b: b[sort_by].lower(),
        reverse=reverse
    )
    return {
        "sort_by": sort_by,
        "order": order,
        "count": len(sorted_books),
        "books": sorted_books
    }

# Q18
@app.get("/books/page")
def get_books_page(page: int = 1, limit: int = 3):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Page and limit must be >= 1")
    total = len(books)
    total_pages = math.ceil(total / limit)
    if page > total_pages and total > 0:
        raise HTTPException(status_code=404, detail="Page not found")
    start = (page - 1) * limit
    end = start + limit
    paginated_books = books[start:end]
    return {
        "total": total,
        "total_pages": total_pages,
        "current_page": page,
        "limit": limit,
        "books": paginated_books
    }

# Q19
@app.get("/borrow-records/search")
def search_borrow_records(member_name: str):
    if not member_name.strip():
        raise HTTPException(status_code=400, detail="member_name cannot be empty")
    keyword = member_name.lower()
    results = [
        record for record in borrow_records
        if keyword in record["member_name"].lower()
    ]
    return {
        "total_found": len(results),
        "records": results
    }

@app.get("/borrow-records/page")
def paginate_borrow_records(page: int = 1, limit: int = 3):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Page and limit must be >= 1")
    total = len(borrow_records)
    total_pages = math.ceil(total / limit)
    if page > total_pages and total > 0:
        raise HTTPException(status_code=404, detail="Page not found")
    start =(page-1)*limit
    end =start+limit
    paginated =borrow_records[start:end]
    return {
        "total": total,
        "total_pages": total_pages,
        "current_page": page,
        "limit": limit,
        "records": paginated
    }

# Q20
@app.get("/books/browse")
def browse_books(
    keyword: Optional[str] = None,
    sort_by: str = "title",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    valid_sort_fields = ["title", "author", "genre"]
    valid_orders = ["asc", "desc"]

    sort_by = sort_by.lower()
    order = order.lower()
    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by. Allowed: {valid_sort_fields}"
        )
    if order not in valid_orders:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid order. Allowed: {valid_orders}"
        )
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Page and limit must be >= 1")
    filtered = books
    if keyword:
        keyword_lower = keyword.lower()
        filtered = [
            b for b in books
            if keyword_lower in b["title"].lower()
            or keyword_lower in b["author"].lower()
        ]
    reverse = True if order == "desc" else False
    sorted_books = sorted(
        filtered,
        key=lambda b: b[sort_by].lower(),
        reverse=reverse
    )
    total = len(sorted_books)
    total_pages = math.ceil(total / limit)
    if page > total_pages and total > 0:
        raise HTTPException(status_code=404, detail="Page not found")
    start = (page-1)*limit
    end = start + limit
    paginated = sorted_books[start:end]
    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "total": total,
        "total_pages": total_pages,
        "current_page": page,
        "limit": limit,
        "results": paginated
    }

# Q3
@app.get("/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    return {"error": "Book not found"}



