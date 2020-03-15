#!/usr/local/bin/python3

import uuid
import datetime as dt
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_PATH = "sqlite:///sochi_athletes.sqlite3"
WIDTH = 66
Base = declarative_base()
class User(Base):
    __tablename__ = 'user'
    id = sa.Column(sa.Integer, primary_key = True, autoincrement = True)
    first_name = sa.Column(sa.Text)
    last_name = sa.Column(sa.Text)
    gender = sa.Column(sa.Text)
    email = sa.Column(sa.Text)
    birthdate = sa.Column(sa.Text)
    height = sa.Column(sa.Float)

class Athlete(Base):
    __tablename__ = 'athelete'
    id = sa.Column(sa.Integer, primary_key = True, autoincrement = True)
    age = sa.Column(sa.Integer, default = 0)
    birthdate = sa.Column(sa.Text)
    gender = sa.Column(sa.Text)
    height = sa.Column(sa.Float)
    name = sa.Column(sa.Text)
    weight = sa.Column(sa.Integer)
    gold_medals = sa.Column(sa.Integer)
    silver_medals = sa.Column(sa.Integer)
    bronze_medals = sa.Column(sa.Integer)
    total_medals = sa.Column(sa.Integer)
    sport = sa.Column(sa.Text)
    country = sa.Column(sa.Text)

def connectDB():
    engine = sa.create_engine(DB_PATH)
    Base.metadata.create_all(engine)
    session = sessionmaker(engine)
    return session()

#функции для вывода красоты в табличке
def print_header(tag = None):
    if tag is None:
        print("+"+"-"*(WIDTH-2)+" +")
    else:
        pass
    #оставим заготовку под вывод в html
def print_line(line, align = "left", tag = None):
    switch_ = {"center": [1,1], "right":[2,0], "left":[0,2] }
    line = line.strip()
    line_width = len(line)
    
    if line_width > WIDTH:
        print("УВЕЛИЧИТЬ ШИРИНУ ВЫВОДА!")
    if tag is None:
        shifts_ = switch_[align]
        prefix = (WIDTH - 2 - line_width)//2# -2 боковые рамки
        print_ = f"|{' '*prefix * shifts_[0]}{line}{' ' * (prefix)* shifts_[1]}"
        postfix_ = f'{" "*(WIDTH-len(print_))}|'
        print(f"{print_}{postfix_}")
    else:
        pass
#получаем код пользователя
def request_data():
    print_header()
    print_line("Поиск данных в БД WADA", align = "center")
    print_header()
    id_ = input("Введите идентификатор пользователя: ")
    try:
        id_ = int(id_)
    except ValueError:
        print("Неверный формат! Введите целое число!\n")
        id_ = 0
    return int(id_)
#а есть ли такой пользователь в таблице пользователей?
def check_id(id_, session):
    query = session.query(User).filter(User.id == id_)
    if query.count():
        user_ = query.first()
        return [user_.birthdate, user_.height, user_.first_name, user_.last_name, user_.gender, user_.email]
    else:
        return []
#делаем выборку по заданному параметру - значение даты рождения или роста для случая, когда есть спортсмен с таким же значением параметра
def query_data_same(session, birthdate = None, height = None):
    #определяем по какому параметру нужно сделать выборку, можно выбрать только один из параметров!
    if (birthdate is None) and (height is None): 
        print_line("Ошибка! Функция ожидает одного параметра для поиска!")
        return
    elif (birthdate is not None) and (height is not None):
        print_line("Ошибка! Функция ожидает только один параметр для поиска!")
        return
    elif birthdate is not None:
        query_Field = Athlete.birthdate
        query_Condition = birthdate
        same_ = {"birthdate":birthdate}
        pre_ = "Сверстник"
    else:
        query_Field = Athlete.height
        query_Condition = height
        same_ = {"height":height}
        pre_ = "Один рост"

    query = session.query(Athlete).filter(query_Field == query_Condition).order_by(Athlete.name.asc()).limit(1)
    ath_eq_ = query.first() #однолетка
    if ath_eq_:
        print_line(f"{pre_}: {ath_eq_.name}, {ath_eq_.birthdate}, {ath_eq_.height}", align = "center")
        #если найден сверстник, остальные не важны
    else:
        query_data(session, **same_)
#поиск по росту

