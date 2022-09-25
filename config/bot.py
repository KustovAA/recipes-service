import logging

from environs import Env
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# from recipes.models import Recipe


logging.basicConfig(
    filename='app.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

AGREEMENT, NAME, PHONE_NUMBER, EMAIL = range(4)
NEXT = range(2)


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
        'Спасибо. Добро пожаловать в наше царство блюд=)) Для продолжения нажми /menu'
    )
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Очень жаль, что вы не с нами=(',
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def menu(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Покажи другой рецепт']]
    photo = 'https://cdn.vkuso.ru/uploads/salat-appetit-s-syrom.jpg'
    update.message.reply_photo(
        photo,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )
    update.message.reply_text(
        'Булочка с кунжутом'
    )

    return NEXT


def next_menu(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    reply_keyboard = [['Покажи другой рецепт']]
    photo = 'https://cdn.vkuso.ru/uploads/klassicheskij-salat-cezar-s-kuricej-i-syrom-parmezan.jpg'
    logger.info("Reciept of %s: %s", user.first_name, update.message.text)
    update.message.reply_photo(
        photo,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )
    update.message.reply_text(
        'Пельмешки без спешки'
    )

    return NEXT


# def random_menu():
#     recipes = Recipe.objects.all()
    
def main() -> None:
    env = Env()
    env.read_env(override=True)
    updater = Updater(env.str("TG_TOKEN"))
    dispatcher = updater.dispatcher

    reg_handler = ConversationHandler(
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
    dispatcher.add_handler(reg_handler)

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


if __name__ == '__main__':
    main()
