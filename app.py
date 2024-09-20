from functools import wraps
from flask import Flask, render_template, request, redirect, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'vidhis'  # Ensure this is set to a secure random key in production

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://bankapp_user:CcDlVWTXWrRS7r9Pe0ybiP28D6LuGdTu@dpg-crmiru5umphs739f5st0-a/bankapp')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model for User
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

# Database model for User_Transfer_List
class User_Transfer_List(db.Model):
    __tablename__ = 'User_Transfer_List'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    bank_id = db.Column(db.Integer)
    balance = db.Column(db.Float)

    def __init__(self, username, bank_id, balance):
        self.username = username
        self.bank_id = bank_id
        self.balance = balance

    def __repr__(self):
        return f"{self.id} | {self.username} | {self.bank_id} | {self.balance}"

def create_one_time_entry():
    # Check if the table is empty before adding the entries
    if User_Transfer_List.query.count() == 0:
        users = [
            {"username": "reey", "bank_id": 12345, "balance": 1000.00},
            {"username": "alex", "bank_id": 67890, "balance": 1500.00},
            {"username": "jane", "bank_id": 54321, "balance": 2000.00},
            {"username": "john", "bank_id": 98765, "balance": 2500.00},
            {"username": "ben", "bank_id": 11111, "balance": 3000.00}
        ]
        
        for user in users:
            if not User_Transfer_List.query.filter_by(username=user['username']).first():
                new_user = User_Transfer_List(username=user['username'], bank_id=user['bank_id'], balance=user['balance'])
                db.session.add(new_user)
        
        db.session.commit()

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to log in to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Route for the homepage
@app.route('/')
@login_required
def index():
    username = session.get('username')
    return render_template('index.html', username=username)

# Route to display the transfer list
@app.route('/transferlist', methods=['GET'])
@login_required
def transferlist():
    # Query the User_Transfer_List table
    order_list = User_Transfer_List.query.order_by(User_Transfer_List.id).all()

    # If the table is empty, insert sample records
    if not order_list:
        sample_transfers = [
            {"username": "reey", "bank_id": 12345, "balance": 1000.00},
            {"username": "alex", "bank_id": 67890, "balance": 1500.00},
            {"username": "jane", "bank_id": 54321, "balance": 2000.00},
            {"username": "john", "bank_id": 98765, "balance": 2500.00},
            {"username": "ben", "bank_id": 11111, "balance": 3000.00},
        ]
        
        for transfer in sample_transfers:
            new_transfer = User_Transfer_List(
                username=transfer["username"],
                bank_id=transfer["bank_id"],
                balance=transfer["balance"]
            )
            db.session.add(new_transfer)
        
        db.session.commit()
        # Query again to include the newly added sample records
        order_list = User_Transfer_List.query.order_by(User_Transfer_List.id).all()

    # Log the results for debugging
    app.logger.info(f"Order List: {order_list}")
    
    return render_template('transferlist.html', order_list=order_list)

@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    if request.method == 'POST':
        sender_name = request.form['sender_name']
        receiver_name = request.form['receiver_name']
        account_no = int(request.form['account_no'])
        amount = float(request.form['amount'])

        # Find the sender and receiver in the database
        sender = User_Transfer_List.query.filter_by(username=sender_name).first()
        receiver = User_Transfer_List.query.filter_by(username=receiver_name).first()

        # Check if the sender exists
        if sender is None:
            flash(f"Sender '{sender_name}' not found. Please check the name and try again.")
            return redirect(request.url)

        # Check if the receiver exists
        if receiver is None:
            flash(f"Receiver '{receiver_name}' not found. Please check the name and try again.")
            return redirect(request.url)

        # Check if the sender's bank_id matches the provided account_no
        if sender.bank_id == account_no:
            sender.balance -= amount
            receiver.balance += amount

            db.session.add_all([sender, receiver])
            db.session.commit()

            flash(f"Transaction Successful! Your Account Number {sender.bank_id} has been debited by Naira {amount} to {receiver_name}.")
            return redirect(request.url)
        else:
            flash('Account Number entered is incorrect. Please try again!')
            return redirect(request.url)

    return render_template('transfer.html')

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.')
            return redirect('/register')

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.')
        return redirect('/login')

    return render_template('register.html')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id  # Store user ID in session
            session['username'] = user.username  # Store username in session
            flash('Login successful!')
            return redirect('/')
        else:
            flash('Invalid username or password. Please try again.')
            return redirect('/login')

    return render_template('login.html')

# Route for user logout
@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)  # Remove user ID from session
    session.pop('username', None)  # Remove username from session
    flash('You have been logged out.')
    return redirect('/login')

# Route for account overview
@app.route('/account_overview')
@login_required
def account_overview():
    username = session.get('username')
    user_account = User_Transfer_List.query.filter_by(username=username).first()
    return render_template('account_overview.html', user_account=user_account)

# Route for managing credit cards
@app.route('/credit_card', methods=['GET', 'POST'])
@login_required
def credit_card():
    # Add logic here to handle credit card information
    return render_template('credit_card.html')

# Route for loan management
@app.route('/loan_management', methods=['GET', 'POST'])
@login_required
def loan_management():
    # Add logic here to handle loan management functionality
    return render_template('loan_management.html')

@app.route('/add_sample_transfer')
def add_sample_transfer():
    new_transfer = User_Transfer_List(username="Test User", bank_id=123456789, balance=100.0)
    db.session.add(new_transfer)
    db.session.commit()
    
    return "Sample transfer added"

@app.route('/debug/transferlist')
def debug_transferlist():
    # Fetch all transfer entries
    order_list = User_Transfer_List.query.all()
    
    # Return the data for debugging purposes
    return str(order_list) if order_list else "No transfer records found"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create the database tables
        create_one_time_entry()  # Add initial data if the table is empty
    app.run(debug=True)
