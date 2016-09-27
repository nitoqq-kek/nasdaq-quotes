# Парсер котировок nasdaq и сайт с API

**Инструкция для запуска локально**


*Склонировать репозиторий* 
```
git clone https://github.com/nitoqq-kek/nasdaq-quotes.git
```

*Создаем виртуальное окружение python*  
Если используется virtualenvwrapper
```
cd nasdaq-quotes && mkvirtualenv nasdaq-quotes -p /usr/bin/python2.7 -a . -r dev-requirements.txt
export FLASK_APP="nasdaq_quotes.main_app"
```
или на свое усмотрение

*Демо база:*  
Создать базу
Если вы используете Debian или Ubuntu то ansible-playbook установит пакеты и сконфигурирует базу данных автоматически, 
если нет, то настраивайте сами. Настройки подключения к базе в nasdaq_quotes.config
```bash
ansible-playbook -i 'localhost,' db_create.yml -c local

flask db upgrade -d nasdaq_quotes/migrations/

```
Спарсить данные
```bash
flask parse tickers.txt -N 30
```
*Запуск тестового сервера* 
```
flask run
```
