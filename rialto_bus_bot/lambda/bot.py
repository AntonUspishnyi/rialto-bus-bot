import datetime
import logging
import os

import pytz
import telebot
import yaml
from telebot import types

bot = telebot.TeleBot(os.environ["TG_BOT_TOKEN"], threaded=False)

# Define the right timezone for bot calculations
tz = pytz.timezone("Europe/Kiev")
now = datetime.datetime.now(tz)

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


# Handle "/start" and "/help" commands
@bot.message_handler(commands=["start"])
def send_welcome(message) -> None:
    bot.send_message(
        message.chat.id,
        f"Hi {get_username(message.from_user)}, here are the available commands👇",
        reply_markup=main_markup(),
    )


# Reply when's the next bus
@bot.message_handler(func=lambda message: message.text == button_next_bus)
def send_next_bus(message) -> None:
    bot.reply_to(message, f"You hit the {button_next_bus} button", reply_markup=main_markup())


# Reply with schedule for today or specified day
@bot.message_handler(func=lambda message: message.text == button_today_schedule)
@bot.message_handler(func=lambda message: message.text in [day for day in load_schedule()])
def send_day_schedule(message) -> None:
    day = get_weekday(now) if message.text == button_today_schedule else message.text
    schedule = format_schedule(day, get_schedule_for(day))
    bot.send_message(message.chat.id, schedule, parse_mode="HTML", reply_markup=main_markup())


# Reply with markup with all days from schedule
@bot.message_handler(func=lambda message: message.text == button_complete_schedule)
def send_welcome(message) -> None:
    bot.reply_to(message, f"Choose the day:", reply_markup=schedule_markup())


# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=["text"])
def send_re_ask(message) -> None:
    bot.reply_to(
        message,
        f"Sorry, {get_username(message.from_user)}, I don't understand you 🤔\nCheck the available buttons.",
        reply_markup=main_markup(),
    )


def build_markup(buttons: list) -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(row_width=1)
    for button in buttons:
        markup.add(types.KeyboardButton(button))
    return markup


def main_markup() -> types.ReplyKeyboardMarkup:
    return build_markup([button_next_bus, button_today_schedule, button_complete_schedule])


def schedule_markup() -> types.ReplyKeyboardMarkup:
    return build_markup([day for day in load_schedule()])


def get_username(from_user: types.User) -> str:
    return from_user.first_name or from_user.username


def load_schedule(path: str = "./schedule.yaml") -> dict:
    with open(path) as file:
        return yaml.safe_load(file)


def get_weekday(dt: datetime.datetime) -> str:
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
        schedule_list.append(f"\n{description}" if schedule_list else f"{description}")
        time_list.sort(key=lambda t: datetime.time.fromisoformat(t))
        schedule_list.append("\n".join(f"🔹<code>{t}</code>" for t in time_list))
    return "\n".join(schedule_list)
