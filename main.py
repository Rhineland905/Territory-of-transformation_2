import mysql.connector
import telebot
import re
from telebot.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat



my_bot = telebot.TeleBot('7848940794:AAHwffW6cs8GwRyGBcxBS2-UaOsL63WMFzI')

config_tg = {
    'user': 'root',
    'password': '8012',
    'host': 'localhost',
    'database': 'test'
}

conn_tg = mysql.connector.connect(**config_tg)

markup = telebot.types.InlineKeyboardMarkup()
button = telebot.types.InlineKeyboardButton('Реєстрація', callback_data='register')
markup.add(button)
user_commands = [
    BotCommand("text", "text"),
]

my_bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())

admin = [
    BotCommand("list_user", "Перечень зарегистрованих користувачів"),
    BotCommand("curator", "Додати куратора"),
]
super_admin = [
    BotCommand("admin_give", "Додати адміна"),
    BotCommand("admin_delete", "Видалити адміна"),
    BotCommand("list_user", "Перечень зарегистрованих користувачів"),
    BotCommand("curator", "Додати куратора"),
]




def set_bot_commands():
    with conn_tg.cursor() as curs:
        curs.execute(f'SELECT * FROM  user WHERE admin=%s', (True,))
        user_data = curs.fetchall()
    for admin_id in user_data:
        if user_data[0][6]:
            my_bot.set_my_commands(super_admin, scope=BotCommandScopeChat(admin_id[1]))
        elif user_data[0][4]:
            my_bot.set_my_commands(admin, scope=BotCommandScopeChat(admin_id[1]))
        else:
            my_bot.set_my_commands(user_commands, scope=BotCommandScopeChat(admin_id[1]))

set_bot_commands()
def take_curator_date(id):
    with conn_tg.cursor() as curs:
        curs.execute(f'SELECT * FROM  curator WHERE user_id=%s', (str(id),))
        user_curator = curs.fetchall()
    return user_curator
def len_chek(message):
    text = message.text
    part = text.split(maxsplit=1)
    if len(part) == 1:
        return 1
    elif len(part) == 2:
        return 2
    else:
        my_bot.send_message(message.chat.id, "Виникла помилка спробуйте ще раз")
        return 0
def take_user_data_id(id):
    with conn_tg.cursor() as curs:
        curs.execute(f'SELECT * FROM  user WHERE user_id=%s', (str(id),))
        user_data = curs.fetchall()
    return user_data
def take_user_data_FirstLastName(first_name,last_name):
    with conn_tg.cursor() as curs:
        curs.execute(f'SELECT * FROM user WHERE first_name=%s AND last_name=%s', (first_name, last_name))
        user_data = curs.fetchall()
    return user_data
def super_admin_chek(message):
    id = message.from_user.id
    with conn_tg.cursor() as curs:
        curs.execute(f'SELECT * FROM  user WHERE user_id=%s', (id,))
        user_data = curs.fetchall()
    if user_data[0][6]:
        return True
    else:
        my_bot.send_message(message.chat.id, "Недостатньо прав для виконання цієї дії")
        return False

def admin_chek(message):
    id = message.from_user.id
    with conn_tg.cursor() as curs:
        curs.execute(f'SELECT * FROM  user WHERE user_id=%s', (id,))
        user_data = curs.fetchall()
    if user_data[0][4] or user_data[0][6]:
        return True
    else:
        my_bot.send_message(message.chat.id, "Недостатньо прав для виконання цієї дії")
        return False

def is_valid_name(text):
    pattern = r'^[А-Яа-яЇїІіЄєҐґ]{2,}$'
    return bool(re.match(pattern, text))
def process_admin_delete(message):
    if super_admin_chek(message):
        text = message.text
        parts = text.split(maxsplit=1)
        if len_chek(message) == 1:
            id = parts[0]
            user_data = take_user_data_id(id)
            if not user_data:
                my_bot.send_message(message.chat.id, "❌ Такого користувача не існує!")
            elif not user_data[0][4]:
                my_bot.send_message(message.chat.id, f"Користувачь не адміністратор")
            else:
                with conn_tg.cursor() as curs:
                    curs.execute("UPDATE user SET admin=%s WHERE user_id=%s", (False, str(id)))
                    conn_tg.commit()
                my_bot.send_message(message.chat.id, f"✅У користувачу {user_data[0][2]} {user_data[0][3]} відібрано адмінку!")
                my_bot.send_message(user_data[0][1], "Вас було позбавлено ролі адміністратора")
                set_bot_commands()
        elif len_chek(message) == 2:
            first_name, last_name = parts[0], parts[1]
            user_data = take_user_data_FirstLastName(first_name,last_name)
            if not user_data:
                my_bot.send_message(message.chat.id, "❌ Такого користувача не існує!")
            elif not user_data[0][4]:
                my_bot.send_message(message.chat.id, "Користувачь не адміністратор")
            else:
                with conn_tg.cursor() as curs:
                    curs.execute("UPDATE user SET admin=%s WHERE first_name=%s AND last_name=%s",(False, first_name, last_name))
                    conn_tg.commit()
                my_bot.send_message(message.chat.id,f"✅ У користувачу {user_data[0][2]} {user_data[0][3]} відібрано адмінку!")
                my_bot.send_message(user_data[0][1], "Вас було позбавлено ролі адміністратора")
                set_bot_commands()


