# Бунин Николай, 21 группа
# ----------------------------------------------------ИМПОРТЫ-----------------------------------------------------------
import json
import telebot
import os
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, BotCommand, BotCommandScope
from other_funcs import answering_any, count
import time
load_dotenv()
token = os.getenv('TOKEN')
bot = telebot.TeleBot(token=token)


# ------------------------------------------------------JSON------------------------------------------------------------
def save_to_json():
    with open('user_data.json', 'w', encoding='utf8') as f:
        json.dump(user_data, f, indent=2)


def load_from_json():
    # noinspection PyBroadException
    try:
        with open('user_data.json', 'r+', encoding='utf8') as f:
            data = json.load(f)
    except Exception:
        data = {}

    return data


user_data = load_from_json()
with open('locations.json', 'r', encoding='utf8') as file:
    locations = json.load(file)

with open('plot.json', 'r', encoding='utf8') as file:
    plot = json.load(file)


# ----------------------------------------------------ЗАПУСК------------------------------------------------------------
@bot.message_handler(commands=['start'])
def start(message):
    c_id = message.chat.id
    load_from_json()
    user_name = message.from_user.first_name
    user_id = str(message.from_user.id)
    if user_id not in user_data:  # проверка регистрации пользователя
        user_data[user_id] = {"alts": 0, 'show_alts': False, 'name': user_name}
        commands = [  # Установка списка команд с областью видимости и описанием
            BotCommand('start', 'перезапустить бота'),
            BotCommand('help', 'узнайте о доступных командах'),
            BotCommand('show_stat', 'ваш баланс')
        ]

        bot.set_my_commands(commands)
        BotCommandScope('private', chat_id=c_id)
    user_data[user_id]['alts'] = 0
    save_to_json()

    # вывод приветственного сообщения
    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Начать игру!', callback_data='start'))
    pic = 'https://postimg.cc/mc07Y5dK'
    msg = bot.send_photo(c_id, pic, f'Здравствуй, {message.from_user.first_name}!\n '
                         'Я Cмотритель этой Вселенной. У меня есть друг-робот и, кажется, '
                         'он ищет добровольцев для участия в испытании его новой технологии, '
                         'с помощью которой Вам придется управлять другим человеком.\n\n'
                         'Если готовы начать, смело жмите на кнопку.\n А если хотите конструктивно со мной поговорить, '
                         'то заглядывайте в /help',
                         reply_markup=keyboard)

    # сделано, чтобы было только одно сообщение с квестом и нельзя было проходить два одновременно
    ms_id = msg.message_id
    try:
        bot.delete_message(chat_id=c_id, message_id=(user_data[user_id]['ms_id_quest']))
    except (KeyError, telebot.apihelper.ApiTelegramException):
        pass
    user_data[user_id]['ms_id_quest'] = ms_id
    save_to_json()


