import requests
import os, json


from flask import Flask, session, render_template, redirect, url_for, request, jsonify

from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import timedelta


app = Flask(__name__)
app.config["SECRET_KEY"]="secretkey"

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


app.static_folder = 'static'


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")

    db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                    {"username": username, "password": password})
    db.commit()

    return render_template("register.html")

@app.route("/login", methods=["POST", "GET"])
def login():
        if request.method == "POST":
            p_username = request.form.get("username")
            p_password = request.form.get("password")

            checkuser = db.execute("SELECT username FROM users WHERE username=:username;", {"username": p_username}).fetchone()

            if checkuser is not None:

                checkpass = db.execute("SELECT username FROM users WHERE password=:password AND username=:username;", {"password": p_password, "username": p_username}).fetchone()

                if checkpass is not None:

                    #return render_template("success.html", printthis = "You are logged in", name = p_username)
                    session["USERNAME"]= p_username
                    return render_template("search.html")


                else:
                    return render_template("error.html", printthis = "User or pass not correct")

            else:
                return render_template("error.html", printthis="This user does not exist")
        else:
                return render_template("register.html")

db.commit()


@app.route("/logout")
def logout():
    session.pop("USERNAME", None)
    return redirect(url_for("login"))

global p_search

@app.route("/search", methods=["POST", "GET"])
def search():

    if request.method=="POST":
        if not session.get("USERNAME") is None:
                username = session.get("USERNAME")

                p_search  = request.form.get("search")

                search1 = "%" + p_search + "%"


                books = db.execute("SELECT * FROM books WHERE lower(title) LIKE :title", {"title": search1}).fetchall()
                if len(books):
                    return render_template("search.html", books=books, username=username)
                else:
                    books = db.execute("SELECT * FROM books WHERE lower(author) LIKE :author", {"author": search1}).fetchall()

                    if len(books):
                        return render_template("search.html", books=books)
                    else:
                        books = db.execute("SELECT * FROM books WHERE lower(isbn) LIKE :isbn", {"isbn":search1}).fetchall()
                        #search3 = db.execute("SELECT title FROM books WHERE isbn=:isbn", {"isbn": p_search}).fetchall()
                        if len(books):
                            return render_template("search.html", books=books)
                        else:
                            books = db.execute("SELECT * FROM books WHERE lower(year) LIKE :year", {"year": search1}).fetchall()
                            if len(books):
                                return render_template("search.html", books=books)
                            else:
                                return render_template("error.html", printthis = "No such book.")

                db.commit()
        else:
            return render_template("error.html", printthis="Not signed in.")
    else:
        return render_template("search.html")



@app.route("/displayinfo/<book_isbn>", methods=["POST", "GET"])

def displayinfo(book_isbn):

    if request.method=="POST":
        if not session.get("USERNAME") is None:

            #actual_isbn = db.execute("SELECT isbn FROM books WHERE title=:title", {"title":book_isbn})
            #actual_isbn = actual_isbn[48:]


            username = session.get("USERNAME")

            review = request.form.get("review")
            rating = request.form.get("rating")

            user_id = db.execute("SELECT user_id FROM users WHERE username=:username", {"username": username}).fetchone()
            #book_id = db.execute("SELECT book_id FROM books WHERE isbn=:isbn", {"isbn": book_isbn}).fetchone()


            #db.execute("INSERT INTO reviews (comment, user_id, rating) VALUES (:comment, :user_id, :book_id, :rating)",{"comment": review, "user_id": user_id, "book_id":"2", "rating":rating})
             db.execute(
            "INSERT INTO reviews (review_id, book_id, user_id, comment, rating) VALUES (NULL, :book_id, :user_id, :comment, :rating)",
            {"book_id": book_id, "user_id": user_id, "review": review, "rating": rating})
            return redirect(url_for("login"))

            #return redirect(url_for("/displayinfo/"+ actual_isbn))
            db.commit()



        else:
            return render_template("error.html", printthis="Not signed in.")

    else:
        if not session.get("USERNAME") is None:



            booktitle = db.execute("SELECT title FROM BOOKS WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
            bookauthor = db.execute("SELECT author FROM BOOKS WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
            bookyear = db.execute("SELECT year FROM BOOKS WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
            bookisbn = db.execute("SELECT isbn FROM BOOKS WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()

            res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "KqqGbJlg2XMOyLiYRAnhvQ", "isbns": bookisbn})

            data = res.json()
            a = data["books"][0]
            #response = response['books'][0]['average_rating']['ratings_count']

            return render_template("displayinfo.html", printtitle=booktitle, printauthor=bookauthor,printyear=bookyear, printisbn=bookisbn, book=booktitle, printapi=a["average_rating"], username=session.get("USERNAME"), test=book_isbn)

            db.commit()
        else:
            return render_template("error.html", printthis="Not signed in.")











@app.route("/api/string:<isbn>", methods=["GET"])
def json(isbn):

    book = db.execute("SELECT title FROM books WHERE isbn=:isbn", {"isbn": isbn}).fetchone()

    reviewcount = "count"
    averagescore = "score"


    return jsonify({
            "title": book.title,
            "author": book.author,
            "author": book.year,
            "isbn": isbn,
            "review_count": reviewcount,
            "average_score": averagescore
    })
