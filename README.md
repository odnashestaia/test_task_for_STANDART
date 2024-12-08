# Тестовое задание для Стандарт

## Запуск проекта

1. **Запуск Redis через Docker**

   ```bash
   docker run -d -p 6379:6379 redis
   ```

2. **Установка зависимостей**

   ```bash
   poetry install --no-root
   ```

3. **Запуск сервера**

   ```bash
   flask run
   ```

4. **Запуск Celery**

   ```bash
   celery -A app.celery_worker.celery worker --loglevel=info
   celery -A app.celery_worker.celery beat --loglevel=info
   ```