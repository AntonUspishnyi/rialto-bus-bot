import functools
import logging
import os
from datetime import datetime, time

import telebot
import yaml
from dateutil import tz
from telebot import types


bot = telebot.TeleBot(os.environ["BOT_TOKEN"], threaded=False)
TZ = tz.gettz(os.environ["BOT_TIMEZONE"])

# Define buttons for main markup
button_next_bus = "When's the next bus?"
button_today_schedule = "Today's schedule"
button_complete_schedule = "Show the complete schedule for..."


# Lambda main handler
def handler(event, context) -> dict:
    try:
        update = telebot.types.Update.de_json(event["body"])
        if update.message:
            bot.process_new_messages([update.message])
        return {"statusCode": 200, "body": "OK"}

    except Exception as e:
        logging.exception(f"{e}\nEvent body: {event}", exc_info=True)
        return {"statusCode": 500, "body": "Internal Server Error"}


# Handle "/start" command
@bot.message_handler(commands=["start"])
def send_welcome(message) -> None:
    bot.send_message(
        message.chat.id,
        f"Hi {get_username(message.from_user)}, here are all available commands👇",
        reply_markup=main_markup(),
    )


# Reply when's the next bus
@bot.message_handler(func=lambda message: message.text == button_next_bus)
def send_next_bus(message) -> None:
    answer = get_next_bus_answer(current_datetime(), load_schedule())
    bot.send_message(message.chat.id, answer, parse_mode="HTML", reply_markup=main_markup())


# Reply with schedule for today or any other specified day
@bot.message_handler(func=lambda message: message.text == button_today_schedule)
@bot.message_handler(func=lambda message: message.text in load_schedule())
def send_day_schedule(message) -> None:
    day = get_weekday(current_datetime()) if message.text == button_today_schedule else message.text
    schedule = format_schedule(day, get_schedule_for(day))
    bot.send_message(message.chat.id, schedule, parse_mode="HTML", reply_markup=main_markup())


# Reply with markup with all days from schedule (to choose one day from all available)
@bot.message_handler(func=lambda message: message.text == button_complete_schedule)
def send_choose_day(message) -> None:
    bot.send_message(message.chat.id, "Choose the day!", reply_markup=schedule_markup())


# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=["text"])
def send_re_ask(message) -> None:
    bot.reply_to(
        message,
        f"Sorry, {get_username(message.from_user)}, I don't understand you 🤔\nCheck available buttons.",
        reply_markup=main_markup(),
    )


def build_markup(buttons: list) -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for button in buttons:
        markup.add(types.KeyboardButton(button))
    return markup


def main_markup() -> types.ReplyKeyboardMarkup:
    return build_markup([button_next_bus, button_today_schedule, button_complete_schedule])


def schedule_markup() -> types.ReplyKeyboardMarkup:
    return build_markup([day for day in load_schedule()])


def get_username(from_user: types.User) -> str:
    return from_user.first_name or from_user.username


@functools.lru_cache()
def load_schedule(path: str = "./schedule.yaml") -> dict:
    with open(path) as file:
        schedule = yaml.safe_load(file)
    return {
        k: dict(sorted(v.items(), key=lambda x: time.fromisoformat(x[0])))
        for k, v in schedule.items()
    }


def current_datetime() -> datetime:
    return datetime.now(TZ)


def get_weekday(dt: datetime) -> str:
    return dt.strftime("%A")


def get_schedule_for(weekday: str) -> dict:
    schedule = load_schedule().get(weekday, {})

    # Swap time and description for future formatting
    schedule_swapped = {}
    for time, description in schedule.items():
        schedule_swapped.setdefault(description, []).append(time)
    return schedule_swapped


def format_schedule(weekday: str, schedule: dict) -> str:
    if not schedule:
        return f"Could not find schedule for {weekday} ☹️"

    schedule_list = []
    for description, time_list in schedule.items():
        schedule_list.append(f"\n{description}:" if schedule_list else f"{description}:")
        schedule_list.append("\n".join(f"<code>{t}</code>" for t in time_list))
    return "\n".join(schedule_list)


def get_next_bus_answer(dt: datetime, schedule: dict) -> str:
    today_schedule = schedule.get(get_weekday(dt))
    if not today_schedule:
        return "There are no buses today ☹️"

    next_bus = calculate_delta(dt, today_schedule)
    if not next_bus:
        return "There are no more buses today ☹️"

    return format_next_bus_answer(next_bus)


def calculate_delta(dt: datetime, schedule: dict) -> dict:
    # Find the first timestamp from list bigger then now and return delta, str_time, description
    for each in list(schedule.items()):
        schedule_time = convert_isotime_to_datetime(dt, each[0])
        if dt < schedule_time:
            return {"delta": schedule_time - dt, "str_time": each[0], "description": each[1]}
    return {}


def convert_isotime_to_datetime(dt: datetime, isotime: str) -> datetime:
    isotime = time.fromisoformat(isotime)
    converted = dt.replace(hour=isotime.hour, minute=isotime.minute)
    return converted


def format_next_bus_answer(data: dict) -> str:
    delta = data["delta"].seconds
    forecast = None
    if delta < 60:
        forecast = "less than a minute"
    elif delta > 3600:
        forecast = "more than an hour"
    else:
        forecast = f"{delta//60} minutes"

    return f"It's <b>{forecast}</b> to the next bus:\n\n{data['description']} at <b>{data['str_time']}</b>"