def process_admin_give(message):
    if super_admin_chek(message):
        text = message.text
        parts = text.split(maxsplit=1)
        if len_chek(message) == 1:
            id = parts[0]
            user_data = take_user_data_id(id)
            if not user_data:
                my_bot.send_message(message.chat.id, "❌ Такого користувача не існує!")
            elif user_data[0][4]:
                my_bot.send_message(message.chat.id, f"Вже адміністратор")
            else:
                with conn_tg.cursor() as curs:
                    curs.execute("UPDATE user SET admin=%s WHERE user_id=%s", (True,str(id)))
                    conn_tg.commit()
                my_bot.send_message(message.chat.id, f"✅ Користувачу {user_data[0][2]} {user_data[0][3]} видано адмінку!")
                my_bot.send_message(user_data[0][1], "Вас було підвищено до адміністратора.")
                set_bot_commands()
        elif len_chek(message) == 2:
            first_name, last_name = parts[0], parts[1]
            user_data = take_user_data_FirstLastName(first_name,last_name)
            if not user_data:
                my_bot.send_message(message.chat.id, "❌ Такого користувача не існує!")
            elif user_data[0][4]:
                my_bot.send_message(message.chat.id, "Вже адміністратор")
            else:
                with conn_tg.cursor() as curs:
                    curs.execute("UPDATE user SET admin=%s WHERE first_name=%s AND last_name=%s",(True, first_name, last_name))
                    conn_tg.commit()
                my_bot.send_message(message.chat.id,f"✅ Користувачу {user_data[0][2]} {user_data[0][3]} видано адмінку!")
                my_bot.send_message(user_data[0][1], "Вас було підвищено до адміністратора.")
                set_bot_commands()


def firts_last_name(message):
    id = message.from_user.id
    text = message.text
    parts = text.split(maxsplit=1)
    if is_valid_name(parts[0]) and is_valid_name(parts[1]):
        with conn_tg.cursor() as curs:
            curs.execute("INSERT INTO user (user_id, first_name, last_name) VALUES (%s, %s, %s)",(id,parts[0],parts[1]))
            conn_tg.commit()
            my_bot.send_message(message.chat.id, "Вітаю ви успішно зареєструвалися")
    else:
        my_bot.send_message(message.chat.id, "Ви ввели неправильне ім'я або фамілю")
        my_bot.register_next_step_handler(message, firts_last_name)

def curator(message):
    if admin_chek(message):
        if len_chek(message) == 1:
            id = message.from_user.id
            with conn_tg.cursor() as curs:
                curs.execute(f'SELECT * FROM  curator WHERE user_id=%s', (str(id),))
                curator_data = curs.fetchall()
            if not curator_data:
                with conn_tg.cursor() as curs:
                    curs.execute('INSERT INTO curator (user_id) VALUES (%s)',(id,))
                    conn_tg.commit()
                my_bot.send_message(message.chat.id, f"Куратор успішно додан")
            else:
                pass
@my_bot.message_handler(commands=['curator'])
def curator_command(message):
    my_bot.send_message(message.chat.id, f"Ведіть Ім'я прізвище або id")
    my_bot.register_next_step_handler(message, curator)

@my_bot.message_handler(commands=['admin_give'])
def admin_give(message):
    my_bot.send_message(message.chat.id, f"Ведіть Ім'я прізвище або id")
    my_bot.register_next_step_handler(message, process_admin_give)

@my_bot.message_handler(commands=['admin_delete'])
def admin_give(message):
    my_bot.send_message(message.chat.id, f"Ведіть Ім'я прізвище або id")
    my_bot.register_next_step_handler(message, process_admin_delete)

@my_bot.message_handler(commands=['list_user'])
def list_user(message):
    if admin_chek(message):
        with conn_tg.cursor() as curs:
            curs.execute(f'SELECT * FROM  user')
            user_data = curs.fetchall()
        user_list = "\n".join([f"User ID: {user[1]}, {user[2]} {user[3]}" for user in user_data])
        my_bot.send_message(message.chat.id, f"Список користувачів:\n{user_list}")

@my_bot.message_handler(commands=['start'])
def start(message):
    my_bot.send_message(message.chat.id, f"Доброго дня!\nВас вітає чат-бот «Територія Трансформації». Якщо Ви бажаєте приймати участь у наших марафонах, будь ласка, пройдіть реєстрацію!!", reply_markup=markup)

@my_bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "register":
        id = call.from_user.id
        with conn_tg.cursor() as curs:
            curs.execute(f'SELECT * FROM  user WHERE user_id=%s', (id,))
            user_data = curs.fetchall()
        if not user_data:
            my_bot.send_message(call.message.chat.id, "Введіть ім'я та фамілію")
            my_bot.register_next_step_handler(call.message, firts_last_name)
        else:
            my_bot.send_message(call.message.chat.id, "Ви вже зареєстровані")





my_bot.polling()