#делаем выборку по заданному параметру - значение даты роджения или роста для случая, когда нет спортсменов с таким же значением параметра
def query_data(session, birthdate = None, height = None):
    #определяем по какому параметру нужно сделать выборку, можно выбрать только один из параметров!
    #как вариант, можно сделать через словарь без распаковки при вызове и заменть на проверку через get()
    if (birthdate is None) and (height is None): 
        print_line("Ошибка! Функция ожидает одного параметра для поиска!")
        return
    elif (birthdate is not None) and (height is not None):
        print_line("Ошибка! Функция ожидает только один параметр для поиска!")
        return
    elif birthdate is not None:
        query_Field = Athlete.birthdate
        query_Condition = birthdate
    else:
        query_Field = Athlete.height
        query_Condition = height
    #получаем 2 набора данных для ближайших атлетов:
    #     старше и отсортировано по возрастанию, имя первым по алфавиту, ровно одна запись
    #     младше и сортировка по убыванию,  имя первым по алфавиту, ровно одна запись
    query = session.query(Athlete).filter(query_Field > query_Condition).order_by(query_Field.asc(),Athlete.name.asc()).limit(1)
    ath_ge_ = query.first() #больше
    query = session.query(Athlete).filter(query_Field < query_Condition).order_by(query_Field.desc(),Athlete.name.asc()).limit(1)
    ath_le_ = query.first() #меньше
        
    if (not ath_le_) and (not ath_ge_):
        print_line("Ошибка БД. Таблица атлетов пуста!")
        return
    if not ath_le_:
        print_line(f"Ближайший: {ath_ge_.name}, {ath_ge_.birthdate}, {ath_ge_.height}")
        #если меньше никого нет, то ближайший - больше
    elif not ath_ge_:
        print_line(f"Ближайший: {ath_le_.name}, {ath_le_.birthdate}, {ath_le_.height}")
        #если больше никого нет, то ближайший - меньше
    else:
        query_gt_ = 0
        query_lt_ = 0
        #определяем специфичный параметр для сравнения выбранных записей, какая из них ближе к заданному
        if birthdate is not None:
            ge_date_ = dt.date.fromisoformat(ath_ge_.birthdate)
            le_date_ = dt.date.fromisoformat(ath_le_.birthdate)
            eq_date_ = dt.date.fromisoformat(birthdate)
            
            query_gt_ = (ge_date_ - eq_date_) > (eq_date_ - le_date_)
            query_lt_ = (ge_date_ - eq_date_) < (eq_date_ - le_date_)
            #параметр выбора для даты
        else:
            try_height_ = ath_ge_height_.height + ath_le_height_.height - height * 2
            query_gt_ = try_height_ > 0 # le
            query_lt_ = try_height_ < 0 # ge
            #параметр выбора для роста
        
        if query_gt_:
            query_final_ = f"Ближайший: {ath_le_.name}, {ath_le_.birthdate}, {ath_le_.height}"
        elif query_lt_:
            query_final_ = f"Ближайший: {ath_ge_.name}, {ath_ge_.birthdate}, {ath_ge_.height}"
        else:
            print_line(f"Ближайший: {ath_ge_.name}, {ath_ge_.birthdate}, {ath_ge_.height}")
            print_line(f"Ближайший: {ath_le_.name}, {ath_le_.birthdate}, {ath_le_.height}")
            query_final_ = "Разница в возрасте одинакова!"
        print_line(query_final_, align = "center")
#вывод данных по поиску
def print_athletes(id_data, session):
    #преобразуем дату к формату ISO записи даты в базе гггг-мм-дд
    convert_date = id_data[0].split("-")
    convert_date.reverse()
    convert_date = "-".join(convert_date)
    
    gender_ = {"Male":"муж.", "Female":"жен."}
    #наводим красоту для возраста
    print_header()
    print_line(f"= {id_data[3]} {id_data[2]}, пол: {gender_[id_data[4]]}, email: {id_data[5]}")
    print_header()
    print_line("Дата рождения:"+convert_date, align = "center")
    print_line("-"*10, align = "center")
    #ищем по дате рождения
    query_data_same(session, birthdate = convert_date)
    #наводим красоту по росту
    height_ = id_data[1]    
    
    print_header()
    print_line(f"Рост пользователя: {id_data[1]}", align = "center")
    print_line("-"*10, align = "center")
    #ищем по росту
    query_data_same(session, height = height_)

    print_header()


def main():
    try:
        session = connectDB()
    except:
        print("Ошибка подключения к базе! Проверьте, а есть ли база в папке с модулями")
        exit()
        
    id_ = 0
    while not id_:
        id_ = request_data()
    id_data = check_id(id_,session)
    if not id_data:
        print("Пользователь не найден!")
        return
    else:
        print_athletes(id_data, session)

if __name__ == "__main__":
    main()








