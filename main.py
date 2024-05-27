import telebot
from telebot import types
import random
import uuid
import time


def read_categories(file_path):
    with open(file_path, 'r') as file:
        categories = [line.strip() for line in file.readlines()]
    return categories


def read_products(category, subcategory):
    file_path = f"{category.lower()}.{subcategory.lower()}.txt"
    with open(file_path, 'r') as file:
        products = [line.strip() for line in file.readlines()]
    return products


def write_order_to_file(user_id):
    order_data = user_data_dict[user_id]
    category = order_data['category']
    subcategory = order_data['subcategory']
    product = order_data['product']
    order_number = order_data['order_number']
    delivery_method = order_data['delivery_method']

    file_path = 'orders.txt'

    with open(file_path, 'a') as file:
        file.write(f"User ID: {user_id}\n"
                   f"Order Number: {order_number}\n"
                   f"Category: {category}\n"
                   f"Subcategory: {subcategory}\n"
                   f"Product and price: {product}\n"
                   f"Delivery Method: {delivery_method}\n"
                   f"Order Status: {order_data['order_status']['status']}\n\n")


bot = telebot.TeleBot('6494685813:AAGPTcoHj2WDaHpkF5mbfkwehOo_u9aTL8Q')

user_data_dict = {}


@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("clothing")
    markup.add(item)
    item1 = types.KeyboardButton("book")
    markup.add(item1)
    item3 = types.KeyboardButton("laptop")
    markup.add(item3)
    bot.reply_to(message, f"Привіт, {user.first_name}! Я твій чат-бот для замовлень. Вибери категорію: ",
                 reply_markup=markup)


def generate_order_number():
    return str(uuid.uuid4())


@bot.message_handler(func=lambda message: message.text == "clothing" or message.text == "book" or message.text == "laptop")
def choose_category(message):
    category = message.text
    subcategories = read_categories(f"{category.lower()}.subcategoria.txt")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for subcategory in subcategories:
        item = types.KeyboardButton(subcategory)
        markup.add(item)
    bot.reply_to(message, "Вибери підкатегорію:", reply_markup=markup)
    user_data_dict[message.from_user.id] = {'category': category}


@bot.callback_query_handler(func=lambda call: call.data == 'add_product')
def add_another_product_callback(call):
    user_id = call.from_user.id
    category = user_data_dict[user_id]['category']
    subcategory = user_data_dict[user_id]['subcategory']
    show_products(user_id, category, subcategory)


