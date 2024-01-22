import random
import json


def check_greet(message):
    greet = ['привет', 'прив', 'приветствую', 'здравствуйте', 'здравствуй', 'йоу', 'hello', 'hi']
    for i in greet:
        if i in message.text.lower():
            return True


def check_bye(message):
    bye = ['пока', 'поки', 'до свидания', 'до встречи', 'бай']
    for i in bye:
        if i in message.text.lower():
            return True


def answering_any(message):
    if check_greet(message):
        # одно из привествий связано со временем
        import datetime

        def check_time():
            current_time = datetime.datetime.now().time()
            if current_time < datetime.time(12):
                return f'Доброе утро, {message.from_user.first_name}!'
            elif current_time < datetime.time(18):
                return f'Добрый день, {message.from_user.first_name}!'
            else:
                return f'Добрый вечер, {message.from_user.first_name}!'

        greet_time = check_time()
        bot_greets = ['Привет-привет!', f'Здравствуйте, {message.from_user.first_name}!', 'Приветики-пистолетики!',
                      f'Сердечно приветствую, {message.from_user.first_name}!',
                      f'Здравья желаю, товарищ, {message.from_user.first_name}!', greet_time, 'Салют!',
                      'Сколько лет, сколько зим!', 'Привет, собутыльники!', 'Привет вашему дому',
                      'Приветствую вас, Землянин!', 'Шалом', 'Просто здравствуй, просто как дела.',
                      'Здравствуйте. Меня зовут Иниго Монтойя.']
        msg = random.choice(bot_greets)
    elif check_bye(message):
        msg = (f'До встречи, {message.from_user.first_name}! Если захотите еще раз услышать об интересных людях, '
               f'я всегда к вашим услугам.')
    else:
        msg = ('К сожалению, на языке Вселенной нельзя выразить то, что вы сейчас сказали. Во избежание недопонимания '
               'со Cмотрителем я не буду это переводить.\n\n Пожалуйста, загляните в /help справочник.')
    return msg


def load_from_json():
    # noinspection PyBroadException
    try:
        with open('user_data.json', 'r+', encoding='utf8') as f:
            data = json.load(f)
    except Exception:
        data = {}

    return data


def save_to_json():
    with open('user_data.json', 'w', encoding='utf8') as f:
        json.dump(user_data, f, indent=2)


user_data = load_from_json()


def count(location, user_id):
    load_from_json()
    alts = user_data[user_id]['alts']
    if location in ['wake_up', 'move_right_lose', 'evade_lose', 'lift_lose', 'wolves_lose']:
        alts = 0
    else:
        plus = {'stairs': 200, 'baby_mate': 150,
                'near_lift': 100, 'run_away': 20,
                'bit_first': 70, 'normal_taxi': -50,
                'sleep_taxi_win': -1500050, 'credit_with_win': -50000}
        if location in plus.keys():
            alts += plus[location]
    return alts
