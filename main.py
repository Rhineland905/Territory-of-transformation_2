import mysql.connector
import telebot
import re
from telebot.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat



my_bot = telebot.TeleBot('5116218178:AAHThqvo_5BpxJv8L_kpgrM_a7LQPZQEfI4')

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

def set_bot_commands():
    user_commands = [
        BotCommand("text", "text"),
        BotCommand("help", "Допомога"),
        BotCommand("about", "Про бота")
    ]
    my_bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())
    super_admin_id = [534670150,565948862]
    super_admin = [
        BotCommand("admin", "Видавваня адмінки"),
        BotCommand("help", "Допомога"),
        BotCommand("about", "Про бота")
    ]
    for admin_id in super_admin_id:
        my_bot.set_my_commands(super_admin, scope=BotCommandScopeChat(admin_id))

set_bot_commands()
def is_valid_name(text):
    pattern = r'^[А-Яа-яЇїІіЄєҐґ]{2,}$'
    return bool(re.match(pattern, text))
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

@my_bot.message_handler(commands=['menu'])
def admin(message):
    pass

@my_bot.message_handler(commands=['start'])
def start(message):
    my_bot.send_message(message.chat.id, f'<text>', reply_markup=markup)

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