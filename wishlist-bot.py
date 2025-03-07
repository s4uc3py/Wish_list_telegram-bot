import json
import logging
import telebot
from telebot import types

logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(message)s')

bot = telebot.TeleBot('YOUR_BOT_TOKEN')

def load_data():
    try:
        with open('data.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        default_data = {
            "gifts": [],
            "users": {},
            "admins": []
        }
        with open('data.json', 'w', encoding='utf-8') as file:
            json.dump(default_data, file, ensure_ascii=False, indent=4)
        return default_data

def save_data(data):
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def is_admin(user_id):
    data = load_data()
    return str(user_id) in data.get('admins', [])

add_gift_data = {}  # Хранилище для добавления подарков

def generate_main_menu(user_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        types.KeyboardButton("🎁 Список подарков"),
        types.KeyboardButton("📦 Мои бронирования"),
    ]
    if is_admin(user_id):
        buttons.append(types.KeyboardButton("🔒 Админ-панель"))
    keyboard.add(*buttons)
    return keyboard

def generate_admin_menu():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("Добавить подарок", callback_data="admin_add"),
        types.InlineKeyboardButton("Удалить подарок", callback_data="admin_delete"),
        types.InlineKeyboardButton("Все бронирования", callback_data="admin_allbookings")
    )
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    bot.send_message(
        message.chat.id,
        "Добро пожаловать в список желаний!",
        reply_markup=generate_main_menu(user_id)
    )

@bot.message_handler(commands=['list'])
def list_gifts(message):
    data = load_data()
    gifts = data.get("gifts", [])
    if not gifts:
        bot.send_message(message.chat.id, "Список подарков пуст.")
        return
    keyboard = generate_gift_keyboard(gifts, data)
    bot.send_message(message.chat.id, "Выберите подарок:", reply_markup=keyboard)

def generate_gift_keyboard(gifts, data):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for gift in gifts:
        booked_by = gift.get('booked_by')
        status = "Забронировано" if booked_by else "Свободен"
        callback = f"book_{gift['id']}" if not booked_by else f"view_{gift['id']}"
        button = types.InlineKeyboardButton(
            text=f"{gift['name']} ({status})",
            callback_data=callback
        )
        keyboard.add(button)
    return keyboard

@bot.message_handler(commands=['mybookings'])
def my_bookings(message):
    user_id = str(message.from_user.id)
    data = load_data()
    booked = [g for g in data['gifts'] if g.get('booked_by') == user_id]

    if not booked:
        bot.send_message(message.chat.id, "У вас нет забронированных подарков.")
        return

    for gift in booked:
        name = gift['name'].strip()
        link = gift['link'].strip()
        description = gift['description'].strip()

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton("Отменить бронь", callback_data=f"unbook_{gift['id']}")
        )

        bot.send_message(
            message.chat.id,
            f"🎁 {name}\n"
            f"🔗 {link}\n"
            f"📖 {description}",
            reply_markup=keyboard
        )

