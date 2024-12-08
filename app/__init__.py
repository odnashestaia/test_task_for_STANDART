from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_migrate import Migrate
from celery import Celery
from flasgger import Swagger

from celery.schedules import crontab
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['result_backend'] = 'redis://localhost:6379/0'
app.config['broker_connection_retry_on_startup'] = True
app.config['beat_max_loop_interval'] = 60


db = SQLAlchemy(app)
migrate = Migrate(app, db)
swagger = Swagger(app)

admin = Admin(app, name='Admin Panel', template_mode='bootstrap4')

# Инициализация Celery
def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['result_backend'],
    )
    celery.conf.update(app.config)
    return celery

celery = make_celery(app)

celery.conf.beat_schedule = {
    'print-message-every-minute': {
        'task': 'check_pending_transactions',
        'schedule': crontab(minute='*'),
    },
}

celery.conf.timezone = 'Europe/Moscow'


from .task import check_pending_transactions 

# Модели
from .models import User, Transaction

# Flask Admin Views
from .views import UserAdmin, TransactionAdmin, DashboardView
admin.add_view(DashboardView(name='Dashboard', endpoint='dashboard'))
admin.add_view(UserAdmin(User, db.session))
admin.add_view(TransactionAdmin(Transaction, db.session))

if __name__ == '__main__':
    app.run(debug=True)
