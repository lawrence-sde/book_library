Question:

Create a REST API using FastAPI to manage a Books database table with the following features:

Requirements:

1. Database Schema:

Create a books table with the following fields:

id (primary key, integer, auto-increment).

title (string).

author (string).

published_date (date).


2. CRUD Operations: Implement the following endpoints:

Create: Add a new book.

Read: Retrieve the details of all books or a specific book by its ID.

Update: Update the details of a book by its ID.

Delete: Remove a book by its ID.



3. Authentication:

Implement JWT-based authentication using FastAPI's OAuth2PasswordBearer.

Only authenticated users should be able to access the CRUD endpoints.



4. Error Handling: Return appropriate HTTP status codes for errors such as "Book not found," "Unauthorized access," etc.


5. Database: Use SQLAlchemy as the ORM and postgres / sql server  as the database.