from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'vidhis'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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
    # Adding multiple users to the database for testing
    user1 = User_Transfer_List(username="reey", bank_id=12345, balance=1000.00)
    user2 = User_Transfer_List(username="alex", bank_id=67890, balance=1500.00)
    user3 = User_Transfer_List(username="jane", bank_id=54321, balance=2000.00)
    user4 = User_Transfer_List(username="john", bank_id=98765, balance=2500.00)
    user5 = User_Transfer_List(username="ben", bank_id=11111, balance=3000.00)
    
    db.session.add_all([user1, user2, user3, user4, user5])
    db.session.commit()

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route to display the transfer list
@app.route('/transferlist', methods=['GET', 'POST'])
def transferlist():
    order_list = User_Transfer_List.query.order_by(User_Transfer_List.id).all()
    return render_template('transferlist.html', order_list=order_list)

# Route to handle money transfers
@app.route('/transfer', methods=['GET', 'POST'])
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

        # Check if the receiver's bank_id matches the provided account_no
        if receiver.bank_id == account_no:
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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create the database tables
        create_one_time_entry()  # Add initial data
    app.run(debug=True)