# ----------------------------------------------------ЛОГИКА------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: True)
def game_logic(call):  # т.к. кнопки только инлайн, вся реализация квеста находится здесь
    load_from_json()
    user_name = call.from_user.first_name
    user_id = str(call.from_user.id)
    if user_id not in user_data:  # проверка регистрации пользователя (на случай, если файл user_data удален)
        user_data[user_id] = {"alts": 0, 'show_alts': False, 'name': user_name}
        save_to_json()

    ms_id = call.message.message_id
    c_id = call.message.chat.id
    # ------------------------------------------------СООБЩЕНИЯ В ЧАТЕ--------------------------------------------------
    if call.data == 'explain':  # смотри в функции answer_all()
        bot.edit_message_text(chat_id=c_id, message_id=ms_id, text='"Меня зовут Иниго Монтойя и я несу '
                                                                   'возмездие во имя Луны! Ты убил моего отца.'
                                                                   ' Приготовься умереть!" - Это общая фраза, '
                                                                   'подразумевающая, что говорящий зол на '
                                                                   'своего собеседника и готов к драке с ним.\n\n'
                                                                   'Что-то похожее '
                                                                   'злодеи часто говорят героям или наоборот, '
                                                                   'перед тем как начать драться. '
                                                                   'Так, когда они представляются, то '
                                                                   'якобы создают себе грозную репутацию, '
                                                                   'возвышают свою персону. ')
        return
    if call.data == 'upload':
        stats = (f'Текущий баланс - {user_data[user_id]["alts"]} альтов.\n\n'
                 f'Максимальный итоговый баланс - 250 альтов')

        if call.message.text == stats:
            new_stats = stats + '\n\n Ваш баланс не изменился'
            keyboard = None
            bot.edit_message_text(chat_id=c_id, message_id=ms_id, text=new_stats, reply_markup=keyboard)
            time.sleep(2)
        keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Обновить', callback_data='upload'))
        bot.edit_message_text(chat_id=c_id, message_id=ms_id, text=stats, reply_markup=keyboard)
        return
    # ----------------------------------------------СООБЩЕНИЯ РОБОТА----------------------------------------------------
    if call.data == 'start':
        captions = {'cap1': 'Связываюсь с  роботом...',
                    'cap2': 'Вычисляю...',
                    'cap3': f'Ах да, это вы, {call.from_user.first_name}. Буду очень признателен, '
                            f'если вы поможете мне кое с чем.'}
        for key, cap in captions.items():
            keyboard = None
            if key == 'cap2':
                time.sleep(2)
                pic = "https://postimg.cc/ftSCzys6"
                bot.edit_message_media(chat_id=c_id, message_id=ms_id, media=InputMediaPhoto(pic))
            if key == 'cap3':
                time.sleep(1.5)
                keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text='С чем?', callback_data='question'))
            bot.edit_message_caption(message_id=ms_id, chat_id=c_id, caption=cap, reply_markup=keyboard)
        return

    elif call.data == 'question':
        keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Подключиться к технологии ',
                                                                   callback_data='darkness'))
        bot.edit_message_caption(chat_id=c_id, message_id=ms_id,
                                 caption='Я нашел для вас не самый обычный мир и человека, '
                                         'с которым вот-вот что-то случится. Ваша задача - помочь ему справиться '
                                         'с предстоящими трудностями и благополучно добраться до места назначения. '
                                         'Сложность заключается в том, что, если умрёт тот, '
                                         'кем вы управляете, умрете и вы.\n Кстати, в этом мире есть денежная система. '
                                         'Пожалуйста, постарайтесь не уйти в минус!\n'
                                         'Советую во время прохождения использовать /show_stat,'
                                         ' чтобы всегда знать свой баланс. \n\n'
                                         'Важно: ваш денежный результат обнулится, если вы не выживите.',
                                 reply_markup=keyboard)

    # --------------------------------------------------КВЕСТ-----------------------------------------------------------
    else:
        if call.data == 'darkness':  # начало квеста
            user_data[user_id]["alts"] = 0
            bot.edit_message_caption(chat_id=c_id, message_id=ms_id, caption='Отлично! Начало через...',
                                     reply_markup=None)

            time.sleep(1.5)

            for num in range(3, 0, -1):  # отсчет, реализация через time
                bot.edit_message_caption(caption=f'{num}',
                                         chat_id=c_id, message_id=ms_id)
                time.sleep(1)

        current_location = call.data  # получаем локацию пользователя
        user_data[user_id]['current_location'] = current_location
        # --------------------------------------------------------------------------------------------------------------
        num_alts = user_data[user_id]["alts"]
        alts = count(current_location, num_alts)  # расчет баланса
        user_data[user_id]["alts"] = alts

        text = plot[current_location]['text']  # контент хранится в словаре plot
        pic = plot[current_location]['pic']  # контент хранится в словаре plot

        # если квест завершен, появится кнопка с предложением начать сначала
        if current_location in ['bath_lose', 'evade_lose', 'lift_lose', 'talk_to_driver_win', "move_left_win",
                                "move_right_lose", 'credit_with_win', 'wolves_lose', 'sleep_taxi_win']:
            btn = InlineKeyboardButton(text='Начать с первого выбора', callback_data='wake_up')
            keyboard = InlineKeyboardMarkup().add(btn)

        else:  # кнопки остальных локаций хранятся в словаре locations и выводятся исходя из локации
            keyboard = InlineKeyboardMarkup()
            for answer, next_location in locations[current_location].items():  # находим кнопки по локации-ключу
                keyboard.add(InlineKeyboardButton(text=answer, callback_data=next_location))

        bot.edit_message_media(chat_id=c_id, message_id=ms_id, media=InputMediaPhoto(pic))
        bot.edit_message_caption(caption=text, chat_id=c_id, message_id=ms_id, reply_markup=keyboard)
        save_to_json()


# ----------------------------------------------------ФУНКЦИИ-----------------------------------------------------------
@bot.message_handler(commands=['help'])
def about(message):
    text = ('Что-ж, человеческий язык настолько сложен, '
            'что даже сама бесконечная Вселенная может понять лишь небольшую его часть. '
            'Вам повезло! Здесь представлен справочник слов и выражений для конструктивного общения с самой Вселенной!'
            '\n\n Справка:\n\n'
            '/start - начнет квест с диалога со смотрителем\n\n'
            '/help - направит вас сюда\n\n'
            '/show_stat - покажет ваш текущий баланс и максимально возможный (то есть при лучшей концовкe!)\n'
            'Как только увидите в квесте что-то про деньги, '
            'можете нажать кнопку "обновить" и ваш баланс изменится.\n\n'
            'Так как Cмотрителю по непонятным причинам нравится здороваться со всеми, при чем фразами, '
            'характерными для того вида существ, с которым он ведет диалог, '
            'то вас он при желании может поприветствовать более чем десятью способами.\n\n'
            'Попрощаться он тоже может, но в этом случае его словарный запас невелик.')
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['show_stat'])
def show_statistics(message):
    load_from_json()
    user_name = message.from_user.first_name
    user_id = str(message.from_user.id)
    c_id = message.chat.id
    if user_id not in user_data:  # проверка регистрации пользователя (на случай, если файл user_data удален)
        user_data[user_id] = {"alts": 0, 'show_alts': False, 'name': user_name}
        save_to_json()

    stats = (f'Текущий баланс - {user_data[user_id]["alts"]} альтов.\n\n'
             f'Максимальный итоговый баланс - 250 альтов')
    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Обновить', callback_data='upload'))
    msg = bot.send_message(c_id, stats, reply_markup=keyboard)
    ms_id = msg.message_id
    try:
        bot.delete_message(chat_id=c_id, message_id=(user_data[user_id]['ms_id_stats']))
    except (KeyError, telebot.apihelper.ApiTelegramException):
        pass
    user_data[user_id]['ms_id_stats'] = ms_id
    save_to_json()


@bot.message_handler(content_types=['text', 'audio', 'video', 'document', 'voice', 'photo'])
def answer_all(message):
    msg = answering_any(message)
    keyboard = None
    if msg == 'Здравствуйте. Меня зовут Иниго Монтойя.':
        keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Объясни!", callback_data='explain'))
    bot.send_message(message.chat.id, msg, reply_markup=keyboard)


bot.infinity_polling()