@bot.message_handler(func=lambda message: message.from_user.id in user_data_dict and 'category' in user_data_dict[message.from_user.id] and message.text.lower() == 'назад')
def go_back(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("clothing")
    markup.add(item)
    item1 = types.KeyboardButton("book")
    markup.add(item1)
    item3 = types.KeyboardButton("laptop")
    markup.add(item3)
    bot.send_message(message.from_user.id, "Обери категорію:", reply_markup=markup)
    del user_data_dict[message.from_user.id]['category']


@bot.message_handler(func=lambda message: message.from_user.id in user_data_dict and 'category' in user_data_dict[message.from_user.id] and message.text.lower() in read_categories(f"{user_data_dict[message.from_user.id]['category'].lower()}.subcategoria.txt"))
def choose_subcategory(message):
    subcategory = message.text
    category = user_data_dict[message.from_user.id]['category']
    if category == 'clothing' and subcategory == 'outerwear':
        show_subcategories(message.from_user.id, subcategory)
    else:
        show_products(message.from_user.id, category, subcategory)


def show_subcategories(user_id, subcategory):
    subcategories_outerwear = read_categories('clothing.outerwear.txt')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for subcat_outerwear in subcategories_outerwear:
        item = types.KeyboardButton(subcat_outerwear)
        markup.add(item)
    back_button = types.KeyboardButton('назад')
    markup.add(back_button)
    bot.send_message(user_id, "Вибери підкатегорію:", reply_markup=markup)
    user_data_dict[user_id]['subcategory'] = subcategory


def show_products(user_id, category, subcategory):
    products = read_products(category, subcategory)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for product in products:
        item = types.KeyboardButton(product)
        markup.add(item)
    back_button = types.KeyboardButton('назад')
    markup.add(back_button)
    bot.send_message(user_id, "Вибери товар:", reply_markup=markup)
    user_data_dict[user_id]['subcategory'] = subcategory


@bot.message_handler(func=lambda message: message.from_user.id in user_data_dict and 'subcategory' in user_data_dict[message.from_user.id] and message.text in read_products(user_data_dict[message.from_user.id].get('category', ''), user_data_dict[message.from_user.id]['subcategory']))
def choose_product(message):
    user_id = message.from_user.id

    if user_id in user_data_dict and 'category' in user_data_dict[user_id]:
        product = message.text
        bot.reply_to(message, f"Ти вибрав(ла) товар: {product}.")

        order_number = generate_order_number()

        user_data_dict[user_id]['product'] = product
        user_data_dict[user_id]['order_number'] = order_number
        user_data_dict[user_id]['delivery_method'] = None

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        courier_button = types.InlineKeyboardButton(text="Кур'єр", callback_data="courier")
        pickup_button = types.InlineKeyboardButton(text="Самовивіз", callback_data="pickup")
        add_product_button = types.InlineKeyboardButton(text="Змініть товар", callback_data="add_product")
        keyboard.add(courier_button, pickup_button, add_product_button)

        bot.send_message(user_id, "Вибери спосіб доставки або змініть товар:", reply_markup=keyboard)
    else:
        bot.send_message(user_id, "Щось пішло не так. Будь ласка, спробуйте знову.")



@bot.callback_query_handler(func=lambda call: call.data in ['courier', 'pickup'])
def choose_delivery_method(call):
    delivery_option = call.data
    user_id = call.from_user.id
    product = user_data_dict[user_id]['product']
    order_number = user_data_dict[user_id]['order_number']

    if delivery_option == 'courier':
        delivery_method = 'courier'
    elif delivery_option == 'pickup':
        delivery_method = 'pickup'

    bot.send_message(user_id, f"Дякуємо за замовлення товару: {product}. "
                              f"Ваше замовлення з номером {order_number} у стані обробки. "
                              f"Спосіб доставки: {delivery_method}.")

    user_data_dict[user_id]['delivery_method'] = delivery_method

    order_status = {'status': 'Processing', 'delivery_method': delivery_method, 'order_number': order_number}
    user_data_dict[user_id]['order_status'] = order_status

    time.sleep(10)
    update_order_status(user_id, 'In the way')

    time.sleep(15)
    update_order_status(user_id, 'Delivered')

    write_order_to_file(user_id)


def update_order_status(user_id, new_status):
    order_number = user_data_dict[user_id]['order_number']

    if new_status == 'Processing':
        bot.send_message(user_id, "Ваше замовлення обробляється.")
    elif new_status == 'In the way':
        bot.send_message(user_id, f"Ваше замовлення в дорозі.")
    elif new_status == 'Delivered':
        bot.send_message(user_id, "Ваше замовлення доставлено. Дякуємо за покупку!")

    user_data_dict[user_id]['order_status']['status'] = new_status
    bot.send_message(user_id, f"Стан замовлення {order_number} оновлено: {new_status}.")


@bot.message_handler(commands=['status'])
def check_order_status(message):
    user_id = message.from_user.id
    if user_id in user_data_dict and 'order_status' in user_data_dict[user_id]:
        order_status = user_data_dict[user_id]['order_status']['status']
        if 'category' in user_data_dict[user_id] and 'subcategory' in user_data_dict[user_id]:
            category = user_data_dict[user_id]['category']
            subcategory = user_data_dict[user_id]['subcategory']
            bot.send_message(user_id, f"Статус вашого замовлення в категорії '{category}', підкатегорії '{subcategory}': {order_status}.")
        else:
            bot.send_message(user_id, f"Статус вашого замовлення: {order_status}.")
    else:
        bot.send_message(user_id, "Ви ще не зробили замовлення. Зробіть замовлення спочатку.")




bot.polling()
