import os
import logging

import django

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
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
from recipes.models import Recipe, IngredientAndRecipe

logging.basicConfig(
    filename='app.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

AGREEMENT = 1
NAME = 2
PHONE_NUMBER = 3
EMAIL = 4
NEXT = 5
LIKE, DISLIKE = 6, 7
END = ConversationHandler.END


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
        'Спасибо. Добро пожаловать в наше царство блюд=)) /menu'
    )
    return ConversationHandler.END


def menu(update: Update, context: CallbackContext) -> int:
    context.bot_data['next_id'] = 1
    user = update.message.from_user
    logger.info("Reciept of %s: %s", user.first_name, update.message.text)
    recipe = Recipe.objects.get(id=context.bot_data['next_id'])
    reply_keyboard = [['Следующее блюдо'], ['Показать рецепт'], ['Посмотреть ингридиенты'], ['Закрыть']]
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
    try:
        context.bot_data['next_id'] += 1
        user = update.message.from_user
        reply_keyboard = [['Следующее блюдо'], ['Показать рецепт'], ['Посмотреть ингридиенты'], ['Закрыть']]
        logger.info("Reciept of %s: %s", user.first_name, update.message.text)
        recipe = Recipe.objects.get(id=context.bot_data['next_id'])
        keyboard = [
            [
                InlineKeyboardButton(text='Нравится', callback_data=LIKE)
            ],
            [
                InlineKeyboardButton(text='Не нравится', callback_data=DISLIKE),
            ]
        ]
        update.message.reply_photo(
            recipe.img,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True,
                resize_keyboard=True,
            ),
        )
        update.message.reply_text(
            recipe.name,
            reply_markup=InlineKeyboardMarkup(
                keyboard, one_time_keyboard=True,
                resize_keyboard=True,
            )
        )
        return NEXT
    except Recipe.DoesNotExist:
        update.message.reply_text(
            'Блюд больше нет',
        )
        context.bot_data['next_id'] = 1
        return ConversationHandler.END


def send_recipe(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    reply_keyboard = [['Следующее блюдо'], ['Показать рецепт'], ['Посмотреть ингридиенты'], ['Закрыть']]
    logger.info("Reciept of %s: %s", user.first_name, update.message.text)
    recipe = Recipe.objects.get(id=context.bot_data['next_id'])
    update.message.reply_text(
        recipe.description,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
            resize_keyboard=True,
        )
    )

    return NEXT


def send_ingredients(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    reply_keyboard = [['Следующее блюдо'], ['Показать рецепт'], ['Посмотреть ингридиенты'], ['Закрыть']]
    logger.info("Reciept of %s: %s", user.first_name, update.message.text)
    recipe = Recipe.objects.get(id=context.bot_data['next_id'])
    ingredient_and_recipe = IngredientAndRecipe.objects.filter(recipe=recipe.pk)
    ingredient_message = ''
    for item in ingredient_and_recipe:
        ingredient_message += f'{item.ingredient.name}: {item.amount} {item.unit.name}\n'

    update.message.reply_text(
        ingredient_message,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
            resize_keyboard=True,
        )
    )

    return NEXT


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Очень жаль, что вы не с нами=(',
        reply_markup=ReplyKeyboardRemove()
    )

    return END


def run_bot():
    updater = Updater(token=TG_TOKEN, use_context=True)
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
                    Filters.regex('^Следующее блюдо$'),
                    next_menu
                ),
                MessageHandler(
                    Filters.regex('^Показать рецепт$'),
                    send_recipe
                ),
                MessageHandler(
                    Filters.regex('^Посмотреть ингридиенты$'),
                    send_ingredients
                ),
                MessageHandler(
                    Filters.regex('^Закрыть$'),
                    cancel
                ),
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(menu_handler)

    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    run_bot()
