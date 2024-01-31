import telebot
import sqlite3

bot = telebot.TeleBot('TOKEN')

connect = sqlite3.connect('kursova/food.db', check_same_thread=False)
cursor = connect.cursor()

def products_list_update():
    global products_list
    cursor.execute("SELECT product FROM ingredients;")
    products_list = cursor.fetchall()
    products_list = [x[0].lower() for x in products_list]

products_list_update()
counter = False
change_values = False
add_product = False

def valid(user_list):
    if len(user_list) %2 != 0:
        return False
    try:
        str("".join(user_list[::2]))
        int("".join(user_list[::-2]))
    except:
        return False
    return True

@bot.message_handler(commands=['start'])
def start(message):    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = telebot.types.KeyboardButton('🧮 Підрахунок')
    item2 = telebot.types.KeyboardButton('🍏 Продукти')
    markup.add(item1,item2)
    bot.send_message(message.chat.id, 'Це бот для підрахунку харчової цінності. Виберіть розділ', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def bot_message(message):
    global counter
    global products
    global change_values
    global add_product

    if message.text == '🧮 Підрахунок':
        counter = True
        #buttons
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = telebot.types.KeyboardButton('◀ Назад')
        markup.add(item1)
        bot.send_message(message.chat.id, "Введіть продукти ['Назва' 'вага(г)']", reply_markup=markup)
    
    elif message.text == '🍏 Продукти':
        products = True

        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = telebot.types.KeyboardButton('📝 Додати продукт')
        item2 = telebot.types.KeyboardButton('◀ Назад')
        markup.add(item1,item2)
        bot.send_message(message.chat.id, "Для пошуку введіть назву або виберіть розділ", reply_markup=markup)
    
    elif message.text == '◀ Назад':
        counter = False

        if change_values == True:
            change_values = False

            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = telebot.types.KeyboardButton('◀ Назад')
            markup.add(item1)
            bot.send_message(message.chat.id, "Для пошуку введіть назву або виберіть розділ", reply_markup=markup)
        
        elif add_product == True:
            add_product = False

            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = telebot.types.KeyboardButton('◀ Назад')
            markup.add(item1)
            bot.send_message(message.chat.id, "Для пошуку введіть назву або виберіть розділ", reply_markup=markup)
        else:
            products = False
            
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = telebot.types.KeyboardButton('🧮 Підрахунок')
            item2 = telebot.types.KeyboardButton('🍏 Продукти')
            markup.add(item1,item2)
            bot.send_message(message.chat.id, '◀ Назад', reply_markup=markup)
    
    elif counter == True:
        extraprod = []
        user_list = list(message.text.lower().split())

        if valid(user_list) == True:
            for prod in user_list[::2]:
                if prod not in products_list:
                    extraprod.append(prod)
        
            if len(extraprod) == 0:
                user_list = list(zip(user_list[::2], user_list[::-2][::-1]))
                finlist = []
                finnum = [0,0,0,0]
                for prod,weight in user_list:
                    cursor.execute(f"""SELECT 
                        `product`,
                        `proteins_g`/100*{int(weight)},
                        `fats_g`/100*{int(weight)},
                        `carbs_g`/100*{int(weight)},
                        `kcal`/100*{int(weight)} 
                        FROM ingredients WHERE product="{prod.capitalize()}";
                    """)
                    for x in cursor.fetchall():
                        finlist.append(x)
                for prod,prot,fat,carb,kcal in finlist:
                    finnum[0] = finnum[0] + float(prot)
                    finnum[1] = finnum[1] + float(fat)
                    finnum[2] = finnum[2] + float(carb)
                    finnum[3] = finnum[3] + int(kcal)
                finnum = [round(x,2) for x in finnum]
                bot.send_message(message.chat.id, f'Білок: {finnum[0]}г\nЖири: {finnum[1]}г\nВуглеводи: {finnum[2]}г\nКкал: {finnum[3]}')
            elif len(extraprod) > 0:
                extraprod = '\n'.join(extraprod)
                bot.send_message(message.chat.id, f'В базі даних таких продуктів немає:\n`{extraprod}`', parse_mode="MARKDOWN")
        else:
            bot.send_message(message.chat.id, 'Некоректна форма!')
    
    elif products == True:
        if message.text == '📝 Додати продукт':
            add_product = True
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = telebot.types.KeyboardButton('◀ Назад')
            markup.add(item1)
            bot.send_message(message.chat.id, "Введіть дані для нового запису\n ['Назва' 'Білки' 'Жири' 'Вуглеводи' 'Ккал']", reply_markup=markup)

        elif message.text != '✏ Змінити дані' and message.text != '🗑 Видалити запис' and change_values != True and add_product != True:
            if message.text.lower() in products_list:
                cursor.execute(f"""SELECT *
                    FROM ingredients WHERE product="{message.text.capitalize()}";
                """)
                product = cursor.fetchall()[0]
                global productname
                productname = product[0]
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                item1 = telebot.types.KeyboardButton('✏ Змінити дані')
                item2 = telebot.types.KeyboardButton('🗑 Видалити запис')
                item3 = telebot.types.KeyboardButton('◀ Назад')
                markup.add(item1, item2, item3)
                bot.send_message(message.chat.id, f"{product[0]} (на 100г):\n Білків: {product[1]}г\n Жирів: {product[2]}г\n Вуглеводів: {product[3]}г\n Ккал: {product[4]}", reply_markup=markup)
            else:
                bot.send_message(message.chat.id, 'Такого продукту немає!')
        
        elif message.text == '🗑 Видалити запис':
            cursor.execute(f'DELETE FROM ingredients WHERE product="{productname}"')
            connect.commit()
            products_list_update()
            bot.send_message(message.chat.id, 'Запис видалено!')
        
        elif message.text == '✏ Змінити дані':
            change_values = True
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = telebot.types.KeyboardButton('◀ Назад')
            markup.add(item1)
            bot.send_message(message.chat.id, f"Введіть нові дані для '{productname} (на 100г продукту)'\n ['Назва' 'Білки' 'Жири' 'Вуглеводи' 'Ккал']", reply_markup=markup)
        
        elif change_values == True:
            if len(message.text.split()) == 5:
                new_list = message.text.split()
                try:
                    str(new_list[0])
                    float(new_list[1])
                    float(new_list[2])
                    float(new_list[3])
                    float(new_list[4])
                except:
                    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                    item1 = telebot.types.KeyboardButton('◀ Назад')
                    markup.add(item1)
                    bot.send_message(message.chat.id, 'Некоректна форма!', reply_markup=markup)
                else:
                    cursor.execute(f"""UPDATE ingredients SET
                        product = "{new_list[0].capitalize()}",
                        proteins_g = {new_list[1]},
                        fats_g = {new_list[2]},
                        carbs_g = {new_list[3]},
                        kcal = {new_list[4]}
                        WHERE product="{productname.capitalize()}";
                    """)
                    connect.commit()
                    products_list_update()
                    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                    item1 = telebot.types.KeyboardButton('◀ Назад')
                    markup.add(item1)
                    bot.send_message(message.chat.id, 'Дані змінено!', reply_markup=markup)
                    change_values = False
            else:
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                item1 = telebot.types.KeyboardButton('◀ Назад')
                markup.add(item1)
                bot.send_message(message.chat.id, 'Некоректна форма!', reply_markup=markup)
        
        elif add_product == True:
            if len(message.text.split()) == 5 and message.text.split()[0].lower() not in products_list:
                new_list = message.text.split()
                try:
                    str(new_list[0])
                    float(new_list[1])
                    float(new_list[2])
                    float(new_list[3])
                    float(new_list[4])
                except:
                    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                    item1 = telebot.types.KeyboardButton('◀ Назад')
                    markup.add(item1)
                    bot.send_message(message.chat.id, 'Некоректна форма!', reply_markup=markup)
                else:
                    cursor.execute(f"""INSERT INTO ingredients VALUES(
                        '{new_list[0].capitalize()}',
                        {new_list[1]},
                        {new_list[2]},
                        {new_list[3]},
                        {new_list[4]}
                    );""")
                    connect.commit()
                    products_list_update()
                    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                    item1 = telebot.types.KeyboardButton('◀ Назад')
                    markup.add(item1)
                    bot.send_message(message.chat.id, 'Запис створено!', reply_markup=markup)
            else:
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                item1 = telebot.types.KeyboardButton('◀ Назад')
                markup.add(item1)
                bot.send_message(message.chat.id, 'Некоректна форма або продукт вже існує!', reply_markup=markup)

    else:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = telebot.types.KeyboardButton('🧮 Підрахунок')
        item2 = telebot.types.KeyboardButton('🍏 Продукти')
        markup.add(item1,item2)
        bot.send_message(message.chat.id, 'Виберіть розділ!', reply_markup=markup)

bot.polling(non_stop=True)
