from . import celery, db, app
from .models import Transaction
import datetime
import requests

@celery.task(name='check_pending_transactions')
def check_pending_transactions():
    with app.app_context():
        now = datetime.datetime.now()
        threshold = now - datetime.timedelta(minutes=0.1)
        pending_transactions = Transaction.query.filter(Transaction.status == 'Ожидание', Transaction.created_at < threshold).all()

        for transaction in pending_transactions:
            transaction.status = 'Истекла'
            db.session.commit()

            requests.post(transaction.user.webhook_url, json={'transaction_id': transaction.id, 'status': transaction.status})

        print('Задача выполнена')
