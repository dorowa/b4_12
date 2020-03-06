#!/usr/bin/python3
#import os
#import json
"""
CREATE TABLE user(
    "id"            integer primary key autoincrement, 
    "first_name"    text, 
    "last_name"     text, 
    "gender"        text, 
    "email"         text, 
    "birthdate"     text, 
    "height"        real
    );
"""
#import uuid
import datetime as dt
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import re

DB_PATH = "sqlite:///sochi_athletes.sqlite3"
Base = declarative_base()

#так как в таблицах поле id автоинкрементное, можно не заморачиваться с генерированием id через uuid
class User(Base):
    __tablename__ = 'user'
    id = sa.Column(sa.Integer, primary_key = True, autoincrement = True)
    first_name = sa.Column(sa.Text)
    last_name = sa.Column(sa.Text)
    gender = sa.Column(sa.Text)
    email = sa.Column(sa.Text)
    birthdate = sa.Column(sa.Text)
    height = sa.Column(sa.Float, default = 0)

def connectDB():
    engine = sa.create_engine(DB_PATH)
    Base.metadata.create_all(engine)
    session = sessionmaker(engine)
    return session()

def request_data():
    #упростим жизнь пользователям, для ввода пола можно использовать сокращения
    #также можно добить словать и английскими сокращениями
    gender_ = {"м":"Male","у":"Male","му":"Male","муж":"Male","ж":"Female","е":"Female","же":"Female","жен":"Female"}
    print("+"+"-"*31+"+")
    print("| Привет! Я запишу твои данные! |")
    print("+"+"-"*31+"+")
    
    first_name = input("Введи свое имя: ")
    last_name = input("Введи свою фамилию: ")
    #чтоб не разводить код проверками, проверим правильность почтового ящика через регулярку
    #ввод не прекращается пока пользователь не введет корректный ящик (доступность не проверяем)
    re_ = r"[a-zA-z]\w+\@(\w+\.)+\w+$"
    re_ = re.compile(re_)
    err_msg = ""
    while True:
            email = input(err_msg+"Введите email:").lower().strip()    
            email_ = re_.match(email)
            if email_ is None:
                err_msg = "Ошибка формата! "
                continue
            else:
                break
    #получаем пол, если пользователь не осилил правильно ввести пол,
    #делаем по умолчанию мальчиком, а могли бы бы и девочкой
    try:
        gender = gender_[input("Пол (муж/жен):").strip()]
    except KeyError:
        gender = "Female"
    #тут также, чтобы не разводить код проверками, ограничим ввод даты рождения
    #форматом ISO в обратной записи дд-мм-гггг через регулярку
    #ввод не прекращается пока не будут введена правильная дата
    #дополнительно проверим, чтобы дата была правильной с точки зрения календаря 30.02. не зайдет
    re_ = r"[0-3][0-9]-[0-1][0-9]-[1-2][0-9]{3}$"
    re_ = re.compile(re_)
    err_msg = ""
    while True:
            birthdate = input(err_msg+"Дата рождения (дд-мм-гггг):").strip()    
            birthdate_ = re_.match(birthdate)
            b_test = birthdate.split("-")
            b_test.reverse()
            if birthdate_ is None:
                err_msg = "Ошибка формата! "
                continue
            else:
                b_test = "-".join(b_test)
                try:
                    dt_test = dt.date.fromisoformat(b_test)
                    break
                except ValueError:
                    err_msg = "Ошибка даты! "
                    continue

    height = input("Рост, см: ")
    try:
        height = int(height)/100
    except ValueError:
        height = 1.80
#    user_id = str(uuid.uuid4())
    user = User(
#        id = user_id,
        first_name = first_name,
        last_name = last_name,
        gender = gender,
        email = email,
        birthdate = birthdate,
        height = height
    )
    return user

def print_users_list(session):
    query = session.query(User)
    users_cnt = query.count()
    if not users_cnt:
        print("Список пользователей пуст!")
        return
    user_users = query.all()
    if user_users:
        print("Найдено пользователей:", users_cnt)
        print("+"+"-"*6+"+"+"-"*50+"+")
        print("|  id  |       Имя/Фамилия, пол, дата рождения, рост      |")
        print("+"+"-"*6+"+"+"-"*50+"+")
        for user_user in user_users:
            id_pre = 4-len(str(user_user.id))
            output_= f"{user_user.first_name}, {user_user.last_name}, {user_user.gender}, {user_user.birthdate}, {user_user.height} |"
            out_pre = 51 - len(output_)
            print(f"|  {user_user.id}"+" "*id_pre+"|"+" "*out_pre+output_)
        print("+"+"-"*6+"+"+"-"*50+"+")
    else:
        print("Пользователей с таким именем нет!")

def main():
    session = connectDB()
    print("+"+"-"*35+"+")
    print("| Выбери режим:"+" "*21+"|\n| 1 - добавить нового пользователя  |\n| 2 - вывести список пользователей  |")
    print("+"+"-"*35+"+")
    mode = input(":")
    if mode == "1":
        user = request_data()
        session.add(user)
        session.commit()
        print("Спасибо, данные сохранены!")        
    elif mode == "2":
        print_users_list(session)
    else:
        print("Некорректный режим!")

if __name__ == "__main__":
    main()








