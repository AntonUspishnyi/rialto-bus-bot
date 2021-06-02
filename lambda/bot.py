import logging
import os

import telebot
from telebot import types

bot = telebot.TeleBot(os.environ["TG_BOT_TOKEN"], threaded=False)

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
@bot.message_handler(commands=["start", "help"])
def send_welcome(message) -> None:
    bot.send_message(
        message.chat.id,
        f"Hi {get_username(message.from_user)}, here are the available commands:",
        reply_markup=main_markup(),
    )


@bot.message_handler(func=lambda message: message.text == button_next_bus)
def send_welcome(message) -> None:
    bot.reply_to(message, f"You hit the {button_next_bus} button", reply_markup=main_markup())


@bot.message_handler(func=lambda message: message.text == button_today_schedule)
def send_welcome(message) -> None:
    bot.reply_to(message, f"You hit the {button_today_schedule} button", reply_markup=main_markup())


@bot.message_handler(func=lambda message: message.text == button_complete_schedule)
def send_welcome(message) -> None:
    bot.reply_to(
        message, f"You hit the {button_complete_schedule} button", reply_markup=main_markup()
    )


# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=["text"])
def send_re_ask(message) -> None:
    bot.reply_to(
        message,
        f"Sorry, {get_username(message.from_user)}, I don't understand you. Here are the available commands:",
        reply_markup=main_markup(),
    )


def build_markup(buttons: list) -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(row_width=1)
    for button in buttons:
        markup.add(types.KeyboardButton(button))
    return markup


def main_markup() -> types.ReplyKeyboardMarkup:
    return build_markup([button_next_bus, button_today_schedule, button_complete_schedule])


def get_username(from_user: types.User) -> str:
    return from_user.first_name or from_user.username
