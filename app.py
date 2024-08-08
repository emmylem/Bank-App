from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'vidhis'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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
    # Add initial data
    pass

def update_entry(sender_name, receiver_name, bank_id, amount):
    # Update entries
    pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transferlist', methods=['GET', 'POST'])
def transferlist():
    order_list = User_Transfer_List.query.order_by(User_Transfer_List.id).all()
    return render_template('transferlist.html', order_list=order_list)

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if request.method == 'POST':
        sender_name = request.form['sender_name']
        receiver_name = request.form['receiver_name']
        account_no = int(request.form['account_no'])
        amount = float(request.form['amount'])

        sender = User_Transfer_List.query.filter_by(username=sender_name).first()
        receiver = User_Transfer_List.query.filter_by(username=receiver_name).first()

        if receiver.bank_id == account_no:
            sender.balance -= amount
            receiver.balance += amount

            db.session.add_all([sender, receiver])
            db.session.commit()

            flash(f"Transaction Successful! Your Account Number {sender.bank_id} has been credited by Rs {amount} to {receiver_name}.")
            return redirect(request.url)
        else:
            flash('Account Number entered is incorrect. Please try again!')
            return redirect(request.url)

    return render_template('transfer.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create the database tables
        # create_one_time_entry()  # Uncomment to add initial data
    app.run(debug=True)

