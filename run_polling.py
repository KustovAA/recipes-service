import os
import logging

import django

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from config.settings import TG_TOKEN
from recipes.models import Recipe

logging.basicConfig(
    filename='app.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

AGREEMENT, NAME, PHONE_NUMBER, EMAIL = range(4)
NEXT, _ = range(2)


def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Согласен', 'Я против']]

    update.message.reply_text(
        'Привет, мы собираем личные данные',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
            resize_keyboard=True,
            input_field_placeholder='Нажми Согласен=))'
        ),
    )

    return AGREEMENT


def agreement(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Agreement of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Напишите вашу Фамилию Имя',
        reply_markup=ReplyKeyboardRemove(),
    )

    return NAME


def name(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Name of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Прекрасно. Теперь напишите ваш номер телефона'
    )

    return PHONE_NUMBER


def phone_number(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Phone number of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Отлично. И последнее, напишите ваш email'
    )

    return EMAIL


def email(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Email of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Спасибо. Добро пожаловать в наше царство блюд=))'
    )
    return ConversationHandler.END


next_id = 1


def menu(update: Update, context: CallbackContext) -> int:
    global next_id
    recipe = Recipe.objects.get(id=next_id)
    next_id += 1
    reply_keyboard = [['Покажи другой рецепт']]
    update.message.reply_photo(
        recipe.img,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )
    update.message.reply_text(recipe.name)

    return NEXT


def next_menu(update: Update, context: CallbackContext) -> int:
    global next_id
    user = update.message.from_user
    reply_keyboard = [['Покажи другой рецепт']]
    logger.info("Reciept of %s: %s", user.first_name, update.message.text)
    recipe = Recipe.objects.get(id=next_id)
    next_id += 1
    update.message.reply_photo(
        recipe.img,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )
    update.message.reply_text(recipe.name)

    return NEXT


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Очень жаль, что вы не с нами=(',
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def run_polling():
    updater = Updater(TG_TOKEN)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AGREEMENT: [
                MessageHandler(
                    Filters.regex('^Согласен$'),
                    agreement
                ),
                MessageHandler(
                    Filters.regex('^Я против$'),
                    cancel
                )
            ],
            NAME: [MessageHandler(Filters.text & ~Filters.command, name)],
            PHONE_NUMBER: [
                MessageHandler(Filters.text & ~Filters.command, phone_number)
            ],
            EMAIL: [MessageHandler(Filters.text & ~Filters.command, email)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(conv_handler)

    menu_handler = ConversationHandler(
        entry_points=[CommandHandler('menu', menu)],
        states={
            NEXT: [
                MessageHandler(
                    Filters.regex('^Покажи другой рецепт$'),
                    next_menu
                )
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(menu_handler)

    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    run_polling()
