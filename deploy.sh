#!/bin/bash

# Проверка наличия root прав
if [[ $EUID -ne 0 ]]; then
   echo "Этот скрипт должен быть запущен с правами root" 
   exit 1
fi

# Определение переменных
PROJECT_NAME="gorbachev-shop"
PROJECT_PATH="/var/www/$PROJECT_NAME"
PYTHON_VERSION="3.10"
DOMAIN="example.com"
USER="www-data"
GROUP="www-data"

echo "Начало установки зависимостей..."

# Обновление системы
apt update && apt upgrade -y

# Установка необходимых пакетов
apt install -y \
    python$PYTHON_VERSION \
    python$PYTHON_VERSION-dev \
    python3-pip \
    postgresql \
    postgresql-contrib \
    nginx \
    redis-server \
    supervisor \
    certbot \
    python3-certbot-nginx \
    git \
    build-essential \
    libpq-dev \
    curl

echo "Установка зависимостей завершена"

# Создание директории проекта
mkdir -p $PROJECT_PATH
chown -R $USER:$GROUP $PROJECT_PATH

# Настройка PostgreSQL
echo "Настройка PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE ${PROJECT_NAME};"
sudo -u postgres psql -c "CREATE USER ${PROJECT_NAME} WITH PASSWORD '${DB_PASSWORD}';"
sudo -u postgres psql -c "ALTER ROLE ${PROJECT_NAME} SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE ${PROJECT_NAME} SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE ${PROJECT_NAME} SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${PROJECT_NAME} TO ${PROJECT_NAME};"

# Настройка виртуального окружения
echo "Настройка виртуального окружения Python..."
python$PYTHON_VERSION -m pip install virtualenv
python$PYTHON_VERSION -m virtualenv $PROJECT_PATH/venv
source $PROJECT_PATH/venv/bin/activate

# Установка зависимостей Python
echo "Установка зависимостей Python..."
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Настройка Django
echo "Настройка Django..."
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser

# Настройка Gunicorn
echo "Настройка Gunicorn..."
cat > /etc/supervisor/conf.d/$PROJECT_NAME.conf << EOF
[program:$PROJECT_NAME]
command=$PROJECT_PATH/venv/bin/gunicorn --workers 3 --bind unix:$PROJECT_PATH/$PROJECT_NAME.sock backend.wsgi:application
directory=$PROJECT_PATH
user=$USER
group=$GROUP
autostart=true
autorestart=true
stderr_logfile=/var/log/$PROJECT_NAME/gunicorn.err.log
stdout_logfile=/var/log/$PROJECT_NAME/gunicorn.out.log
EOF

mkdir -p /var/log/$PROJECT_NAME
chown -R $USER:$GROUP /var/log/$PROJECT_NAME

# Настройка Celery
echo "Настройка Celery..."
cat > /etc/supervisor/conf.d/$PROJECT_NAME-celery.conf << EOF
[program:${PROJECT_NAME}-celery]
command=$PROJECT_PATH/venv/bin/celery -A backend worker -l info
directory=$PROJECT_PATH
user=$USER
group=$GROUP
autostart=true
autorestart=true
stderr_logfile=/var/log/$PROJECT_NAME/celery.err.log
stdout_logfile=/var/log/$PROJECT_NAME/celery.out.log
EOF

# Настройка Redis
echo "Настройка Redis..."
systemctl enable redis-server
systemctl start redis-server

# Копирование и настройка Nginx конфигурации
echo "Настройка Nginx..."
cp nginx.conf.example /etc/nginx/sites-available/$DOMAIN
ln -s /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Получение SSL сертификата
echo "Получение SSL сертификата..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN

# Перезапуск сервисов
echo "Перезапуск сервисов..."
supervisorctl reread
supervisorctl update
supervisorctl start $PROJECT_NAME
supervisorctl start ${PROJECT_NAME}-celery
systemctl restart nginx

# Настройка файрвола
echo "Настройка файрвола..."
ufw allow 'Nginx Full'
ufw allow ssh
ufw enable

# Создание скрипта для бэкапов
echo "Настройка системы бэкапов..."
cat > /usr/local/bin/backup.sh << EOF
#!/bin/bash
BACKUP_DIR="/var/backups/$PROJECT_NAME"
DATE=\$(date +%Y%m%d_%H%M%S)
mkdir -p \$BACKUP_DIR

# Backup database
pg_dump ${PROJECT_NAME} > \$BACKUP_DIR/db_\${DATE}.sql

# Backup media files
tar -czf \$BACKUP_DIR/media_\${DATE}.tar.gz $PROJECT_PATH/mediafiles

# Backup env files
cp $PROJECT_PATH/.env \$BACKUP_DIR/env_\${DATE}

# Remove backups older than 7 days
find \$BACKUP_DIR -type f -mtime +7 -delete
EOF

chmod +x /usr/local/bin/backup.sh

# Добавление задачи в cron для ежедневного бэкапа
echo "0 3 * * * root /usr/local/bin/backup.sh" > /etc/cron.d/$PROJECT_NAME-backup

echo "Установка завершена!"
echo "Проверьте работу сайта по адресу: https://$DOMAIN"
echo ""
echo "Не забудьте:"
echo "1. Настроить файл .env с реальными значениями"
echo "2. Настроить мониторинг сервера"
echo "3. Настроить ротацию логов"
echo "4. Проверить права доступа к файлам"
echo "5. Настроить регулярные обновления системы"
