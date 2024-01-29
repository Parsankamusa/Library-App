from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import flash
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.secret_key = 'c42f59c7d3b85ad171b7ec6fc4cc99d6'
db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('base.html')

books = []
members = []
transactions = []

# Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, nullable=False)

# Creating  the database tables
with app.app_context():
    db.create_all()

# ...

# CRUD operations for Books
@app.route('/books', methods=['GET', 'POST'])
def books_page():
    if request.method == 'POST':
        # Handle form submission for adding a book
        title = request.form.get('title')
        author = request.form.get('author')
        stock = request.form.get('stock')

        new_book = Book(title=title, author=author, stock=stock)
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for('books_page'))

    books = Book.query.all()
    return render_template('books.html', books=books)
# ...

# Member model
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(100), nullable=False)
    Phone_number = db.Column(db.Integer)
    outstanding_debt = db.Column(db.Float, default=0.0)

# # Create the database tables
with app.app_context():
    db.create_all()



# CRUD operations for Members
@app.route('/members', methods=['GET', 'POST'])
def members_page():
    if request.method == 'POST':
        # Handle form submission for adding a member
        name = request.form.get('name')
        Email = request.form.get('Email')
        Phone_number= request.form.get('Phone number')

        new_member = Member(name=name, Email=Email, Phone_number= Phone_number)
        db.session.add(new_member)
        db.session.commit()

        return redirect(url_for('members_page'))

    members = Member.query.all()
    return render_template('members.html', members=members)
# ...

# Transaction model
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)
    rent_fee = db.Column(db.Float, default=0.0)

    # Define relationships
    book = db.relationship('Book', backref='transactions')
    member = db.relationship('Member', backref='transactions')

# Create the database tables
with app.app_context():
    db.create_all()

# ...

# CRUD operations for Transactions
@app.route('/transactions', methods=['GET', 'POST'])
def transactions_page():
    if request.method == 'POST':
        # Handle form submission for adding a transaction
        book_id = request.form.get('book_id')
        member_id = request.form.get('member_id')
        return_date = request.form.get('return_date')
        
        # Add logic to calculate rent_fee and update outstanding_debt for the member
        
        new_transaction = Transaction(book_id=book_id, member_id=member_id, return_date=return_date)
        db.session.add(new_transaction)
        db.session.commit()

        return redirect(url_for('transactions_page'))

    transactions = Transaction.query.all()
    return render_template('transactions.html', transactions=transactions, books=books, members=members)

# Issue a book to a member
@app.route('/issue_book', methods=['GET', 'POST'])
def issue_book():
    if request.method == 'POST':
        # Handle form submission for issuing a book
        book_id = request.form.get('book_id')
        member_id = request.form.get('member_id')

        # Check if the book is available (in stock)
        book = Book.query.get(book_id)
        if book and book.stock > 0:
            # Decrease the stock of the book
            book.stock -= 1

            # Create a new transaction
            issue_date = datetime.utcnow()
            new_transaction = Transaction(book_id=book_id, member_id=member_id, issue_date=issue_date)
            db.session.add(new_transaction)
            db.session.commit()

            return redirect(url_for('transactions_page'))

    books = Book.query.all()
    members = Member.query.all()
    return render_template('issue_book.html', books=books, members=members)


# Issue a book return from a member
# ...

# Return a book from a member
@app.route('/return_book', methods=['GET', 'POST'])
def return_book():
    if request.method == 'POST':
        # Handle form submission for returning a book
        transaction_id = request.form.get('transaction_id')

        # Retrieve the transaction from the database
        transaction = Transaction.query.get(transaction_id)

        if transaction and not transaction.return_date:
            # Update return date and calculate rent fee
            transaction.return_date = datetime.utcnow()

            # Calculate rent fee based on your logic
            # For example, you can calculate the difference in days and charge a fee per day
            # rent_fee_per_day = 5
            # days_difference = (transaction.return_date - transaction.issue_date).days
            # transaction.rent_fee = rent_fee_per_day * days_difference

            db.session.commit()

            # Increase the stock of the returned book
            returned_book = Book.query.get(transaction.book_id)
            returned_book.stock += 1
            db.session.commit()

            return redirect(url_for('transactions_page'))

    transactions = Transaction.query.filter(Transaction.return_date.is_(None)).all()
    return render_template('return_book.html', transactions=transactions)

if __name__ == '__main__':
    app.run(debug=True)