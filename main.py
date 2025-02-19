import mysql.connector,telebot,re,json

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
    BotCommand("curator_give", "Додати куратора/Подивитися куратора"),
    BotCommand("curator_delete", "Видалити куратора"),
]
super_admin = [
    BotCommand("admin_give", "Додати адміна"),
    BotCommand("admin_delete", "Видалити адміна"),
    BotCommand("list_user", "Перечень зарегистрованих користувачів"),
    BotCommand("curator", "Додати куратора/Подивитися куратора"),
]

def create_curator_markup(user_id):
    markup = telebot.types.InlineKeyboardMarkup()
    curator_update = telebot.types.InlineKeyboardButton("Обновити опис", callback_data=f'update_curator:{user_id}')
    delete_curator = telebot.types.InlineKeyboardButton("Видалити куратора", callback_data=f'delete_curator:{user_id}')
    markup.add(curator_update)
    markup.add(delete_curator)
    return markup

def creat_curator_registration_markup():
    with conn_tg.cursor() as curs:
        curs.execute("SELECT * FROM curator")
        curator_data = curs.fetchall()
    markup = telebot.types.InlineKeyboardMarkup()

    for i in curator_data:
        user_data = take_user_data_id(i[1])
        add_curator = telebot.types.InlineKeyboardButton(f"{user_data[0][2]} {user_data[0][3]}", callback_data=f'regestration_curator:{i[1]}')
        markup.add(add_curator)
    return markup



def set_bot_commands():
    with conn_tg.cursor() as curs:
        curs.execute('SELECT * FROM user WHERE admin = %s OR super_admin = %s', (True, True))
        user_data = curs.fetchall()
    for admin_id in user_data:
        if user_data[0][6]:
            my_bot.set_my_commands(super_admin, scope=BotCommandScopeChat(admin_id[1]))
        elif user_data[0][4]:
            my_bot.set_my_commands(admin, scope=BotCommandScopeChat(admin_id[1]))


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
                my_bot.set_my_commands(user_commands, scope=BotCommandScopeChat(user_data[0][1]))

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
                my_bot.set_my_commands(user_commands, scope=BotCommandScopeChat(user_data[0][1]))
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
        my_bot.send_message(message.chat.id, "Виберіть куратора.",reply_markup=creat_curator_registration_markup())
    else:
        my_bot.send_message(message.chat.id, "Ви ввели неправильне ім'я або фамілю")
        my_bot.register_next_step_handler(message, firts_last_name)


def curator(message):
    if admin_chek(message):
        if len_chek(message) == 1:
            text = message.text
            if take_user_data_id(text):
                if not take_curator_date(text):
                    with conn_tg.cursor() as curs:
                        curs.execute('INSERT INTO curator (user_id) VALUES (%s)',(text,))
                        conn_tg.commit()
                    my_bot.send_message(message.chat.id, f"Куратора успішно додано.")
                else:
                    user_data = take_user_data_id(text)
                    curator_data = take_curator_date(text)
                    my_bot.send_message(message.chat.id, f"\t {user_data[0][2]} {user_data[0][3]} \n {curator_data[0][3]}",reply_markup=create_curator_markup(text))
            else:
                my_bot.send_message(message.chat.id, "Користувача не існує в системі.")
        elif len_chek(message) == 2:
            text = message.text
            parts = text.split(maxsplit=1)
            user_data = take_user_data_FirstLastName(parts[0],parts[1])
            if user_data:
                curator_data = take_curator_date(user_data[0][1])
                if not curator_data:
                    with conn_tg.cursor() as curs:
                        curs.execute('INSERT INTO curator (user_id) VALUES (%s)', (user_data[0][1],))
                        conn_tg.commit()
                        my_bot.send_message(message.chat.id, f"Куратора успішно додано.")
                else:
                    my_bot.send_message(message.chat.id, f"\t {user_data[0][2]} {user_data[0][3]} \n {curator_data[0][3]}",reply_markup=create_curator_markup(user_data[0][1]))

            else:
                my_bot.send_message(message.chat.id, "Користувача не існує в системі.")

def update_curator(message,user_id):
    with conn_tg.cursor() as curs:
        curs.execute("UPDATE curator SET description=%s WHERE user_id=%s", (message.text,user_id))
        conn_tg.commit()
    my_bot.send_message(message.chat.id, "Дані успішно оновлено.")

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

@my_bot.callback_query_handler(func=lambda call: call.data.startswith("delete_curator:"))
def delete_curator_callback(call):
    user_id = call.data.split(":")[1]
    with conn_tg.cursor() as curs:
        curs.execute('DELETE FROM curator WHERE user_id = %s', (user_id,))
        conn_tg.commit()
    user_data = take_user_data_id(user_id)
    my_bot.edit_message_text(f"✅ Куратор {user_data[0][2]} {user_data[0][3]} успішно видалений.",call.message.chat.id,call.message.message_id)

@my_bot.callback_query_handler(func=lambda call: call.data.startswith("update_curator:"))
def update_curator_callback(call):
    user_id = call.data.split(":")[1]
    my_bot.send_message(call.message.chat.id, "Введіть опис.")
    my_bot.register_next_step_handler(call.message, update_curator, user_id)

@my_bot.callback_query_handler(func=lambda call: call.data.startswith("regestration_curator:"))
def update_curator_callback(call):
    curator_id = call.data.split(":")[1]
    with conn_tg.cursor() as curs:
        curs.execute("UPDATE user SET curator=%s WHERE user_id=%s", (curator_id, call.from_user.id))
        conn_tg.commit()
    my_bot.send_message(call.message.chat.id, "Ви успішно зареєструвалися.")
    curato_data = take_curator_date(curator_id)


@my_bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    id = call.from_user.id
    if call.data == "register":
        with conn_tg.cursor() as curs:
            curs.execute(f'SELECT * FROM  user WHERE user_id=%s', (id,))
            user_data = curs.fetchall()
        if not user_data:
            my_bot.send_message(call.message.chat.id, "Введіть ім'я та фамілію")
            my_bot.register_next_step_handler(call.message, firts_last_name)
        else:
            my_bot.send_message(call.message.chat.id, "Ви вже зареєстровані")










my_bot.polling()