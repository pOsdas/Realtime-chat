# Realtime chat
## Запуск и подготовка
### Django server
```shell
uvicorn chat_project.asgi:application --host 127.0.0.1 --port 8005 --reload
```
### Проверить базу данных
```shell
poetry run python ensure_db.py
```
## Отправка сообщений
- Подключитесь к чату используя `access_token`
```shell
wscat -c "ws://127.0.0.1:8005/ws/chat/general/?token=<ACCESS>"
```
- Отправьте сообщение
```shell
{"message": "hello world!"}
```