from flask import jsonify, request
from . import app, db
from .models import User, Transaction
from flasgger import swag_from
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
import datetime


class UserAdmin(ModelView):
    column_list = ('id', 'balance', 'commission_rate', 'webhook_url')

class TransactionAdmin(ModelView):
    column_list = ('id', 'amount', 'commission', 'status', 'created_at', 'user_id')

class DashboardView(BaseView):
    @expose('/')
    def index(self):
        user_count = User.query.count()
        transaction_count = Transaction.query.count()
        today = datetime.datetime.utcnow().date()
        today_transactions = Transaction.query.filter(db.func.date(Transaction.created_at) == today).all()
        total_sum = sum(t.amount for t in today_transactions)
        latest_transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(10).all()
        return self.render('dashboard.html', 
                           user_count=user_count, 
                           transaction_count=transaction_count, 
                           total_sum=total_sum, 
                           latest_transactions=latest_transactions)

@app.route('/create_transaction', methods=['POST'])
@swag_from('swagger/create_transaction.yml')
def create_transaction():
    data = request.json
    user_id = data.get('user_id')
    amount = data.get('amount')

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    commission = amount * user.commission_rate
    transaction = Transaction(amount=amount, commission=commission, user_id=user_id)
    db.session.add(transaction)
    db.session.commit()

    return jsonify({'transaction_id': transaction.id, 'commission': commission}), 201




@app.route('/cancel_transaction', methods=['POST'])
@swag_from('swagger/cancel_transaction.yml')
def cancel_transaction():
    data = request.json
    transaction_id = data.get('transaction_id')

    transaction = Transaction.query.get(transaction_id)
    if not transaction or transaction.status != 'Ожидание':
        return jsonify({'error': 'Invalid transaction or status'}), 400

    transaction.status = 'Отменена'
    db.session.commit()
    return jsonify({'message': 'Transaction cancelled'}), 200

@app.route('/check_transaction', methods=['GET'])
@swag_from('swagger/check_transaction.yml')
def check_transaction():
    transaction_id = request.args.get('transaction_id')
    transaction = Transaction.query.get(transaction_id)

    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404

    return jsonify({'transaction_id': transaction.id, 'status': transaction.status}), 200