from flask import Flask, request, session, redirect, url_for, abort, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_material import Material
from sqlalchemy import func
import datetime

from sqlalchemy import Table
import json

app = Flask(__name__)
Material(app)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] ='super-secret-key'
app.config['USERNAME'] = 'admin'
app.config['PASSWORD'] = '12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookshoppe.db'

db=SQLAlchemy(app)

class Login(db.Model):
    # __tablename__ = 'users'
    email = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(240))

    def __init__(self, email, password,):
        self.email = email
        self.password = password

    def __repr__(self):
        return '<Entry %r %r>' % (self.email, self.password,)

class CustOrders(db.Model):
    # __tablename__ = 'users'
    serial = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), db.ForeignKey('login.email'))
    order_id = db.Column(db.String(100))
    datetime = db.Column(db.DateTime)
    isbn=db.Column(db.String(20))
    quantity=db.Column(db.Integer)
    price=db.Column(db.Integer)

    def __init__(self, serial, email, order_id, datetime, isbn, quantity, price):
        self.email = email
        self.order_id = order_id
        self.datetime = datetime
        self.isbn = isbn
        self.quantity = quantity
        self.price = price

    def __repr__(self):
        return '<Entry %r %r %r %r %r %r>' % (self.email, self.order_id, self.datetime, self.isbn, self.quantity, self.price)

class CurrentCart(db.Model):
    # __tablename__ = 'users'
    serial = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), db.ForeignKey('login.email'))
    book = db.Column(db.String(20))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)

    def __init__(self, email, datetime, book, quantity, price):
        self.email = email
        self.book = book
        self.quantity = quantity
        self.price = price

    def __repr__(self):
        return '<Entry %r %r %r %r>' % (
        self.email, self.book, self.quantity, self.price)

# Create the table
db.create_all()


def authenticate(e, p):
    print(e)
    details= Login.query.filter_by(email=e).filter_by(password=p).all()
    print(details)
    if(len(details)>0):
        return True
    else:
        return False

@app.route('/')
def homepage():
    count=0
    return render_template('homepage.html', size=len(data['items']), data= data, currentBook=count)

@app.route('/logout')
def logout():
    if session['logged_in'] == True:
        session['logged_in'] = False
        return render_template('homepage.html',size=len(data['items']), data= data)
    else:
        return render_template('homepage.html',size=len(data['items']), data= data)

@app.route('/sign_up')
def signup():
    return render_template('sign_up.html')


@app.route('/show_books')
def show_books():
    return render_template('show_books.html', size=len(data['items']), data= data)

@app.route('/book/<int:id>/', methods=['GET','POST'])
def book(id):
    flag=0
    if request.method == 'GET':
        return render_template('book.html', id = id, data=data, flag=flag)
    else:
        quantity=request.form.get('comp_select')
        book = str(data['items'][id]["volumeInfo"]["authors"][0])
        cart=CurrentCart(email=session['log_email'], datetime=datetime.datetime.now(),book=book , quantity=quantity, price=data['items'][id]["saleInfo"]["listPrice"]["amount"])
        detail = CurrentCart.query.filter_by(book=book).all()
        sum=0
        for d in detail:
            sum+=(d.__dict__["quantity"])
        if sum+int(quantity)<3:
            db.session.add(cart)
            db.session.commit()
            flag = 1
        else:
            flag = 2

        return render_template('book.html', id=id, data=data, flag=flag)


@app.route('/login',methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if(authenticate(request.form['username'], request.form['password'])):
            session['logged_in'] = True
            session['log_email'] = request.form['username']
            flash("You are logged in")
            return redirect(url_for('homepage'))
        else:
            error='Invalid credentials'
    return render_template('login.html', error=error)

@app.route('/cart',methods=['GET','POST'])
def cart():
    # book = str(data['items'][id]["volumeInfo"]["authors"][0])
    return render_template('cart.html',size=len(data['items']), data=data, items= CurrentCart.query.all())

@app.route('/clear_cart',methods=['GET'])
def clear_cart():
    total=0
    cart_items= CurrentCart.query.all()
    for cart_item in cart_items:
        db.session.delete(cart_item)
        db.session.commit()
    flash("You just cleared the cart!!")
    return render_template('cart.html',size=len(data['items']), data=data, items= CurrentCart.query.all(),total=total)

with open("json/catalog.json") as data_file:
    data = json.loads(data_file.read())
    print(data['items'][0]['volumeInfo']['title'])

if __name__ == '__main__':
    app.run(debug=True)
