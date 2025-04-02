import sqlite3
import csv
import datetime

now_date = datetime.datetime.utcnow().strftime("%H:%M-%d.%m.%Y")

class SQL_atm:
    # создание таблицы
    @staticmethod
    def create_table():
        with sqlite3.connect("atm.db") as db:
            cur = db.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS Users_data(
                        UserID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Number_card INTEGER NOT NULL,
                        Pin_code INTEGER NOT NULL,
                        Balance INTEGER NOT NULL);""")
    
    # заполнение базы пользователями
    @staticmethod
    def insert_users(data_users):
        with sqlite3.connect("atm.db") as db:
            cur = db.cursor()
            cur.execute("""INSERT INTO Users_data(Number_card, Pin_code, Balance) VALUES (?, ?, ?);""", data_users)

    # ввод и проверка номера карты
    @staticmethod
    def input_card(number_card):
        try:
            with sqlite3.connect("atm.db") as db:
                cur = db.cursor()
                cur.execute(f"""SELECT Number_card FROM Users_data WHERE Number_card = {number_card}""")
                result_card = cur.fetchone()
                if result_card == None:
                    print("Введен неизвестный номер карты")
                    return False
                else:
                    return True
        except:
            print("Введен неизвестный номер карты")
    
    # ввод и проверка пин-кода
    @staticmethod
    def input_code(number_card):
        pin_code = input("Введите пин-код: ")
        with sqlite3.connect("atm.db") as db:
                cur = db.cursor()
                cur.execute(f"""SELECT Pin_code FROM Users_data WHERE Number_card = {number_card}""")
                result_code = cur.fetchone()
                input_pin = result_code[0]
                try:
                    if input_pin == int(pin_code):
                        print("Введен верный пин-код")
                        return True
                    else:
                        print("Введен неверный пин-код")
                        return False
                except:
                    print("Введен неверный пин-код")
                    return False
                
    # проверка баланса
    @staticmethod
    def info_balance(number_card):
        with sqlite3.connect("atm.db") as db:
                cur = db.cursor()
                cur.execute(f"""SELECT Balance FROM Users_data WHERE Number_card = {number_card}""")
                result_info_balance = cur.fetchone()
                balance_card = result_info_balance[0]
                print(f"Баланс вашей карты: {balance_card}")

    # снятие средств с баланса
    @staticmethod
    def withdraw_money(number_card):
        amount = input("Введите сумму, необходимую для снятия: ")
        with sqlite3.connect("atm.db") as db:
                cur = db.cursor()
                cur.execute(f"""SELECT Balance FROM Users_data WHERE Number_card = {number_card}""")
                result_info_balance = cur.fetchone()
                balance_card = result_info_balance[0]
                try:
                    if int(amount) > balance_card:
                        print("На вашей карте недостаточно средств")
                        return False
                    else:
                        cur.execute(f"""UPDATE Users_data SET Balance = Balance - {amount} WHERE Number_card = {number_card}""")
                        db.commit()
                        SQL_atm.info_balance(number_card)
                        SQL_atm.report_operation_1(now_date, number_card, "1", amount, "")
                        return True
                except:
                    print("Попытка выполнить некорректное действие")
                    return False
                
    # пополнение баланса
    @staticmethod
    def depositing_money(number_card):
        amount = input("Введите сумму, необходимую для внесения: ")
        with sqlite3.connect("atm.db") as db:
                try:
                    amount = int(amount)
                    if amount <= 0:
                        print("Попытка выполнить некорректное действие")
                        return False
                    cur = db.cursor()
                    cur.execute(f"""SELECT Balance FROM Users_data WHERE Number_card = {number_card}""")
                    cur.execute(f"""UPDATE Users_data SET Balance = Balance + {amount} WHERE Number_card = {number_card}""")
                    db.commit()
                    SQL_atm.info_balance(number_card)
                    SQL_atm.report_operation_1(now_date, number_card, "2", amount, "")
                    return True
                except:
                    print("Попытка выполнить некорректное действие")
                    return False
                
    # перевод средств другому пользователю
    @staticmethod
    def send_money(number_card):
        amount = input("Введите сумму, необходимую для отправки: ")
        with sqlite3.connect("atm.db") as db:
            cur = db.cursor()
            cur.execute(f"""SELECT Balance FROM Users_data WHERE Number_card = {number_card}""")
            result_info_balance = cur.fetchone()
            if result_info_balance is None:
                print("Карта отправителя не найдена")
                return False
            balance_card = result_info_balance[0]
            try:
                amount = int(amount)
                if amount <= 0:
                    print("Попытка выполнить некорректное действие")
                    return False
                if amount > balance_card:
                    print("На вашей карте недостаточно средств")
                    return False
                
                target_number = input("Введите номер карты получателя: ")
                try:
                    target_number = int(target_number)
                except ValueError:
                    print("Введен неизвестный номер карты")
                    return False
                
                cur.execute(f"""SELECT Number_card FROM Users_data WHERE Number_card = {target_number}""")
                result_target = cur.fetchone()
                if result_target is None:
                    print("Введен неизвестный номер карты")
                    return False
                
                target = result_target[0]
                if target == int(number_card):
                    print("Ошибка, нельзя выполнять перевод самому себе")
                    return False
                
                cur.execute(f"""UPDATE Users_data SET Balance = Balance - {amount} WHERE Number_card = {number_card}""")
                cur.execute(f"""UPDATE Users_data SET Balance = Balance + {amount} WHERE Number_card = {target}""")
                db.commit()
                SQL_atm.report_operation_1(now_date, number_card, "3", amount, target)
                SQL_atm.report_operation_2(now_date, target, "3", amount, number_card)
                SQL_atm.info_balance(number_card)
                return True
            except ValueError:
                print("Попытка выполнить некорректное действие")
                return False
                
    # выбор операции
    @staticmethod
    def input_operation(number_card):
        while True:
            operation = input("Введите номер необходимой операции:\n1. Проверка баланса\n2. Снятие средств\n3. Внесение средств\n4. Отправить средства\n5. Завершить работу\n")
            if operation == "1":
                SQL_atm.info_balance(number_card)
            elif operation == "2":
                SQL_atm.withdraw_money(number_card)
            elif operation == "3":
                SQL_atm.depositing_money(number_card)
            elif operation == "4":
                SQL_atm.send_money(number_card)
            elif operation == "5":
                print("Спасибо за ваш визит, всего доброго!")
                return False
            else:
                print("Ошибка, такой операции не существует")

    # отчет о работе1
    @staticmethod
    def report_operation_1(now_date, number_card, type_operation, amount, payee):
        """Типы операций:
        1 - Снятие средств
        2 - Пополнение счета
        3 - Перевод средств"""
        user_data = [
            (now_date, number_card, type_operation, amount, payee)
        ]
        with open("report_1.csv", "a", newline='') as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerows(
                user_data
            )
    
    # отчет о работе2
    @staticmethod
    def report_operation_2(now_date, payee, type_operation, amount, sender):
        # Date, Payee, Type operation, Amount, Sender
        user_data = [
            (now_date, payee, type_operation, amount, sender)
        ]
        with open("report_2.csv", "a", newline='') as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerows(
                    user_data
                )