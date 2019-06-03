import os
import json
import datetime
from botocore.vendored import requests


BOT_URL = 'https://api.telegram.org/bot{}/'.format(os.environ['BOT_TOKEN'])

question_next_bus = '🏃🏻‍ Когда следующая развозка? 🏃🏼'
question_shedule_mon_thu = '🚐 Расписание понедельник-четверг 🚌'
question_shedule_fri = '🛸 Расписание пятница 🚀'
questionnaire = [
    [question_next_bus],
    [question_shedule_mon_thu],
    [question_shedule_fri]
]


def get_weekday(date_time: datetime.datetime):
    return date_time.isoweekday()


def convert_unixtime_to_datetime(unix_date: int) -> datetime.datetime:
    """
    Add (3600 * 2) for UTC+02:00 offset (Kyiv timezone)
    OR Add (3600 * 3) for UTC+02:00 offset (Kyiv timezone with summer-time)
    TODO: automatic summer-time detection
    """
    return datetime.datetime.utcfromtimestamp(unix_date + 3600 * 3)


def convert_str_to_datetime(str_time: str) -> datetime.datetime:
    now = datetime.datetime.utcnow()

    return datetime.datetime.strptime('{}:{}:{}:{}'.format(now.year, now.month, now.day, str_time), '%Y:%m:%d:%H:%M')


def get_schedule() -> dict:
    return json.loads(open('shedule.json').read())


def get_username(data: dict) -> str:
    if data['message']['from']['first_name']:
        return data['message']['from']['first_name']
    else:
        return data['message']['from']['username']


def welcome_reply(username: str) -> str:
    return 'Привет {}, просто выбери нужную опцию из списка 😀'.format(username)


def text_reply_shedule(friday: bool) -> str:
    schedule = get_schedule()
    text = ['🌝 Утренняя развозка:']
    key = 'friday' if friday else 'mon_thu'
        
    for time, description in schedule[key]['to'].items():
        text.append('{}  {}'.format(time, description))
    text.append('\n🌚 Вечерняя развозка:')
    for time, description in schedule[key]['from'].items():
        text.append('{}  {}'.format(time, description))

    return "\n".join(text)


def text_reply_next_bus(unix_time: int) -> str:
    shedule = get_schedule()
    timestamp = convert_unixtime_to_datetime(unix_time)
    weekday = get_weekday(timestamp)
    pre_text = '🚀 Следующая развозка:\n'
    weekends_answer = 'В понедельник в {} утра 🤷‍'.format(list(shedule['mon_thu']['to'].keys())[0])

    if weekday == 5:
        if timestamp < convert_str_to_datetime(list(shedule['friday']['to'].keys())[-1]):
            for time, description in shedule['friday']['to'].items():
                if timestamp < convert_str_to_datetime(time):
                    return '{}{}  {}'.format(pre_text, time, description)
        elif timestamp < convert_str_to_datetime(list(shedule['friday']['from'].keys())[-1]):
            for time, description in shedule['friday']['from'].items():
                if timestamp < convert_str_to_datetime(time):
                    return '{}{}  {}'.format(pre_text, time, description)
        else:
            return weekends_answer
    elif weekday <= 4:
        if timestamp < convert_str_to_datetime(list(shedule['mon_thu']['to'].keys())[-1]):
            for time, description in shedule['mon_thu']['to'].items():
                if timestamp < convert_str_to_datetime(time):
                    return '{}{}  {}'.format(pre_text, time, description)
        elif timestamp < convert_str_to_datetime(list(shedule['mon_thu']['from'].keys())[-1]):
            for time, description in shedule['mon_thu']['from'].items():
                if timestamp < convert_str_to_datetime(time):
                    return '{}{}  {}'.format(pre_text, time, description)
        else:
            if weekday == 4:
                return 'Завтра в {} утра 🤷‍'.format(list(shedule['friday']['to'].keys())[0])
            else:
                return 'Завтра в {} утра 🤷‍'.format(list(shedule['mon_thu']['to'].keys())[0])
    else:
        return weekends_answer


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
    elif '/start' in message_text:
        return send_message(welcome_reply(get_username(data)), chat_id)
    else:
        return send_message("Я тебя не понял, повтори ещё раз 🙄", chat_id)
