import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(("postgres://aalgitfmwsynso:cebf73e97c971d1e3d95319dd2380e94b05804f6feaeb4bcfdfe57c060c85916@ec2-3-231-16-122.compute-1.amazonaws.com:5432/dfao8hvjjbai15")) #if doesnt work replace with actual url
db = scoped_session(sessionmaker(bind=engine))

def main():
    db.execute("DROP TABLE IF EXISTS users")
    db.execute("DROP TABLE IF EXISTS books")
    db.execute("CREATE TABLE users (user_id SERIAL PRIMARY KEY, username VARCHAR NOT NULL, password VARCHAR NOT NULL)")
    db.execute("CREATE TABLE books (book_id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year VARCHAR NOT NULL)")
    db.execute("CREATE TABLE reviews (review_id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users, book_id INTEGER REFERENCES books, comment VARCHAR NOT NULL, rating VARCHAR NOT NULL)")
    b = open("books.csv")
    reader = csv.reader(b)
    for number, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                {"isbn":number, "title":title, "author": author, "year": year})
        print(f"Added {title} by {author} published in {year}, ISBN {number}.")
    db.commit()

if __name__ == "__main__":
    main()
