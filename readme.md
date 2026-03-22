# library API
basic library system
uses FastAPI
thumbs up emo

## what it does
- lists all books
- shows availability
- borrow and return books
- keeps simple borrow records
- lets you add, update, delete books
- filter, search, sort, and paginate
- queue system for unavailable books

## how to run
```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```
open: http://127.0.0.1:8000/docs

## how to run
data is in-memory. It resets on restart.
no auth.
no database.

## endpoints 
`/books` - list
`/books/{id}` - get one
`/borrow` - borrow
`/return/{id}` - return
`/books/filter` - filter
`/books/search` - search
`/books/sort` - sort
`/books/page` - paginate
`/queue` - queue