# Перемещенный обработчик для добавления подарка (должен быть выше handle_buttons)
@bot.message_handler(func=lambda message: str(message.from_user.id) in add_gift_data)
def process_add_steps(message):
    user_id = str(message.from_user.id)
    step = add_gift_data[user_id].get('step')

    if step == 'name':
        add_gift_data[user_id]['name'] = message.text.strip()
        add_gift_data[user_id]['step'] = 'link'
        bot.send_message(
            message.chat.id,
            "Теперь введите ссылку:"
        )
    elif step == 'link':
        add_gift_data[user_id]['link'] = message.text.strip()
        add_gift_data[user_id]['step'] = 'description'
        bot.send_message(
            message.chat.id,
            "Введите описание (или пропустите с помощью /skip):"
        )
    elif step == 'description':
        description = message.text.strip()
        add_gift_data[user_id]['description'] = description
        finalize_add(user_id)

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = message.from_user.id
    text = message.text

    if text == "🎁 Список подарков":
        list_gifts(message)
    elif text == "📦 Мои бронирования":
        my_bookings(message)
    elif text == "🔒 Админ-панель" and is_admin(user_id):
        bot.send_message(
            message.chat.id,
            "Админ-панель. Выберите действие:",
            reply_markup=generate_admin_menu()
        )
    else:
        bot.send_message(message.chat.id, "Неизвестная команда")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    data = load_data()
    user_id = call.from_user.id

    if call.data.startswith("book_"):
        gift_id = int(call.data.split("_")[1])
        username = call.from_user.username or call.from_user.first_name
        for gift in data["gifts"]:
            if gift["id"] == gift_id and not gift["is_booked"]:
                gift["is_booked"] = True
                gift["booked_by"] = str(user_id)
                data["users"][str(user_id)] = username
                save_data(data)
                bot.answer_callback_query(call.id, f"Вы забронировали {gift['name']}")
                logging.info(f"User {user_id} booked gift {gift_id}")
                return
        bot.answer_callback_query(call.id, "Подарок уже забронирован.")

    elif call.data.startswith("view_"):
        gift_id = int(call.data.split("_")[1])
        gift = next((g for g in data["gifts"] if g["id"] == gift_id), None)
        if gift:
            status = "Забронировано" if gift["is_booked"] else "Свободен"
            bot.answer_callback_query(
                call.id,
                f"🎁 {gift['name']}\n"
                f"🔗 {gift['link']}\n"
                f"📖 Описание: {gift['description']}\n"
                f"📦 Статус: {status}"
            )

    elif call.data.startswith("admin_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "У вас нет прав администратора.")
            return

        if call.data == "admin_add":
            bot.edit_message_text(
                "Введите название подарка:",
                call.message.chat.id,
                call.message.message_id
            )
            add_gift_data[str(user_id)] = {"step": "name"}

        elif call.data == "admin_allbookings":
            all_bookings(call.message)

        elif call.data == "admin_delete":
            keyboard = types.InlineKeyboardMarkup()
            for gift in data["gifts"]:
                keyboard.add(
                    types.InlineKeyboardButton(gift['name'],
                                               callback_data=f"delete_{gift['id']}")
                )
            bot.edit_message_text(
                "Выберите подарок для удаления:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )

    elif call.data.startswith("delete_"):
        gift_id = int(call.data.split("_")[1])
        data["gifts"] = [g for g in data["gifts"] if g["id"] != gift_id]
        save_data(data)
        bot.answer_callback_query(call.id, f"Подарок удален!")
        logging.info(f"Admin {user_id} deleted gift {gift_id}")

    elif call.data.startswith("unbook_"):
        gift_id = int(call.data.split("_")[1])
        user_id_str = str(user_id)
        for gift in data["gifts"]:
            if gift["id"] == gift_id and str(gift["booked_by"]) == user_id_str:
                gift["is_booked"] = False
                gift["booked_by"] = None
                save_data(data)
                bot.answer_callback_query(call.id, f"Бронь на {gift['name']} отменена!")
                bot.delete_message(call.message.chat.id, call.message.message_id)
                return
        bot.answer_callback_query(call.id, "Вы не можете отменить эту бронь.")

@bot.message_handler(commands=['skip'])
def skip_description(message):
    user_id = str(message.from_user.id)
    if add_gift_data.get(user_id, {}).get('step') == 'description':
        add_gift_data[user_id]['description'] = ""
        finalize_add(user_id)

def finalize_add(user_id):
    name = add_gift_data[user_id]['name']
    link = add_gift_data[user_id]['link']
    description = add_gift_data[user_id].get('description', "")

    data = load_data()
    new_id = max([g['id'] for g in data['gifts']], default=0) + 1
    data['gifts'].append({
        'id': new_id,
        'name': name,
        'link': link,
        'description': description,
        'is_booked': False,
        'booked_by': None
    })
    save_data(data)
    bot.send_message(
        user_id,
        f"Подарок '{name}' добавлен!"
    )
    del add_gift_data[user_id]

@bot.message_handler(commands=['cancel'])
def cancel_add(message):
    user_id = str(message.from_user.id)
    if user_id in add_gift_data:
        del add_gift_data[user_id]
        bot.send_message(message.chat.id, "Добавление подарка отменено.")

@bot.message_handler(commands=['allbookings'])
def all_bookings(message):
    data = load_data()
    booked = [g for g in data['gifts'] if g.get('is_booked')]
    if not booked:
        bot.send_message(message.chat.id, "Нет забронированных подарков.")
        return
    response = "Список бронирований:\n"
    for gift in booked:
        user = data['users'].get(str(gift['booked_by']), 'Неизвестно')
        response += f"- {gift['name']} (Забронировано: {user})\n"
    bot.send_message(message.chat.id, response)

bot.polling()