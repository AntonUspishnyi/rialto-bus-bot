import os
import json
import pytz
import schedule
from datetime import datetime
from botocore.vendored import requests

BOT_URL = 'https://api.telegram.org/bot{}/'.format(os.environ['BOT_TOKEN'])

question_next_bus = '🏃🏻‍ Когда следующая развозка? 🏃🏼'
question_shedule_mon_thu = '🚐 Расписание понедельник-четверг 🚌'
question_shedule_fri = '🛸 Расписание пятница 🚀'
question_lunch_bus = '🍝 Расписание ланч-автобусов 🌭'
questionnaire = [
    [question_next_bus],
    [question_shedule_mon_thu],
    [question_shedule_fri],
    [question_lunch_bus]
]

def get_username(data: dict) -> str:
    if data['message']['from']['first_name']:
        return data['message']['from']['first_name']
    else:
        return data['message']['from']['username']


def welcome_reply(username: str) -> str:
    return 'Привет {}, просто выбери нужную опцию из списка 😀'.format(username)


def text_reply_shedule(friday: bool) -> str:
    text = ['🌝 Утренняя развозка:']
    key = 'friday' if friday else 'mon_thu'
        
    for time, description in schedule.times[key].items():
        text.append('{}  {}'.format(time, description))
        if time == '11:05':
            text.append('\n🌚 Вечерняя развозка:')

    return "\n".join(text)


def text_reply_lunch_bus() -> str:
    text = ['🍔 Ланч-автобусы:']
    for description, time in schedule.lunch.items():
        text.append(f'{time}  {description}')

    return "\n".join(text)


def text_reply_next_bus(unix_time: int) -> str:
    pre_text = '🚀 Следующая развозка:\n'
    tz = pytz.timezone('Europe/Kiev')
    dt = datetime.fromtimestamp(unix_time, tz)

    # weekday(): Monday is 0 and Sunday is 6
    if dt.weekday() > 4:
        return schedule.next_day_texts['friday']
    elif dt.weekday() == 4:
        key = 'friday'
    else:
        key = 'mon_thu'

    for n in list(schedule.times[key].keys()):
        hrs, mnts = (int(x) for x in n.split(':'))
        if dt.hour < hrs or (dt.hour == hrs and dt.minute < mnts):
            return '{}{}  {}'.format(pre_text, n, schedule.times[key][n])

    # To get next morning time for Monday, Tuesday, Wednesday
    if dt.weekday() < 3:
        key = 'friday'

    return schedule.next_day_texts[key]


def get_send_message_url() -> str:
    return BOT_URL + 'sendMessage'


def get_keyboard_markup(question_array: list) -> dict:
    return {
        'keyboard': question_array,
        'resize_keyboard': True,
        'one_time_keyboard': True
    }


def send_message(text: str, chat_id: int):
    params = {
        'text': text,
        'chat_id': str(chat_id),
        'reply_markup': json.dumps(get_keyboard_markup(questionnaire))
    }
    requests.get(get_send_message_url(), params=params)


def run(data: dict):
    chat_id = data['message']['chat']['id']
    message_date = data['message']['date']
    message_text = data['message']['text']
    
    if question_next_bus in message_text or '/1' in message_text:
        return send_message(text_reply_next_bus(message_date), chat_id)

    elif question_shedule_mon_thu in message_text or '/2' in message_text:
        return send_message(text_reply_shedule(friday=False), chat_id)

    elif question_shedule_fri in message_text or '/3' in message_text:
        return send_message(text_reply_shedule(friday=True), chat_id)

    elif question_lunch_bus in message_text or '/4' in message_text:
        return send_message(text_reply_lunch_bus(), chat_id)

    elif '/start' in message_text:
        return send_message(welcome_reply(get_username(data)), chat_id)

    else:
        return send_message("Я тебя не понял, повтори ещё раз 🙄", chat_id)
