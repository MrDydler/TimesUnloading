# TimesUnloading

В директории с проектом нужно создать файл config.txt и заполнить необходимые переменные. Запуск через ready.py


[DEFAULT]

#Переменные вводятся без кавычек

#email toggle
toggle_login = myToggleLogin

#Пароль toggle
toggle_pass = myTogglePass

#За какой диапазаон будем выгружать карточки тоггла YYYY-MM-DD 

start_date = 2023-07-01

end_date = 2023-09-09

#Kaiten api-key
api_key = можно узнать в настройках профиля


[POSTGRES]

host = 127.0.0.1

user = postgres

password = pass

db_name = test

port = 5432






ПРИМЕР
[POSTGRES]
user = postgres
password = 1337
db_name = postgres
host = 127.0.0.1
port = 5433


[DEFAULT]
toggle_login = a.gubashew@web-regata.ru
toggle_pass = passtoggl
start_date = 2023-07-01
end_date = 2023-09-14
api_key = d02df52b-api-4971-a0fd-b57ead3718c5




