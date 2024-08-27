# Best Realty Stats Bot

Этот проект состоит из двух сервисов:

1. **api_service**: Обрабатывает вебхуки с данными и сохраняет их в базу данных.
2. **bot_service**: Форматирует данные и выводит их в удобном виде в Telegram чат.

## Запуск проекта

### 1. Настройка конфигурации
Скопируйте пример конфигурационного файла и настройте его:
```bash
cp common/config.py.example common/config.py
```

**Важно**: Убедитесь, что в `config.py` указан правильный токен Telegram бота.

### 2. Создание виртуального окружения
Рекомендуется работать в отдельной вкладке tmux:
```bash
tmux new -s best_realty_stats_bot
```
Создайте окружение с помощью Poetry:
```bash
poetry shell
```
Установите зависимости:
```bash
poetry install
```

### 3. Миграция базы данных
Выполните миграцию базы данных:
```bash
python common/migration.py
```

### 4. Настройка системного сервиса
Оба сервиса запускаются через единую точку: `python services/__main__.py`. Рекомендую использовать сервис для этого.

В директории `services/` находится пример системного сервиса: `best_realty_monitoring_bot.service`.

Не забудьте изменить следующие параметры:
 - `WorkingDirectory=/projects/best_realty_stats_bot` — укажите корректный путь к проекту.
 - `ExecStart=/root/.cache/pypoetry/virtualenvs/my_new_service_env/bin/python -m services/main.py` — укажите корректный путь к окружению Poetry.

Скопируйте файл сервиса в системную директорию:
```bash
sudo cp services/best_realty_monitoring_bot.service /etc/systemd/system/best_realty_monitoring_bot.service
```

Загрузите изменения в systemd:
```bash
sudo systemctl daemon-reload
```

Запустите сервис:
```bash
sudo systemctl start best_realty_monitoring_bot.service
```

Чтобы сервис автоматически запускался при перезагрузке системы, выполните:
```bash
sudo systemctl enable best_realty_monitoring_bot.service
```

### 5. Настройка Nginx для api_service
Настройте Nginx для проксирования запросов к **api_service**:
```bash
sudo nano /etc/nginx/sites-enabled/my_domain.dev
```
Пример конфигурации:
```nginx
server {
    server_name my_domain.dev;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    listen 80;
}
```
Рекомендуется также установить SSL-сертификат через Let's Encrypt для повышения безопасности.

### 6. Тестирование сервисов

Для тестирования `api_service` используйте скрипт с тестовыми запросами: `services/api_service/main.http`

Для тестирования `bot_service` отправьте команду `/getStats` вашему боту в Telegram. 