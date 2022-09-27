import os
import sys
import logging
import random

import django
from retry import retry

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
from recipes.models import Recipe, IngredientAndRecipe, User

logging.basicConfig(
    stream=sys.stdout,
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
    reply_keyboard = [['Согласен', 'Не согласен']]

    update.message.reply_text(
        'Привет, мы собираем личные данные. Вы согласны на обработку вашей персональной информации?',
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
    telegram_id = update.effective_user.id
    first_name = update.effective_user.first_name
    last_name = update.effective_user.last_name
    User.objects.create(telegram_id=telegram_id, first_name=first_name, last_name=last_name)
    update.message.reply_text(
        'Пожалуйста, укажите ваше имя',
        reply_markup=ReplyKeyboardRemove(),
    )

    return NAME


def name(update: Update, context: CallbackContext) -> int:
    try:
        user = update.message.from_user
        if not user:
            raise ValueError('Invalid value')
        logger.info("Name of %s: %s", user.first_name, update.message.text)
        update.message.reply_text(
            'Прекрасно. Теперь напишите ваш номер телефона'
        )
    except ValueError:
        print('Вы не указали ваше имя.')

    return PHONE_NUMBER


def phone_number(update: Update, context: CallbackContext) -> int:
    try:
        user = update.message.from_user
        if not user:
            raise ValueError('Invalid value')
        logger.info("Phone number of %s: %s", user.first_name, update.message.text)
        update.message.reply_text(
            'Отлично. И последнее, напишите ваш email'
        )
    except ValueError:
        print('Похоже, что во введённом вами номере есть ошибка.')

    return EMAIL


def email(update: Update, context: CallbackContext) -> int:
    try:
        user = update.message.from_user
        if not user:
            raise ValueError('Invalid value')
        logger.info("Email of %s: %s", user.first_name, update.message.text)
        update.message.reply_text(
            'Спасибо. Добро пожаловать в наше царство блюд! =)) /menu'
        )
    except ValueError:
        print('Похоже, что во введённом вами адресе электронной почты есть ошибка.')

    return END


def menu(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Reciept of %s: %s", user.first_name, update.message.text)
    reply_keyboard = [['Начать']]
    update.message.reply_text(
        f'Привет {user.first_name}. Давай выберем что тебе стоит приготовить.',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )

    return NEXT


def next_menu(update: Update, context: CallbackContext) -> int:
    count = random.randint(0, Recipe.objects.count())
    context.bot_data['next_id'] = count

    try:
        user = update.message.from_user
        reply_keyboard = [
            ['Следующее блюдо'],
            ['Показать рецепт'],
            ['Посмотреть ингредиенты'],
            ['Закрыть']
        ]
        logger.info("Reciept of %s: %s", user.first_name, update.message.text)
        recipe = Recipe.objects.get(id=context.bot_data['next_id'])
        keyboard = [
            [
                InlineKeyboardButton(
                    text='Нравится',
                    callback_data=str(LIKE)
                )
            ],
            [
                InlineKeyboardButton(
                    text='Не нравится',
                    callback_data=str(DISLIKE)
                ),
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
        return END


def send_recipe(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    reply_keyboard = [
        ['Следующее блюдо'],
        ['Показать рецепт'],
        ['Посмотреть ингредиенты'],
        ['Закрыть']
    ]
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
    reply_keyboard = [
        ['Следующее блюдо'],
        ['Показать рецепт'],
        ['Посмотреть ингредиенты'],
        ['Закрыть']
    ]
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
        'Очень жаль, что вы не с нами! =(',
        reply_markup=ReplyKeyboardRemove()
    )

    return END


def like(update: Update, context: CallbackContext) -> int:
    telegram_id = update.effective_user.id
    db_user = User.objects.get(telegram_id=telegram_id)
    recipe_id = context.bot_data['next_id']
    recipe = Recipe.objects.get(id=recipe_id)
    db_user.likes.add(recipe)

    return NEXT


def dislike(update: Update, context: CallbackContext) -> int:
    telegram_id = update.effective_user.id
    db_user = User.objects.get(telegram_id=telegram_id)
    recipe_id = context.bot_data['next_id']
    recipe = Recipe.objects.get(id=recipe_id)
    db_user.dislikes.add(recipe)

    return NEXT


@retry(exceptions=Exception, delay=1, backoff=2, tries=10)
def run_bot():
    try:
        updater = Updater(token=TG_TOKEN)
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
                        Filters.regex('^Не согласен$'),
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
                        Filters.regex('^Начать$|^Следующее блюдо$'),
                        next_menu
                    ),
                    MessageHandler(
                        Filters.regex('^Показать рецепт$'),
                        send_recipe
                    ),
                    MessageHandler(
                        Filters.regex('^Посмотреть ингредиенты$'),
                        send_ingredients
                    ),
                    MessageHandler(
                        Filters.regex('^Закрыть$'),
                        cancel
                    ),
                    MessageHandler(
                        Filters.regex(('^Нравится')),
                        like
                    ),
                    MessageHandler(
                        Filters.regex(('^Не нравится')),
                        dislike
                    )
                ]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )
        dispatcher.add_handler(menu_handler)

        updater.start_polling()

        updater.idle()
    except Exception as error:
        logger.error(error)
        raise error


if __name__ == "__main__":
    run_bot()
